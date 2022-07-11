"""Protocol classes of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""
from abc import ABC
from enum import Enum

import copy
import logging

import cipa
from cipa.liquids import Liquid
from cipa.waveforms import Waveform


class Protocol_Type(Enum):
    """
    Type of protocol

    There are different protocols that are run during a CiPA assay to influence
    the system. These include but are not limited to voltage or current
    commands, liquid additions (e.g., dosing, washout), or controlled changes
    in temperature.

    """
    CIPA_PROTOCOL_VOLTAGE = 1
    CIPA_PROTOCOL_CURRENT = 2
    CIPA_PROTOCOL_LIQUID = 3
    CIPA_PROTOCOL_TEMPERATURE = 4
    CIPA_PROTOCOL_UNKNOWN = 99


class Protocol(ABC):
    """
    Protocol to be executed in the assay (abstract class)

    Attributes:
        id (cipa.Id): protocol identifier.
        type (Protocol_Type): type of protocol.
        name (str): name of the protocol.
        duration (float): duration in `duration_u` units of the protocol.
        duration_u (str): units of the `duration` attribute.
        waveform (cipa.waveforms.Waveform, optional): waveform associated with
            the protocol (e.g., intended voltage command). None for liquid
            protocols.
        liquid (cipa.liquids.Liquid, optional): liquid assocaited with the
            protocol (e.g., liquid to be added when dosing). None for voltage,
            current and temperature protocols.
    """
    def __init__(
        self, id: cipa.Id, type: Protocol_Type,
        name: str = '',
        duration: float = 0.0, duration_u: str = 's',
        waveform: Waveform = None,
        liquid: Liquid = None
            ):
        self.id = id
        self.type = type
        self.name = name
        self.duration = duration
        self.duration_u = duration_u
        self.waveform = waveform
        self.liquid = liquid

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)
        cpyobj.id = copy.deepcopy(self.id, memo)
        cpyobj.waveform = copy.deepcopy(self.waveform, memo)
        cpyobj.liquid = copy.deepcopy(self.liquid, memo)

        return cpyobj


class Concentration_Type(Enum):
    """
    Type of concentration

    Liquid protocols include a concentration value for the substance used by
    the protocol. Concentration values are typically described as nominal
    concentrations in the protocol, but values measured in samples collected
    from the well after running the assay are reported some times. In some
    assays, reported values are from satellite experiments, or calculated
    based on some estimation method for a particular device and liquid.
    """
    CIPA_PROTOCOL_LIQUID_CONCENTRATION_NOMINAL = 1
    CIPA_PROTOCOL_LIQUID_CONCENTRATION_CALCULATED = 2
    CIPA_PROTOCOL_LIQUID_CONCENTRATION_MEASURED = 3
    CIPA_PROTOCOL_LIQUID_CONCENTRATION_SATELLITE = 4
    CIPA_PROTOCOL_LIQUID_CONCENTRATION_UNKNOWN = 99


class LiquidProtocol(Protocol):
    """
    Liquid protocol to be executed in the assay (abstract class)

    Attributes:
        id (cipa.Id): protocol identifier.
        liquid (cipa.liquids.Liquid): liquid associated with the protocol
            (e.g., liquid to be added when dosing).
        name (str): name of the protocol.
        duration (float): duration in `duration_u` units of the protocol.
        duration_u (str): units of the `duration` attribute.
        conc (float): concentration of the liquid.
        conc_u (str): units of the `concentration` attribute (e.g., uM).
        conc_type (Concentration_Type): Type of value reported for the
            `conc` attribute.
        isControl (bool): True if the liquid is used as control. False
            otherwise.
        isSelectiveBlocker (bool): True if the liquid is used to eliminate
            residual currents (e.g., E-4031 used to unmask non-hERG mediated
            currents may have this attribute as True in hERG assays that use
            E-4031 at the end of the recordings). False otherwise.
    """
    def __init__(
        self, id: cipa.Id, liquid: Liquid,
        name: str = '',
        duration: float = 0.0, duration_u: str = '',
        conc: float = float('nan'),
        conc_u: str = '',
        conc_type:
            Concentration_Type =
            Concentration_Type.CIPA_PROTOCOL_LIQUID_CONCENTRATION_UNKNOWN,
        isControl: bool = False,
        isSelectiveBlocker: bool = False,
            ):
        super().__init__(
            id=id, type=Protocol_Type.CIPA_PROTOCOL_LIQUID,
            name=name, duration=duration, duration_u=duration_u,
            liquid=liquid)
        self.conc = conc
        self.conc_u = conc_u
        self.conc_type = conc_type
        self.isControl = isControl
        self.isSelectiveBlocker = isSelectiveBlocker


class VoltageProtocol(Protocol):
    """
    Liquid protocol to be executed in the assay (abstract class)

    Attributes:
        id (cipa.Id): protocol identifier.
        waveform (cipa.waveforms.Waveform): waveform associated with the
            protocol (e.g., waveform of the intended voltage command).
        name (str): name of the protocol.
        duration (float): duration in `duration_u` units of the protocol.
        duration_u (str): units of the `duration` attribute.
    """
    def __init__(
        self, id: cipa.Id, waveform: Waveform,
        name: str = '',
        duration: float = 0.0, duration_u: str = ''
            ):
        super().__init__(
            id=id, type=Protocol_Type.CIPA_PROTOCOL_VOLTAGE,
            name=name, duration=duration, duration_u=duration_u,
            waveform=waveform)
