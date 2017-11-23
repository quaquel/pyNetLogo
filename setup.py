from setuptools import setup

NAME = 'pyNetLogo'

VERSION = 0.1
LONG_DESCRIPTION ="""Project Documentation: https://pyNetLogo.readthedocs.io/"""

setup(
    name            = NAME,
    version         = VERSION,
    description     = 'Python interface to NetLogo',
    long_description= LONG_DESCRIPTION,
    author          = 'Jan Kwakkel',
    author_email    = 'j.h.kwakkel@tudelft.nl',
    url             = 'https://github.com/quaquel/pyNetLogo',
    license         = 'BSD 3-Clause',
    platforms       = "Linux, Mac OS X, Windows",
)
