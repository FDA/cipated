"""Study classes of the cipa open data package

See authors, license and disclaimer at the top level directory of this project.

"""
import copy
import logging


class StudyReport:
    """
    Study report of a CiPA Study

    Attributes:
        title (str): study report title.
        version (str): study report version.
        date (str): study report date in ISO-8106 format.
        text (str): contents of the study report.
    """
    def __init__(
        self, title: str = '', version: str = '', date: str = '',
        text: str = ''
            ):
        self.title = title
        self.version = version
        self.date = date
        self.text = text

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)

        return cpyobj


class Study:
    """
    A CiPA Study

    Attributes:
        studyId (str): study identifier.
        report (StudyReport): study report information.
    """
    def __init__(self, studyId: str = '', report: StudyReport = None):
        self.studyId = studyId
        if report:
            self.report = report
        else:
            self.report = StudyReport()

        self.logger = logging.getLogger(__name__)

    def __deepcopy__(self, memo={}):
        cpyobj = copy.copy(self)
        cpyobj.report = copy.deepcopy(self.report, memo)

        return cpyobj
