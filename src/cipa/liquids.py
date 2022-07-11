"""Liquid classes of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""
from enum import Enum

import copy
import logging

import cipa


class LJP_ReportedVoltage_Type(Enum):
    """
    Type of Liquid Junction Potential Voltage

    Sign convention Vcell = Vclamp - Vljp

    """
    Vcell = 1
    Vclamp = 2


class LiquidJunctionPotential:
    """
    Liquid junction potential

    Attributes:
        value (float): liquid junction potential voltage value assuming sign
            convention Vcell = Vclamp - Vljp
        unit (str): unit of the reported value (e.g., mV)
        reportedVoltage (LJP_ReportedVoltage_Type): either
            `LJP_ReportedVoltage_Type.Vclamp` for reported voltages already
            corrected for liquid juntion potential or
            `LJP_ReportedVoltage_Type.Vcell` for reported voltages not
            corrected for liquid junction potential.
    """
    def __init__(
        self, value: float = float('nan'), unit: str = '',
        reportedVoltage: LJP_ReportedVoltage_Type =
            LJP_ReportedVoltage_Type.Vclamp
            ):
        self.value = value
        self.unit = unit
        self.reportedVoltage = reportedVoltage


class Liquid:
    """
    Liquid used in a CiPA assay

    Attributes:
        id (cipa.Id): liquid identifier.
        name (str): liquid name (e.g., control, drug X)
        batch (str): liquid batch.
        description (str): additional description of the liquid.
    """
    def __init__(
        self, id: cipa.Id, name: str,
        batch: str = '', description: str = ''
            ):
        self.id = id
        self.name = name
        self.batch = batch
        self.description = description

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)
        cpyobj.id = copy.deepcopy(self.id, memo)

        return cpyobj
