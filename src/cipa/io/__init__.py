"""Input/output utility functions of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""

from typing import Dict, List

import logging


# Initialization --------------------------------------------------------------

logger = logging.getLogger(__name__)


# Other I/O helper functions --------------------------------------------------

def value_to_int(val: float, scale: float, origin: float) -> int:
    """ Convert double to a scaled integer referenced to an origin.

    Args:
        val (float): Physical value to code as integer using scale and origin.
        scale (float): scale factor to apply (in physical units).
        origin (float): reference value in physical units.

    Returns:
        int: Scaled integer value referenced to the origin.
    """
    return round(val * scale + origin)


def physical_to_int16(physical_values: List[float]) -> Dict:
    """ Convert a list of physical_values to int16 values

    Args:
        physical_values (List[float]): physical quantities

    Returns:
        Dict: Dictionary with list of integers of 16 bits precission in
        sampled_values and the corresponding origin and scale factors.
    """
    amplitude = max(physical_values) - min(physical_values)
    origin = min(physical_values)
    # Using 16 bits numbers (i.e., 2 bytes)
    if amplitude > 1:
        scale = amplitude / (2 ^ 16 - 1)
    else:
        scale = (2 ^ 16 - 1) / amplitude
    int16_values = [value_to_int(n, scale, origin) for n in physical_values]

    return {"sampled_values": int16_values, "origin": origin, "scale": scale}


def sampled_to_physical(
    sampled_values: List[int], origin: float, scale: float
        ) -> List[float]:
    """ Converts a list of sampled values to their physical quantities

    Args:
        sampled_values (List[int]): integer values
        origin (float): The origin of the list item value scale, i.e., the
            physical quantity that a zero-digit would represent in the sequence
            of values.
        scale (float): A ratio-scale quantity that is factored out of the
            sequence of values.

    Returns:
        List[float]: physical_values = (sampled_values - origin) / scale
    """

    physical_values = [(n - origin) / scale for n in sampled_values]

    return physical_values
