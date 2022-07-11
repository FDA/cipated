"""Functions to import/export datasets in Tabulated Experimental Data format

See authors, license and disclaimer at the top level directory of this project.

"""

import csv
import logging
from zipfile import ZIP_DEFLATED, ZipFile

import cipa
from cipa.core import EncapsulatedDataFileError
import cipa.cursors
import cipa.edfiles
import cipa.io
from cipa.properties import Property, Property_Type, propertiesDict
import cipa.protocols
import cipa.results
import copy
import io
import os
import pandas as pd

from cipa.cursors import Cursor, CursorResult, Cursor_Type
from cipa.devices import Device
from cipa.experiments import Experiment
from cipa.liquids import (
    Liquid, LiquidJunctionPotential, LJP_ReportedVoltage_Type)
from cipa.protocols import Concentration_Type, LiquidProtocol, VoltageProtocol
from cipa.results import (
    Cell, LeakMethod_Type, Patch_Type,
    ProtocolExecution, Results, Result, Result_Type)
from cipa.study import Study, StudyReport
from cipa.trial import Trial
from cipa.waveforms import Waveform, waveforms_to_df


class TED_GeneralInformation:
    def __init__(self):
        self.STUDYID = ''
        self.REPORT_TITLE = ''
        self.REPORT_VERSION = ''
        self.REPORT_DATE = ''
        self.REPORT_DESCRIPTION = ''
        self.DEVICE_ID = ''
        self.DEVICE_CODE = ''
        self.DEVICE_MODEL = ''
        self.DEVICE_SOFTWARE = ''


class TED_CellProperty:
    def __init__(self):
        self.EXPID = ''
        self.CELLID = ''
        self.PARAMCD = ''
        self.PARAM = ''
        self.VALUE = ''
        self.UNIT = ''


class TED_LiquidAddition:
    def __init__(self):
        self.EXPID = ''
        self.CELLID = ''
        self.STIME = ''
        self.LJP = float('nan')
        self.LJPU = ''
        self.LIQUID = ''
        self.CONC = float('nan')
        self.CONCU = ''
        self.CONCT = ''
        self.FIRST = 0
        self.LAST = 0
        self.CTLFL = ''
        self.SBFL = ''
        self.ANL = ''
        self.SRCXFN = ''
        self.NOTES = ''


class TED_CursorDefinition:
    def __init__(self):
        self.CURSOR = ''
        self.STIME = float('nan')
        self.STIMEU = ''
        self.ETIME = float('nan')
        self.ETIMEU = ''
        self.CURSORT = ''


class TED_ResultWide:
    def __init__(self):
        self.EXPID = ''
        self.CELLID = ''
        self.RESTYPE = ''
        self.LEAKMTH = ''
        self.ELTIME = float('nan')
        self.ELTIMEU = ''
        self.TRACENUM = 0
        # Cursor names and values will be appended separatelly
        self.ANLFL = ''
        self.SRCXFN = ''
        # Liquid information (not needed for TED, but useful in general)
        self.LIQUID = ''
        self.CONC = float('nan')
        self.CONCU = ''
        self.CONCT = ''


def expand_numbers_list(numbers_string: str):
    if numbers_string is not None and numbers_string.replace(" ", "") != '':
        row = numbers_string.split(';')
        tmp = []
        row = [trace.split('-') for trace in row]
        new_row = []
        for item in row:
            if (len(item) == 2) and (int(item[0]) <= int(item[1])):
                [new_row.append(str(anl))
                 for anl in range(int(item[0]), int(item[1]) + 1)]
            elif len(item) == 1:
                new_row.append(str(item[0]))
            else:
                logger = logging.getLogger(__name__)
                logger.error(
                    f"expand_numbers_list: {item[0]} to {item[1]} "
                    f"are out of range")
        return new_row
    else:
        return []


def voltage_command_dataframe(trial: cipa.trial.Trial):
    ivp = pd.DataFrame()
    for p in trial.protocols:
        if p.type == cipa.protocols.Protocol_Type.CIPA_PROTOCOL_VOLTAGE:
            ivp = p.waveform.timeseries_to_df(True)
            break

    ivp_df = pd.DataFrame(data=ivp).drop_duplicates()

    return ivp_df


def cells_cursors_liquids_results_dataframes(trial: cipa.trial.Trial):
    """Generate CellProperties, LiquidAdditions, CursorDefinitions and ResultsWide tables

    Generate CellProperties, LiquidAdditions, CursorDefinitions and ResultsWide
    tables as pd.DataFrame from a cipa.trial.Trial object

    Args:
        trial (cipa.trial.Trial): CiPA trial or assay object

    Returns:
        Dict: dictionary with CellProperties, LiquidAdditions,
            CursorDefinitions and ResultsWide dataframes
    """
    cell_props = []
    cursors_defs = []
    liquid_adds = []
    res_wide = []
    for exp in trial.experiments:
        la = TED_LiquidAddition()
        if exp.id.extension == '':
            la.EXPID = exp.id.root
        else:
            la.EXPID = '_'.join([exp.id.root, exp.id.extension])
        la.STIME = exp.startTime
        # When exporting to TED format, only the first set of results is
        # exported
        rs = exp.resultsSet[0]
        if rs.cursors is not None:
            for c in rs.cursors:
                cdef = TED_CursorDefinition()
                cdef.CURSOR = c.name
                cdef.STIME = float(c.start)
                cdef.STIMEU = c.time_u
                cdef.ETIME = float(c.end)
                cdef.ETIMEU = c.time_u
                cdef.CURSORT = c.type.name
                cursors_defs += [cdef.__dict__]
        if rs.cell.id.extension == '':
            la.CELLID = rs.cell.id.root
        else:
            la.CELLID = '_'.join([rs.cell.id.root, rs.cell.id.extension])

        if rs.ljp is not None:
            la.LJP = rs.ljp.value
            la.LJPU = rs.ljp.unit
        else:
            la.LJP = trial.ljp.value
            la.LJPU = trial.ljp.unit
        # Liquid addition protocols executed
        exec_ps = []
        for p in exp.protocols:
            if p.protocol.type ==\
                    cipa.protocols.Protocol_Type.CIPA_PROTOCOL_LIQUID:
                ctlfl = ''
                if p.protocol.isControl:
                    ctlfl = 'Y'
                sbfl = ''
                if p.protocol.isSelectiveBlocker:
                    sbfl = 'Y'
                exec_ps += [{
                    'LIQUID': p.protocol.liquid.name,
                    'CONC': p.protocol.conc,
                    'CONCU': p.protocol.conc_u,
                    'CONCT': p.protocol.conc_type.name.split('_')[-1],
                    'TIME': float(p.time),
                    'TIMEU': p.time_u,
                    'CTLFL': ctlfl,
                    'SBFL': sbfl
                }]
        exp_las = pd.DataFrame(exec_ps).sort_values(
            ['TIME'], ignore_index=True).drop_duplicates(ignore_index=True)
        # Expermient results in wide layout
        exp_res_wide = []
        # When exporting to TED format, only the first set of results is
        # exported
        for res in exp.resultsSet[0].results:
            # Map liquid additions to recorded current traces
            if res.type == cipa.results.Result_Type.CIPA_RESULT_TYPE_CURRENT:
                rw = TED_ResultWide()
                rw.EXPID = la.EXPID
                rw.CELLID = la.CELLID
                rw.RESTYPE = res.type.name
                rw.LEAKMTH = rs.leakMethod.name  # LM is stored in resultsSet
                rw.ELTIME = float(res.elapsedTime)
                rw.ELTIMEU = res.elapsedTime_u
                rw.TRACENUM = int(res.traceNumber)
                rw.SRCXFN = res.waveform.edfilename
                if res.valid:
                    rw.ANLFL = 'Y'
                rww = rw.__dict__
                for rc in res.cursors:
                    rww[rc.name] = rc.result.value
                exp_res_wide += [rww]

        for p in exp.resultsSet[0].cell.properties:
            cp = TED_CellProperty()
            cp.EXPID = la.EXPID
            cp.CELLID = la.CELLID
            cp.PARAMCD = p.code
            cp.PARAM = p.displayName
            cp.VALUE = p.value
            cp.UNIT = p.unit
            cell_props += [cp.__dict__]

        # Update the experiment liquids addition table with tracenumbers
        tmp = pd.DataFrame(exp_res_wide).sort_values(
            ["EXPID", "CELLID", "ELTIME", "TRACENUM"], ignore_index=True)
        exp_liq_adds = []
        for exp_la in exp_las.itertuples():
            la.LIQUID = exp_la.LIQUID
            la.CONC = exp_la.CONC
            la.CONCU = exp_la.CONCU
            la.CONCT = exp_la.CONCT
            la.CTLFL = exp_la.CTLFL
            la.SBFL = exp_la.SBFL
            # Current liquid addition traces
            tmp_c = tmp[tmp["ELTIME"] >= exp_la.TIME]
            la.FIRST = tmp_c.iloc[0]["TRACENUM"]
            if len(exp_liq_adds) > 0:
                tmp_c = tmp[tmp["ELTIME"] < exp_la.TIME]
                exp_liq_adds[-1].LAST = tmp_c.iloc[-1]["TRACENUM"]
            exp_liq_adds.append(copy.copy(la))
        # Populate last liquid addition LAST with last tracenumber recorded
        exp_liq_adds[-1].LAST = tmp.iloc[-1]["TRACENUM"]
        # Populate analysis traces and SRCXFN files
        for exp_la in exp_liq_adds:
            validtraces = tmp[
                (tmp["ANLFL"] == "Y") &
                (tmp["TRACENUM"] >= exp_la.FIRST) &
                (tmp["TRACENUM"] <= exp_la.LAST)
                ]["TRACENUM"].drop_duplicates().map(str).values
            exp_la.ANL = ";".join(validtraces)
            singalfiles = tmp[
                (tmp["TRACENUM"] >= exp_la.FIRST) &
                (tmp["TRACENUM"] <= exp_la.LAST)
                ]["SRCXFN"].drop_duplicates().values
            exp_la.SRCXFN = ";".join(singalfiles)
            # Add liquid information to exp_res_wide as well
            for er in exp_res_wide:
                if (er["EXPID"] == exp_la.EXPID) and\
                     (er["CELLID"] == exp_la.CELLID) and\
                     (er["TRACENUM"] >= exp_la.FIRST) and\
                     (er["TRACENUM"] <= exp_la.LAST):
                    er["LIQUID"] = exp_la.LIQUID
                    er["CONC"] = exp_la.CONC
                    er["CONCU"] = exp_la.CONCU
                    er["CONCT"] = exp_la.CONCT
                    er["CTLFL"] = exp_la.CTLFL
                    er["SBFL"] = exp_la.SBFL
        [liquid_adds.append(xla.__dict__) for xla in exp_liq_adds]

        res_wide += exp_res_wide

    if len(cell_props) == 0:
        cell_props_df = pd.DataFrame(
            columns=TED_CellProperty().__dict__.keys())
    else:
        cell_props_df = pd.DataFrame(data=cell_props)

    cursors_defs_df = pd.DataFrame(data=cursors_defs).drop_duplicates()

    la_df = pd.DataFrame(data=liquid_adds).sort_values(
            ["STIME", "EXPID", "CELLID", "FIRST", "LAST"], ignore_index=True)

    rw_df = pd.DataFrame(
        data=res_wide).drop(
            columns=["SRCXFN"]).drop_duplicates().sort_values(
            ["EXPID", "CELLID", "ELTIME", "TRACENUM"], ignore_index=True)

    dataframes = {
        "CellProperties": cell_props_df,
        "CursorsDefinitions": cursors_defs_df,
        "LiquidAdditions": la_df,
        "ResultsWide": rw_df
        }

    return dataframes


def to_xlsx(
        trial: cipa.trial.Trial,
        ted_xlsx_filename: str = "ted.xlsx",
        edformat: str = "csv"):
    """Save a cipa.trial.Trial object as TED dataset

    Args:
        trial (cipa.trial.Trial): CiPA trial or assay object.
        ted_xlsx_filename (str): TED filename
        edformat (str): format for the encapsulated data files storing the
            waveforms. Supported formats include '.csv', '.zip' and '.xlsx'

    Returns:
        None.
    """

    # General Information
    gi = TED_GeneralInformation()
    gi.STUDYID = trial.study.studyId
    gi.REPORT_TITLE = trial.study.report.title
    gi.REPORT_VERSION = trial.study.report.version
    gi.REPORT_DATE = trial.study.report.date
    gi.REPORT_DESCRIPTION = trial.study.report.text
    gi.DEVICE_ID = trial.devices[0].id.root + trial.devices[0].id.extension
    gi.DEVICE_CODE = trial.devices[0].code
    gi.DEVICE_MODEL = trial.devices[0].manufacturerModelName
    gi.DEVICE_SOFTWARE = trial.devices[0].deviceSoftwareName

    gi_df = pd.DataFrame(data=[gi.__dict__]).transpose()

    # Inteded Voltage Protocol
    ivp_df = voltage_command_dataframe(trial)
    # Get dataframes for cell properties, default cursors, liquid additions
    # and results
    dfs = cells_cursors_liquids_results_dataframes(trial)
    cell_props_df = dfs["CellProperties"]
    cursors_defs_df = dfs["CursorsDefinitions"]
    la_df = dfs["LiquidAdditions"]
    rw_df = dfs["ResultsWide"]

    # Waveform files
    teddir = os.path.dirname(ted_xlsx_filename)
    if edformat == "csv":
        for exp in trial.experiments:
            if exp.id.extension == '':
                expid = exp.id.root
            else:
                expid = '_'.join([exp.id.root, exp.id.extension])
            # When exporting to TED format, only the first set of results is
            # exported
            rs = exp.resultsSet[0]
            if rs.cell.id.extension == '':
                sheetname = rs.cell.id.root
            else:
                sheetname = '_'.join([rs.cell.id.root, rs.cell.id.extension])
            csvfn = '.'.join([sheetname, 'csv'])
            edf = cipa.edfiles.EDCsvFile(csvfn, teddir)
            la_df.loc[
                (la_df["EXPID"] == expid) & (la_df["CELLID"] == sheetname),
                "SRCXFN"] = csvfn
            print(
                f"Exporting waveforms to "
                f"{os.path.join(edf.ted_dataset_path, edf.edfilename)}")
            edf.save_waveforms([r.waveform for r in rs.results])
    elif edformat == "zip":
        for exp in trial.experiments:
            if exp.id.extension == '':
                expid = exp.id.root
            else:
                expid = '_'.join([exp.id.root, exp.id.extension])
            # When exporting to TED format, only the first set of results is
            # exported
            rs = exp.resultsSet[0]
            if rs.cell.id.extension == '':
                sheetname = rs.cell.id.root
            else:
                sheetname = '_'.join([rs.cell.id.root, rs.cell.id.extension])
            csvfn = '.'.join([sheetname, 'csv', 'zip'])
            edf = cipa.edfiles.EDCsvFile(csvfn, teddir, compression='zip')
            la_df.loc[
                (la_df["EXPID"] == expid) & (la_df["CELLID"] == sheetname),
                "SRCXFN"] = f"{csvfn}:{csvfn[:-4]}"
            print(
                f"Exporting waveforms to "
                f"{os.path.join(edf.ted_dataset_path, edf.edfilename)}")
            edf.save_waveforms([r.waveform for r in rs.results])
    elif edformat == "xlsx":
        edfn = 'waveforms.xlsx'
        edf2 = cipa.edfiles.EDXlsxFile(edfn, teddir)
        with pd.ExcelWriter(
                os.path.join(edf2.ted_dataset_path, edf2.edfilename),
                mode='w', engine='openpyxl') as xlsxwriter:
            for exp in trial.experiments:
                if exp.id.extension == '':
                    expid = exp.id.root
                else:
                    expid = '_'.join([exp.id.root, exp.id.extension])
                # When exporting to TED format, only the first set of results
                # is exported
                rs = exp.resultsSet[0]
                if rs.cell.id.extension == '':
                    sheetname = rs.cell.id.root
                else:
                    sheetname = '_'.join(
                        [rs.cell.id.root, rs.cell.id.extension])
                la_df.loc[
                    (la_df["EXPID"] == expid) & (la_df["CELLID"] == sheetname),
                    "SRCXFN"] = f"{edfn}:{sheetname}"
                print(
                    f"Exporting waveforms to "
                    f"{os.path.join(edf2.ted_dataset_path, edf2.edfilename)}"
                    f":{sheetname}")
                edf2.save_waveforms(
                    [r.waveform for r in rs.results], sheetname, xlsxwriter)
    else:
        raise EncapsulatedDataFileError(
            edformat,
            "Unsopported file format for encapsulated data")

    # Summary xlsx book
    with pd.ExcelWriter(ted_xlsx_filename) as writer:
        gi_df.to_excel(
            writer,
            sheet_name='GeneralInformation',
            header=False)
        cell_props_df.to_excel(
            writer,
            sheet_name='CellProperties',
            index=False)
        la_df.to_excel(
            writer,
            sheet_name='LiquidAdditions',
            index=False)
        cursors_defs_df.to_excel(
            writer,
            sheet_name='CursorsDefinitions',
            index=False)
        ivp_df.to_excel(
            writer,
            sheet_name='IntendedVoltageProtocol',
            index=False)
        rw_df.to_excel(
            writer,
            sheet_name='ResultsWide',
            index=False)


def from_xlsx(
        ted_directory: str = '.',
        ted_file: str = 'ted.xlsx'
        ) -> Trial:
    """Load a cipa.trial.Trial object from a TED dataset

    Args:
        ted_directory (str): directory containing the TED dataset (e.g., TED
            index file and encapsulated data files with waveforms)
        ted_file (str): index TED file. Defaults to ted.xlsx

    Returns:
        cipa.trial.Trial
    """

    logger = logging.getLogger(__name__)

    trial = Trial(
        version=cipa.__version__,
        description="COD dataset imported from TED files"
    )

    # Helper variables ------------------------------------------------------
    conctypes = {
        "NOMINAL": Concentration_Type.
        CIPA_PROTOCOL_LIQUID_CONCENTRATION_NOMINAL,
        "MEASURED": Concentration_Type.
        CIPA_PROTOCOL_LIQUID_CONCENTRATION_MEASURED
        }
    cursortypes = {
        "AVERAGE": Cursor_Type.AVERAGE,
        "MAXIMUM": Cursor_Type.MAXIMUM,
        "MINIMUM": Cursor_Type.MINIMUM,
        "CUSTOM": Cursor_Type.CUSTOM
        }

    # GeneralInformation: Study, report and device info -----------------------
    ted_fn = os.path.join(ted_directory, ted_file)
    gi = pd.read_excel(
        ted_fn, sheet_name="GeneralInformation",
        names=["PARAMCD", "VALUE"], header=None, na_filter=False)
    trial.study = Study(
        gi[gi["PARAMCD"] == "STUDYID"]["VALUE"].map(str).iloc[0]
    )

    trial.study.report = StudyReport(
        gi[gi["PARAMCD"] == "REPORT_TITLE"]["VALUE"].map(str).iloc[0],
        gi[gi["PARAMCD"] == "REPORT_VERSION"]["VALUE"].map(str).iloc[0],
        gi[gi["PARAMCD"] == "REPORT_DATE"]["VALUE"].map(str).iloc[0],
        gi[gi["PARAMCD"] == "REPORT_DESCRIPTION"]["VALUE"].map(str).iloc[0]
    )

    trial.devices = [
        Device(
            cipa.Id(
                gi[gi["PARAMCD"] == "DEVICE_ID"]["VALUE"].map(str).iloc[0]
                ),
            gi[gi["PARAMCD"] == "DEVICE_CODE"]["VALUE"].map(str).iloc[0],
            gi[gi["PARAMCD"] == "DEVICE_MODEL"]["VALUE"].map(str).iloc[0],
            gi[gi["PARAMCD"] == "DEVICE_SOFTWARE"]["VALUE"].map(str).iloc[0]
            )
        ]

    # CellProperties: "other" results reported in the cell properties sheet ---
    cp = pd.read_excel(ted_fn, sheet_name="CellProperties",
                       dtype={
                           'EXPID': str, 'CELLID': str, 'PARAMCD': str,
                           'PARAM': str, 'VALUE': str, 'UNIT': str},
                       na_filter=False)

    # LiquidAdditions -------------------------------------------------------
    #  liquids, liquids protocols, liquid junction potential, experiment IDs,
    #  cell IDs, and other data
    la = pd.read_excel(ted_fn, sheet_name="LiquidAdditions",
                       dtype={'EXPID': str, 'CELLID': str, 'STIME': str},
                       na_filter=False)

    la["CTLFL"] = la["CTLFL"].map(str).replace('nan', '').str.upper()
    la["SBFL"] = la["SBFL"].map(str).replace('nan', '').str.upper()

    # Adding liquid juntion potential.
    # Assuming each TED file contains 1 unique LJP value
    ljp = float('nan')
    if la["LJP"][0] != "":
        ljp = la["LJP"][0]
    trial.ljp = LiquidJunctionPotential(
        ljp,
        la["LJPU"][0],
        LJP_ReportedVoltage_Type.Vclamp
    )

    # Let's add the voltage protocol first
    # To add the voltage protocol, we also need to read the intended voltage
    # command
    vc = pd.read_excel(
        ted_fn, sheet_name="IntendedVoltageProtocol", na_filter=False)
    t_units = str.split(vc.columns[0], "_")[-1]
    v_units = str.split(vc.columns[1], "_")[-1]
    vcwf = Waveform()
    vcwf.head["value"] = 0.0
    vcwf.head["unit"] = t_units
    vcwf.increment["value"] = vc.iloc[1, 0] - vc.iloc[0, 0]
    vcwf.increment["unit"] = t_units
    vcwf.origin["value"] = 0.0
    vcwf.origin["unit"] = v_units
    vcwf.scale["value"] = 1.0
    vcwf.scale["unit"] = v_units
    vcwf.cipaType = "CIPA_PROTOCOL_VOLTAGE"
    vcwf.tracenum = -1
    vcwf.signalnam = "voltage"
    vcwf.displayName = "Step ramp voltage protocol for hERG"
    vcwf.sequenceType = "CIPA_TRACE_RECONSTRUTED"
    vcwf.digits = vc.iloc[:, 1].values

    voltage_command_protocol = VoltageProtocol(
        cipa.Id("PV-10001"),
        vcwf,
        "Intended voltage command",
        duration=5,  # TODO: This can be computed from resultsWide sheet
        duration_u='s'
        )
    trial.protocols += [voltage_command_protocol]

    # Let's add the liquid protocols next

    # Liquids
    liquids_df = la[["LIQUID"]].drop_duplicates(ignore_index=True)
    liquids_df["idx"] = liquids_df.index
    liquids_df["cipa_liquid"] = liquids_df.apply(
        lambda x: Liquid(cipa.Id(f"L-{x.idx}"), x.LIQUID), axis=1)
    liquids_df.drop(columns=["idx"])
    for liquid in liquids_df.itertuples():
        trial.liquids += [
            liquid.cipa_liquid
        ]

    liquid_ps = la[
        ["LIQUID", "CONC", "CONCU", "CONCT", "CTLFL", "SBFL"]
        ].drop_duplicates(ignore_index=True)

    liquid_ps = liquid_ps.merge(
        liquids_df, on=["LIQUID"], how="left").reset_index(drop=True)
    liquid_ps["idx"] = liquid_ps.index
    liquid_ps["cipa_lp"] = liquid_ps.apply(
        lambda x: LiquidProtocol(
                cipa.Id(f"P-{x.idx}_{x.cipa_liquid.id.root}"),
                x.cipa_liquid,
                f"{x.LIQUID} {x.CONC} {x.CONCU}",
                conc_type=conctypes[x.CONCT.upper()],
                conc=x.CONC,
                conc_u=x.CONCU,
                isControl=(x.CTLFL.upper() == "Y"),
                isSelectiveBlocker=(x.SBFL.upper() == "Y")
            ), axis=1)
    liquid_ps.drop(columns=["idx"])

    # Add liquid protocols to la dataframe
    la = la.merge(
            liquid_ps,
            on=[
                "LIQUID", "CONC", "CONCU",
                "CONCT", "CTLFL", "SBFL"],
            how="left")

    for liquid in liquid_ps.itertuples():
        trial.protocols += [liquid.cipa_lp]

    # Experiments ------------------------------------------------------------
    # Experiments, protocol executions (protocols) and results (waveforms and
    # cursors).
    cd = pd.read_excel(
        ted_fn, sheet_name="CursorsDefinitions", na_filter=False)
    rsCursors = []
    for c in cd.itertuples():
        rsCursors += [
            Cursor(
                c.CURSOR,
                c.STIME,
                c.ETIME,
                c.STIMEU,
                cursortypes[c.CURSORT.upper()]
            )
        ]
    rw = pd.read_excel(ted_fn, sheet_name="ResultsWide",
                       dtype={'EXPID': str, 'CELLID': str}, na_filter=False)
    # Remove 'Unnamed' columns potentially appearing due to formula in TED
    # template and that causes extra columns with empty header to be identified
    # by pd.read_excel
    rw = rw.loc[:, ~rw.columns.str.contains('^Unnamed')]
    experiments = la[
        ["EXPID", "CELLID", "STIME"]].drop_duplicates(ignore_index=True)

    for experiment in experiments.itertuples():
        exp = Experiment(
            cipa.Id(experiment.EXPID, experiment.CELLID),
            device=trial.devices[0].id,
            startTime=str(experiment.STIME))
        expres = rw[
            (rw["EXPID"] == experiment.EXPID) &
            (rw["CELLID"] == experiment.CELLID)]

        # Execution of liquid additions and voltage protocols
        # Add the liquid addition protocols that were executed
        expres = expres.merge(
            la[
                ["EXPID", "CELLID", "FIRST", "cipa_lp"]
                ].rename(columns={"FIRST": "TRACENUM"}),
            on=["EXPID", "CELLID", "TRACENUM"],
            how="left")

        # Create the resultsSet of the experiment
        lm = expres["LEAKMTH"].drop_duplicates().values
        if len(lm) > 1:
            logger.warning(
                f"ted_to_cod: {len(lm)} leak methods found for "
                f"experiment {experiment.EXPID} but only 1 method is "
                f"supported by this tool version. Using {lm[0]} as default "
                f"for all results.")
            lm = LeakMethod_Type[lm[0]]
        elif len(lm) == 0:
            logger.warning(
                f"ted_to_cod: {len(lm)} leak method not found for "
                f"experiment {experiment.EXPID}. Assuming "
                f"CIPA_LEAK_METHOD_NONE as default for all results.")
            lm = LeakMethod_Type.CIPA_LEAK_METHOD_NONE
        else:
            lm = LeakMethod_Type[lm[0]]

        # generate cell properties
        cell_p = cp[
            (cp["EXPID"] == experiment.EXPID) &
            (cp["CELLID"] == experiment.CELLID)]
        cp_node = []
        if len(cell_p) > 0:
            for p in cell_p.itertuples():
                if p.PARAMCD in propertiesDict.keys():
                    proptype = propertiesDict[p.PARAMCD]
                else:
                    proptype = Property_Type.CIPA_PROPERTY_UNKNOWN
                cprop = Property(
                    p.PARAMCD,
                    p.PARAM,
                    proptype,
                    p.VALUE,
                    p.UNIT)
                cp_node += [cprop]
        exp.resultsSet = [Results(
            Cell(cipa.Id(experiment.CELLID), cp_node),
            Patch_Type.CIPA_CELL_SINGLE,
            "Patch clamp rig", "well",
            lm,
            None,  # Assuming the same LJP for all results
            rsCursors,
            []
            )]
        waveformdata_from_file = {
            "filename": "",
            "data": None,
            "t_increase_ms": 0
        }

        for res in expres.itertuples():
            if not pd.isnull(res.cipa_lp):
                # Liquid addition executed
                pe = ProtocolExecution(
                    res.cipa_lp,
                    res.ELTIME,
                    res.ELTIMEU
                )
                if exp.protocols is not None:
                    exp.protocols += [pe]
                else:
                    exp.protocols = [pe]
            # Add also the voltage command protocols executed at each trace
            pe = ProtocolExecution(
                voltage_command_protocol,
                res.ELTIME,
                res.ELTIMEU
                )
            if exp.protocols is not None:
                exp.protocols += [pe]
            else:
                exp.protocols = [pe]

            # Create the result with trace and cursor values
            # VALID flag
            la_row = la[
                (la["EXPID"] == res.EXPID) &
                (la["CELLID"] == experiment.CELLID) &
                (la["FIRST"] <= res.TRACENUM) &
                (la["LAST"] >= res.TRACENUM)
                ]
            if la_row.shape[0] == 1:
                valid_traces = [
                    int(n)
                    for n in expand_numbers_list(la_row["ANL"].values[0])]
                validfl = res.TRACENUM in valid_traces
                cwf = []  # List of cursor values
                for cn in cd["CURSOR"].values:
                    if (cn in expres.columns):
                        cr = Cursor(cn)
                        # TED format does not include units for cursors,
                        # so units are hardcoded here assuming pA
                        cr.result = CursorResult(
                            res[[v for v in expres.columns].index(cn) + 1],
                            'pA'
                        )
                        cwf += [cr]
                time_units = 'ms'
                time_head = 0
                # Waveform read from file
                if (waveformdata_from_file["filename"] == "") or\
                        (waveformdata_from_file["filename"] !=
                            la_row["SRCXFN"].values[0]):
                    waveformdata_from_file["filename"] =\
                        la_row["SRCXFN"].values[0]
                    # Check SRCXFN extension and load the waveforms
                    if waveformdata_from_file[
                            "filename"][-4:].lower() == '.csv':
                        # Check if csv file is compressed in a zip file
                        parts = waveformdata_from_file[
                            "filename"].split(":")
                        if len(parts) == 1:
                            waveformdata_from_file["data"] = pd.read_csv(
                                os.path.join(
                                    ted_directory,
                                    la_row["SRCXFN"].values[0]))
                        elif parts[0][-4:].lower() == '.zip':
                            with ZipFile(os.path.join(
                                    ted_directory, parts[0])) as container:
                                waveformdata_from_file["data"] = pd.read_csv(
                                    io.BytesIO(container.read(parts[1])))
                        else:
                            print(
                                f"Unsupported format for "
                                f"{waveformdata_from_file['filename']}")
                    elif waveformdata_from_file[
                            "filename"][-5:].lower() == ".xlsx":
                        waveformdata_from_file["data"] = pd.read_excel(
                            os.path.join(
                                ted_directory, la_row["SRCXFN"].values[0]))
                    time_units = waveformdata_from_file[
                        "data"].columns[0].split("_")[-1].lower()
                    time_head = waveformdata_from_file["data"].iloc[0, 0]
                    time_step = waveformdata_from_file["data"].iloc[1, 0] -\
                        waveformdata_from_file["data"].iloc[0, 0]
                    if time_units == 's':
                        time_head = time_head * 1e3
                        time_step = time_step * 1e3
                    elif time_units == 'ms':
                        pass
                    elif time_units == 'us':
                        time_head = time_head * 1e-3
                        time_step = time_step * 1e-3
                    else:
                        # time units unknown, set to ms and infer
                        # scale from step size
                        time_units = 'ms'
                        if time_step < 0.001:
                            # Values are likely in seconds
                            time_head = time_head * 1e-3
                            time_step = time_step * 1e3
                    waveformdata_from_file["t_increase_ms"] = time_step

                colbase = f"Trace_#{res.TRACENUM}_"
                colnamesmatched = list(filter(
                    lambda x: colbase.lower() in x.lower(), [
                        v for v in waveformdata_from_file["data"].columns]
                    ))
                for colname in colnamesmatched:
                    colparts = str.split(colname, "_")
                    colunits = colparts[-1].replace("'", "")
                    coltype = colparts[-2]
                    cipaType = "CIPA_RESULT_TYPE_UNKNOWN"
                    if coltype.upper() == 'CURRENT':
                        cipaType = "CIPA_RESULT_TYPE_CURRENT"
                    elif coltype.upper() == 'VOLTAGE':
                        cipaType = "CIPA_RESULT_TYPE_VOLTAGE"
                    elif coltype.upper() == 'TEMPERATURE':
                        cipaType = "CIPA_RESULT_TYPE_TEMPERATURE"
                    if cipaType == res.RESTYPE:
                        wf = Waveform()
                        wf.cipaType = res.RESTYPE
                        wf.increment["value"] = waveformdata_from_file[
                            "t_increase_ms"]
                        wf.increment["unit"] = "ms"
                        wf.head["value"] = time_head
                        wf.head["unit"] = "ms"
                        wf.origin["value"] = 0
                        wf.origin["unit"] = colunits
                        wf.scale["value"] = 1
                        wf.scale["unit"] = colunits
                        wf.digits = waveformdata_from_file[
                            "data"][colname].values
                        wf.sequenceType = "CIPA_TRACE_RECORDED"
                        # Current name is not specified in the TED format.
                        wf.displayName = coltype
                        wf.tracenum = res.TRACENUM
                        wf.signalnam = coltype
                        result = Result(
                            res.TRACENUM,
                            validfl,
                            Result_Type[res.RESTYPE],
                            res.ELTIME, res.ELTIMEU,
                            wf,
                            cwf
                        )
                        # TED format files only include 1 resultsSet.
                        exp.resultsSet[0].results += [result]

        trial.experiments += [exp]

    return trial
