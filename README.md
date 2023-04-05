## pynetlogo

[![Documentation Status](https://readthedocs.org/projects/emaworkbench/badge/?version=latest)](http://pynetlogo.readthedocs.org/en/latest/?badge=master)
[![PyPi](https://img.shields.io/pypi/v/pynetlogo.svg)](https://pypi.python.org/pypi/pynetlogo)
[![PyPi](https://img.shields.io/pypi/dm/pynetlogo.svg)](https://pypi.python.org/pypi/pynetlogo)

An interface to access [NetLogo](https://ccl.northwestern.edu/netlogo/) from
Python. The interface offers methods for executing commands and returning
values from reporters. It can be used with the NetLogo graphical user
interface, or without (i.e., in headless mode). pynetlogo is compatible with 
NetLogo 6.1 and newer and supports NetLogo extensions.

**Documentation:** http://pynetlogo.readthedocs.io/en/latest/

**Requirements:** [JPype](https://jpype.readthedocs.io/en/latest/)
, [NumPy](http://www.numpy.org/), [SciPy](http://www.scipy.org/)
, [pandas](https://pandas.pydata.org/)

**Installation:** Available with the pip package
manager: `pip install pynetlogo` See [the installation instructions](https://pynetlogo.readthedocs.io/en/latest/install.html)
for more details

**Citation** If you use this library for any academic work, please cite
Jaxa-Rozen & Kwakkel (2018) PyNetLogo: Linking NetLogo with Python, Journal of
Artificial Societies and Social Simulation, 21 (2) 4
<http://jasss.soc.surrey.ac.uk/21/2/4.html>, DOI: 10.18564/jasss.3668


**Releases**
The release process has been updated starting at the 0.5 release. To create a new release, follow the following steps:
 1. Go to [Releases](https://github.com/quaquel/EMAworkbench/releases) in the GitHub UI and press the _Draft a new release_ button
 2. Set the upcoming tag in the _Choose a tag_ and _Release title_ (i.e. `0.6`) fields
 3. The [release.yml](https://github.com/quaquel/EMAworkbench/blob/master/.github/workflows/release.yml) CI workflow should now automatically create and upload the package to PyPI. Check if this happened on [PyPI.org](https://pypi.org/project/ema-workbench/).
 4. Finally, open a new PR in which the version number in [ema_workbench/__init__.py](https://github.com/quaquel/EMAworkbench/blob/master/ema_workbench/__init__.py) is updated towards the next release (i.e. `"2.4.0-dev"`).
