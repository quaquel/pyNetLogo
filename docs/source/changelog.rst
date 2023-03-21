Changelog
=========

Version 0.5
-----------
- support for netlogo 6.3
- dropped support for netlogo 5.x and 6.0
- renamed library from pyNetLogo to pynetlogo to abide with pep8 naming conventions
- minor changes in names of keyword arguments of various methods
- shift from setup.py to pyproject.toml
- removal of python 2 support

Version 0.4
-----------
support for NetLogo 6.1 and 6.2

Version 0.3
-----------
- new repeat_report method
- load_model now raises a FileNotFoundError if the model can't be found
- use temporary folders created by tempfile module in repeat_report (contributed by tfrench)
- extensions now no longer need to be copied to the model directory (contributed by tfrench)
- addition keyword argument on init of PyNetLogo link for passing
  additional arguments to jvm 
- additional documentation 


