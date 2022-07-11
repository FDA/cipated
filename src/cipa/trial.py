"""Top level class of the cipa package for ion channel open data format.

This submodule implements the top level class that groups all the data elements
of a CiPA dataset following the Tabulated Experimetal Data (TED) format
specifications.

See authors, license and disclaimer at the top level directory of this project.

"""

from typing import List

import copy
import logging

from cipa.devices import Device
from cipa.experiments import Experiment
from cipa.liquids import (
    Liquid, LiquidJunctionPotential)
from cipa.protocols import Protocol
from cipa.study import Study

import cipa


class Trial:
    """
    A CiPA trial or assay

    Attributes:

        version (str): version of the format specifications document used to
            generate the files of the Tabulated Experimetal Data (TED) format
            dataset.
        description (str): short description of the assay documented in the COD
            dataset.
        study (Study): general information about the study or assay (e.g.,
            protocol number).
        devices (List[Device]): devices used to perform the assay.
        ljp (LiquidJunctionPotential): default liquid junction potential of the
            internal/external solutions.
        liquids (List[Liquid]): Liquids applied in the assay.
        protocols (List[Protocol]): Protocols used in the assay (e.g.,
            voltage protocols, additions of liquids and/or drugs)
        experiments (List[Experiment]): Experiments performed in the assay.
            These include executed protocols and associated results.

    """

    def __init__(
        self, version: str = '', description: str = '',
        study: Study = None,
        devices: List[Device] = None,
        ljp: LiquidJunctionPotential = None,
        liquids: List[Liquid] = None,
        protocols: List[Protocol] = None,
        experiments: List[Experiment] = None
            ):

        if version != '':
            self.version = version
        else:
            self.version = cipa.__version__
        self.description = description
        self.study = study
        if devices is None:
            self.devices = []
        else:
            self.devices = devices
        self.ljp = ljp
        if liquids is None:
            self.liquids = []
        else:
            self.liquids = liquids
        if protocols is None:
            self.protocols = []
        else:
            self.protocols = protocols
        if experiments is None:
            self.experiments = []
        else:
            self.experiments = experiments

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)
        cpyobj.study = copy.deepcopy(self.study, memo)
        cpyobj.ljp = copy.deepcopy(self.ljp, memo)
        cpyobj.devices = copy.deepcopy(self.devices, memo)
        cpyobj.liquids = copy.deepcopy(self.liquids, memo)
        cpyobj.protocols = copy.deepcopy(self.protocols, memo)
        cpyobj.experiments = copy.deepcopy(self.experiments, memo)

        return cpyobj
