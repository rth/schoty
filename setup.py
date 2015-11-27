#!/usr/bin/python
import re
from setuptools import setup, find_packages

# a define the version sting inside the package
# see https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package 
VERSIONFILE="schoty/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(name='schoty',
      version=version,
      description='A Python package for parsing bank statements',
      packages=find_packages(),
      #package_data={'abel': ['tests/data/*' ]},
      install_requires=[
              "setuptools >= 16.0",
              ],
      test_suite="schoty.tests.run_cli"
     )

