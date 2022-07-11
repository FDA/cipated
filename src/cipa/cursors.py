from enum import Enum

from math import isnan


class Cursor_Type(Enum):
    """Type of cursor assessements

    To facilitate basic analyses, the cursor type defines the operation to be
    performed within the region defined by the cursor start and end times. This
    version defines average, maximum and minimum of the signal and specifies a
    custom for other assessments.

    """
    AVERAGE = 1
    MAXIMUM = 2
    MINIMUM = 3
    CUSTOM = 4


class CursorResult:
    """Result of cursor evaluation

    Attributes:
        value (float): value of the result
        unit (str): unit of the value (e.g., pA)
    """
    def __init__(self,  value: float, unit: str):
        self.value = value
        self.unit = unit


class Cursor:
    """Cursor used to assess a feature of the electrophysiological waveform

    Attributes:
        name (str): Name of the cursor
        start (float): start time of the region asssessed by the cursor
        end (float): end time of the region asssessed by the cursor
        time_u (str): time unit
        type (Cursor_Type): cursor type
        result (CursorResult): result from the cursor assessment
    """
    def __init__(
        self, name: str,
        start: float = float('nan'), end: float = float('nan'),
        time_u: str = '',
        type: Cursor_Type = None,
        result: CursorResult = None
            ):
        self.name = name
        self.start = start
        self.end = end
        self.time_u = time_u
        self.type = type
        self.custom_type = ''
        self.result = result
