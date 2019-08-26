## pyNetLogo

[![Documentation Status](https://readthedocs.org/projects/emaworkbench/badge/?version=latest)](http://pynetlogo.readthedocs.org/en/latest/?badge=master)
[![PyPi](https://img.shields.io/pypi/v/pynetlogo.svg)](https://pypi.python.org/pypi/pynetlogo)
[![PyPi](https://img.shields.io/pypi/dm/pynetlogo.svg)](https://pypi.python.org/pypi/pynetlogo)

An interface to access [NetLogo](https://ccl.northwestern.edu/netlogo/) from Python.
The interface offers methods for executing commands and returning values from reporters.
It can be used with the NetLogo graphical user interface, or without (i.e. in headless mode).
pyNetLogo is currently compatible with NetLogo 5.2, 5.3, 6.0, and 6.1 and should support
most NetLogo extensions.

**Documentation:** http://pynetlogo.readthedocs.io/en/latest/

**Requirements:** [JPype](https://jpype.readthedocs.io/en/latest/), [NumPy](http://www.numpy.org/), [SciPy](http://www.scipy.org/), [pandas](https://pandas.pydata.org/)

**Installation:** Available with the pip package manager: `pip install pyNetLogo`, but it
depends on jpype which needs to be installed separately. See [the installation instructions](https://pynetlogo.readthedocs.io/en/latest/install.html)
for more details


**Citation** If you use this library for any academic work, please cite
Jaxa-Rozen & Kwakkel (2018) PyNetLogo: Linking NetLogo with Python, 
Journal of Artificial Societies and Social Simulation, 21 (2) 4
<http://jasss.soc.surrey.ac.uk/21/2/4.html>, DOI: 10.18564/jasss.3668