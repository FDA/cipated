# CiPA Open Data: Tabulated Experimental Data (TED) format python package

## Abstract

This python package provides basic functionality to read and write datasets
following the Tabulated Experimental Data (TED) format for electrophysiology
raw data (e.g., ion channel data collected under the Comprehensive in vitro
Proarrhythmia Assay [CiPA] initiative).

For a use case example, see Alvarez-Baron et. al *"hERG block potencies for 5
positive control drugs obtained per ICH E14/S7B Q&As best practices: impact of
recording temperature and drug loss"*. J Pharamacol Tox Methods 2022. The
original raw recordings as well as derived TED datasets, analysis scripts,
tabulated results, figures, and reports generated using this package are also
available at [https://osf.io/6w5vn/](https://osf.io/6w5vn/).

See LICENSE and DISCLAIMER at the end of this document.

## Prepare your python environment (optional)

These instructions assume you already have python 3.7.7 or conda installed in
your system.

* Create the cipa-suite directory
  ```
  cd ~/code
  mkdir cipa-suite
  ```

### Linux

* Create a python virtual environment. Here we create the *cipavenv* environment
in ~/code/cipa-suite
  ```
  cd ~/code/cipa-suite
  python -m venv cipavenv
  ```

* Next, activate the virtual environment.
  ```
  source ~/code/cipa-suite/cipavenv/bin/activate
  ```

* Upgrade pip to the most recent version
  ```
  pip install --upgrade pip
  ```

### Anaconda (conda)

* Create a python virtual environment. Here we create the *cipavenv* environment
in ~/code/cipa-suite:
  ```
  cd ~/code/cipa-suite
  conda create -p cipavenv
  ```

* Activate the new conda environment:
  ```
  conda activate .\cipavenv
  ```

* Install python 3.7.7:
  ```
  conda install python==3.7.7
  ```

## Setup

Clone the cipated repository from
[https://github.com/FDA/cipated](https://github.com/FDA/cipated) or
get a copy of the source code.

### Install cipa package and dependencies

* Change to the directory where you have the source code of cipated
  ```
  cd ~/code/cipa-suite/cipated
  ```

* Install cipated in editable mode so you can both use it and make changes
without reinstalling it.

  This will also install the package dependencies
  ```
  pip install -e .
  ```

## Development and deployment tips

### How to build the package for distribution from the source code

To create a source and wheels distributions, type
```python setup.py sdist bdist_wheel``` in the command line.

### How to generate a local copy of the documentation

Install the following additional **requirements**:
```
pip install sphinx sphinx-autobuild sphinx-autodoc-typehints mock autodoc myst-parser
```

Next, assuming you have a copy of the source code in
~/code/cipa-suite/cipated, you can generate a local html version of the
documentation from the command line as follows:
```
cd ~/code/cipa-suite/cipated/docs
make html
```

## Authors

**Jose Vicente Ruiz** \<<jose.vicenteruiz@fda.hhs.gov>\><br>

    Senior Staff Fellow
    Division of Cardiology and Nephrology
    Office of Cardiology, Hematology, Endocrinology and Nephrology
    Office of New Drugs
    Center for Drug Evaluation and Research
    U.S. Food and Drug Administration

**Manni Mashaee** \<<manni.mashaee@fda.hhs.gov>\><br>

    ORISE Fellow
    Division of Cardiology and Nephrology
    Office of Cardiology, Hematology, Endocrinology and Nephrology
    Office of New Drugs
    Division of Applied Regulatory Science
    Office of Clinical Pharmacology, Office of Translational Sciences
    Center for Drug Evaluation and Research
    U.S. Food and Drug Administration

## License

This code is in the public domain within the United States, and copyright and
related rights in the work worldwide are waived through the CC0 1.0 Universal
Public Domain Dedication. This example is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See DISCLAIMER section
below, the COPYING file in the root directory of this project and
https://creativecommons.org/publicdomain/zero/1.0/ for more details.

## Disclaimer

FDA assumes no responsibility whatsoever for use by other parties of the
Software, its source code, documentation or compiled executables, and makes no
guarantees, expressed or implied, about its quality, reliability, or any other
characteristic. Further, FDA makes no representations that the use of the
Software will not infringe any patent or proprietary rights of third parties.
The use of this code in no way implies endorsement by the FDA or confers any
advantage in regulatory decisions.