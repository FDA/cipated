"""Results classes and types of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""
from cipa.properties import Property

from enum import Enum
from typing import List

import copy
import logging

import cipa

from cipa.cursors import Cursor
from cipa.liquids import LiquidJunctionPotential
from cipa.protocols import Protocol
from cipa.waveforms import Waveform


class ProtocolExecution:
    """Execution of a protocol (e.g., voltage command, drug addition)

    Attributes:
        protocol (Protocol): executed protocol
        time (float): time in time_u units from the begining of the experiment
            when the protocol was executed
        time_u (str): time unit
    """
    def __init__(
        self, protocol: Protocol,
        time: float = 0.0, time_u: str = 's'
            ):
        self.protocol = protocol
        self.time = time
        self.time_u = time_u

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)
        cpyobj.protocol = copy.deepcopy(self.protocol, memo)

        return cpyobj


class Patch_Type(Enum):
    """Types of patch
    """
    CIPA_CELL_SINGLE = 1
    CIPA_CELL_POPULATION = 2
    CIPA_CELL_UNKNOWN = 99


class Cell:
    """Cell used in the experiment

    Attributes:
        id (cipa.core.id): cell identifier
        properties (List[Property]): list of cell properties
    """
    def __init__(
        self, id: cipa.core.Id = None,
        properties: List[Property] = [],
            ):
        self.id = id
        self.properties = properties


class LeakMethod_Type(Enum):
    """Types of leak methods
    """
    CIPA_LEAK_METHOD_NONE = 1
    CIPA_LEAK_METHOD_SMALL_PULSE = 2
    CIPA_LEAK_METHOD_FAST_LEAK = 3
    CIPA_LEAK_METHOD_SWEEP = 4
    CIPA_LEAK_METHOD_ZERO_CURSOR = 5
    CIPA_LEAK_METHOD_UNKNOWN = 99


class Result_Type(Enum):
    """Types of results
    """
    CIPA_RESULT_TYPE_VOLTAGE = 1
    CIPA_RESULT_TYPE_CURRENT = 2
    CIPA_RESULT_TYPE_TEMPERATURE = 3
    CIPA_RESULT_TYPE_SERIES_RESISTANCE = 4
    CIPA_RESULT_TYPE_SERIES_RESISTANCE_COMPENSATION = 5
    CIPA_RESULT_TYPE_SEAL_RESISTANCE = 6
    CIPA_RESULT_TYPE_MEMBRANE_CAPACITANCE = 7
    CIPA_RESULT_TYPE_INPUT_RESISTANCE = 8
    CIPA_RESULT_TYPE_UNKNOWN = 99


class Result:
    """Recorded result from a given trace from a cell during the experiment

    Attributes:
        traceNumner (int): Trace number
        valid (bool): Boolean indicating if this result is adequate and
            included in subsequent analyses (e.g., IC50 calculation)
        type (Result_Type): Type of result
        elapsedTime (float): Time from the begining of the experiment
        elapsedTime_u (str): Time unit
        waveform (Waveform): Recorded waveform
        cursors (List[Cursor]): List of evaluated cursors
    """
    def __init__(
        self, traceNumber: int, valid: bool, type: Result_Type,
        elapsedTime: float, elapsedTime_u: str = 's',
        waveform: Waveform = None,
        cursors: List[Cursor] = None
            ):
        self.traceNumber = traceNumber
        self.valid = valid
        self.type = type
        self.elapsedTime = elapsedTime
        self.elapsedTime_u = elapsedTime_u
        self.waveform = waveform
        self.cursors = cursors


class Results:
    """Recorded result from a given trace from a cell during the experiment

    Attributes:
        cell (Cell): cell where the results come from
        patchType (Patch_Type): Type of patch
        PateId (str): Plate identifier (for automated systems)
        WellId (str): Well identifier (for automated systems)
        leakMethod (LeakMethod_Type):Leak correction method
        ljp (LiquidJunctionPotential): Liquid junction potential
        cursors (List[Cursor]): List of cursors to be evaluated
        results (List[Result]): List of results including waveforms and cursors
        lab (str, Optional): Name of the laboratory conducting the assessment.
            Defaults to ''.
        method (str, Optional): Name of the method use in the evaluation.
            Defautls to ''.
    """
    def __init__(
        self, cell: Cell, patchType: Patch_Type,
        plateId: str = '', wellId: str = '',
        leakMethod: LeakMethod_Type = LeakMethod_Type.CIPA_LEAK_METHOD_UNKNOWN,
        ljp: LiquidJunctionPotential = None,
        cursors: List[Cursor] = None,
        results: List[Result] = None,
        lab: str = '',
        method: str = ''
            ):
        self.lab = lab
        self.method = method
        self.cell = cell
        self.patchType = patchType
        self.plateId = plateId
        self.wellId = wellId
        self.leakMethod = leakMethod
        self.ljp = ljp
        self.cursors = cursors
        self.results = results
