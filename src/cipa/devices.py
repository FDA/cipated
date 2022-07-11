"""Device class of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""
import copy
import logging

import cipa


class Device:
    """
    Device used to perform electrophysiology experiments and recordings

    Attributes:
        id (cipa.core.Id): device identifier.
        code (str): study report version.
        manufacturerModelName (str): manufacturer's model name
        deviceSoftwareName (str): software or firmware name and information
            (e.g., version)
        analysisSoftwareName (str): analysis software name and informatio
            (e.g., software runing on a computer connected to the device).
        codSoftwareName (str): cipa open data software name and information
            (e.g., version) used to generate datasets.
        additionalAnalysisInformation (str): additional general information
            regarding the analysis
    """
    def __init__(
        self, id: cipa.core.Id = None,
        code: str = '',
        manufacturerModelName: str = '',
        deviceSoftwareName: str = '',
        analysisSoftwareName: str = '',
        codSoftwareName: str = '',
        additionalAnalysisInformation: str = ''
            ):
        self.id = id
        self.code = code
        self.manufacturerModelName = manufacturerModelName
        self.deviceSoftwareName = deviceSoftwareName
        self.analysisSoftwareName = analysisSoftwareName
        self.codSoftwareName = codSoftwareName
        self.additionalAnalysisInformation = additionalAnalysisInformation

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)

        return cpyobj
