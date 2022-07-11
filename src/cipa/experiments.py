"""Experiment class of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""
from typing import List

import copy
import logging

import cipa

from cipa.results import ProtocolExecution, Results


class Experiment:
    """
    Experiment part of a CiPA assay

    Attributes:
        id (cipa.Id): experiment identifier.
        name (str): name of the experiment.
        device (cipa.Id): identifier of the device used to conduct the
            experiment. Instead of a pointer to one of the devices listed
            in the `cipa.trials.Trial`, the device reference is stored as a
            foreign key using its identifier.
        startTime (str): start time of the experiment coded as ISO-8601.
        protocols (List[cipa.results.ProtocolExecution]): List of execution
            of protocols during the experiment.
        results (List[cipa.results.Results]): List of results recorded during
            the experiment and after analyzing some of them.
    """
    def __init__(
        self, id: cipa.core.Id,
        name: str = '',
        device: cipa.core.Id = None,
        startTime: str = '',
        protocols: List[ProtocolExecution] = None,
        resultsSet: List[Results] = None
            ):
        self.id = id
        self.name = name
        self.device = device
        self.startTime = startTime
        self.protocols = protocols
        self.resultsSet = resultsSet

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)
        cpyobj.id = copy.deepcopy(self.id, memo)
        cpyobj.device = copy.deepcopy(self.device, memo)
        cpyobj.protocols = copy.deepcopy(self.protocols, memo)
        cpyobj.resultsSet = copy.deepcopy(self.resultsSet, memo)

        return cpyobj
