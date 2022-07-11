from typing import List

import logging
import numpy as np
import os
import pandas as pd


# Python logging --------------------------------------------------------------
logger = logging.getLogger(__name__)


# Waveform class and helper functions -----------------------------------------
class Waveform:
    """
    Waveform recorded as timeseries of values.

    Attributes:

        head (Dict): Starting time (value and units).
        increment (Dict): Sampling period (value and units).
        origin (Dict): offset  (value and units).
        scale (Dict): scale factor (value and units).
        digits List[float]: List of sampled/recorded values. The scale factor
            and offset are applied to convert the digits values into true
            physical quantities.
        cipaType (str): Type of the signal encoded using CIPA controlled
            vocabulary (e.g., CIPA_RESULT_TYPE_VOLTAGE,
            CIPA_RESULT_TYPE_CURRENT)
        sequenceType (str): whether the values in the sequence were
            reconstructed (e.g., the values of the intended voltage protocol
            programmed in the device) or recorded (e.g., the values of a
            current recorded by the device). Allowed types are
            CIPA_TRACE_RECONSTRUTED or CIPA_TRACE_RECORDED.
        displayName (str): Display name for reports and figures.
        tracenum (int): Trace number
        signalnam (str): Signal name (e.g., voltage, current)
        edfilename (str): Filename containing the encapsulated data if values
            were not embedded in the XML.
        otherInfo (Dict): Dictionary to store additional information
        itemoffset (int): offset of the item in the encapsulated
                data file (traceNumber-1)*length of sweep*
                sampling frequency*itemsize*number of signals recorded.
                Defaults to 0. Ignored if digits are not included in a bin file
        recordsize (int): Size of each record in the encapsulated
                data file, in bytes for  files, in columns (0 based) for csv
                files. Defaults to 2. Ignored if digits are not included in a
                bin or csv file
        itemsize (int): Number of bytes per sample (e.g., 4 bytes for
                CIPA_CTL_VBL_IEEE754_BIN32 [i.e., IEEE 754 bin32]).  gnored if
                digits are not included in a bin file
        numrows (int): Number of rows to read from csv file. Default to -1 (all
                rows). Ignored if digits are not included in csv file
        itemcol (int): Number of column where the waveform is stored in a csv
                file. Defaults to 0 (i.e., first column). Ignored if digits are
                not included in csv file
        headersize (int): Number of rows of the header and to skip when reading
                the waveform from a csv file. Defaults to 0. Ignored if digits
                are not included in csv file
    """

    def __init__(self):
        self.head = {"value": 0.0, "unit": "s"}
        self.increment = {"value": 0.0, "unit": "s"}
        self.origin = {"value": 0.0, "unit": ""}
        self.scale = {"value": 0.0, "unit": ""}
        self.digits = []
        self.cipaType = ""
        self.sequenceType = ""
        self.displayName = ""
        self.tracenum = -1
        self.signalnam = ""
        self.edfilename = ''
        self.otherInfo = {}
        self.itemoffset = 0
        self.recordsize = 0
        self.itemsize = 0
        self.numrows = -1
        self.itemcol = 0
        self.headersize = 0

    def timeseries_to_df(self, includetime: bool = False) -> pd.DataFrame:
        """Generates a dataframe with the waveform's time series of values

        Args:
            includetime (bool, optional): indicates if a column with the time
                values should be included. Defaults to False.

        Returns:
            pd.Dataframe: Dataframe with the waveform's time series of values.
        """

        scale = float(self.scale['value'])
        origin = float(self.origin['value'])

        if self.scale["unit"] != self.origin["unit"]:
            logger.warning(
                f"Warning: signal's scale unit is {self.scale['unit']}"
                f" but origin unit is {self.origin['unit']}.")

        signam = self.signalnam
        if signam == '':
            signam = self.cipaType.split("_")[-1].lower()
        signal_colname = "trace_#" + str(self.tracenum) + "_" + \
            signam + "_" + self.scale["unit"]
        digits = []
        if len(self.digits) == 0:
            self.digits_from_file()
        if len(self.digits) > 0:
            digits = [float(d) * scale + origin for d in self.digits]
        wf_df = pd.DataFrame({
            signal_colname: digits})
        if includetime:
            num_samples = len(self.digits)

            time_values = np.linspace(0.0,
                                      (num_samples - 1) *
                                      self.increment["value"],
                                      num_samples)
            time_colname = "t_" + self.increment["unit"]
            wf_df.insert(0, time_colname, time_values)

        return wf_df

    def digits_from_file(self, csv_cached_df: pd.DataFrame = None):
        local_csv_df = csv_cached_df
        filename, extension = os.path.splitext(self.edfilename)
        if extension.lower() == ".csv":
            # Get column from cached dataframe
            if csv_cached_df is None:
                hl = None
                if self.headersize > 0:
                    hl = [r for r in range(self.headersize)]
                    local_csv_df = pd.read_csv(
                        self.edfilename,
                        header=hl
                    )
            if self.numrows > 0:
                # Read requested number of rows
                self.digits = np.array(
                    local_csv_df.iloc[0:self.numrows, self.itemcol])
            else:
                # Read all rows
                self.digits = np.array(
                    local_csv_df.iloc[0:, self.itemcol])

        return local_csv_df


def waveforms_to_df(wf_list: List[Waveform]) -> pd.DataFrame:
    """Generates a dataframe with all waveforms sharing the same time axis.

    Args:
        wf_list (List[Waveform]): List of cipa.Waveform objects.

    Returns:
        pd.DataFrame: Dataframe with all waveforms time series sharing the same
        time axis and values in physical units.
    """

    wf_df = wf_list[0].timeseries_to_df(True)

    if len(wf_list) > 1:
        wf_df2 = pd.concat(
            [wf.timeseries_to_df() for wf in wf_list[1:]], axis=1)
        wf_df = pd.concat([wf_df, wf_df2], axis=1)

    return wf_df
