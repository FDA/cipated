"""Core functions of the cipa package for ion channel open data format.

This submodule implements helper functions to validate and read CiPA
datasets stored in files following the Tabulated Experimetal Data (TED) format
specification.

See authors, license and disclaimer at the top level directory of this project.

"""

from typing import List

import logging

# Python logging --------------------------------------------------------------
logger = logging.getLogger(__name__)


# Helper functions ------------------------------------------------------------
def get_supported_versions() -> List[str]:
    """ Returns a list with the supported versions of TED format
    Returns:
        List[str]: list with the supported versions of TED format
    """

    return ["2022.03.rc1", "2022.03"]


# Error classes ---------------------------------------------------------------
class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ParseFileError(Error):
    """Exception raised for errors when parsing files.

    Attributes:
        filename -- filename where parsing failed
        message -- explanation of the error
    """

    def __init__(self, filename, message):
        self.filename = filename
        self.message = message


class EncapsulatedDataFileError(Error):
    """Exception raised for errors when working with encapsulated data files.

    Attributes:
        filename -- filename storing the encapsulated data
        message -- explanation of the error
    """

    def __init__(self, filename, message):
        self.filename = filename
        self.message = message


class Id:
    def __init__(self, root: str, extension: str = ''):
        self.root = str(root)
        self.extension = str(extension)
