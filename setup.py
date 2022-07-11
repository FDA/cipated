"""Setup file for cipa package for ion channel open data format.

**Authors**

***Jose Vicente Ruiz*** <jose.vicenteruiz@fda.hhs.gov><br>

    Division of Cardiology and Nephrology
    Office of Cardiology, Hematology, Endocrinology and Nephrology
    Office of New Drugs
    Center for Drug Evaluation and Research
    U.S. Food and Drug Administration

**Manni Mashaee** <manni.mashaee@fda.hhs.gov>

    ORISE Fellow

    Division of Cardiology and Nephrology
    Office of Cardiology, Hematology, Endocrinology and Nephrology
    Office of New Drugs
    Center for Drug Evaluation and Research
    U.S. Food and Drug Administration
    

    Division of Applied Regulatory Science
    Office of Clinical Pharmacoloy
    Office of Translational Science
    Center for Drug Evaluation and Research
    U.S. Food and Drug Administration

*Created*: December 6, 2019<br>
*Last update*: Januay 15, 2021


* LICENSE *
===========
This code is in the public domain within the United States, and copyright and
related rights in the work worldwide are waived through the CC0 1.0 Universal
Public Domain Dedication. This example is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See DISCLAIMER section
below, the COPYING file in the root directory of this project and
https://creativecommons.org/publicdomain/zero/1.0/ for more details.

* Disclaimer *
==============
FDA assumes no responsibility whatsoever for use by other parties of the
Software, its source code, documentation or compiled executables, and makes no
guarantees, expressed or implied, about its quality, reliability, or any other
characteristic. Further, FDA makes no representations that the use of the
Software will not infringe any patent or proprietary rights of third parties.
The use of this code in no way implies endorsement by the FDA or confers any
advantage in regulatory decisions.

"""

from setuptools import setup, find_packages

import codecs
import os
import pathlib


setup_path = pathlib.Path(__file__).parent.resolve()
long_description = (setup_path / 'README.md').read_text(encoding='utf-8')
history_log = (setup_path / 'HISTORY.md').read_text(encoding='utf-8')


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


setup(name="cipa",
      version=get_version("src/cipa/__init__.py"),
      description="Validation and reader tools for datasets stored in the "
                  "CiPA Open Data format (COD files)",
      long_description=long_description + history_log,
      long_description_content_type="text/markdown",

      url='https://github.com/FDA/cipated',

      author="Jose Vicente Ruiz",
      author_email="jose.vicenteruiz@fda.hhs.gov",

      keywords="FDA, CiPA, ion channels, hERG, COD, electrophysiology, "
               "drug, cardiac, xml",

      package_dir={'': 'src'},
      packages=find_packages(where='src'),

      license="CC0",

      install_requires=[
          "cmdstanpy>=1.0.1",
          "matplotlib>=3.3.4",
          "numpy>=1.21.6",
          "openpyxl==3.0.9",
          "pandas>=1.3.5",
          "pytest==5.4.3",
          "tqdm>=4.46.1",
          "scipy>=1.4.1",
          "xlrd==1.2.0",
          "xport==2.0.2"],

      package_data={"cipa": [
          "cfg/cipa_logging.conf",
          ]},
      include_package_data=True,


      project_urls={
          'Bug Reports': 'https://github.com/FDA/cipated/issues',
          'Source': 'https://github.com/FDA/cipated',
          },

      python_requires='>=3.7.7',)
