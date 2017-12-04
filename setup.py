from __future__ import (print_function, absolute_import)

import io
import os
import re

from setuptools import setup


def read(path, encoding='utf-8'):
    path = os.path.join(os.path.dirname(__file__), path)
    with io.open(path, encoding=encoding) as fp:
        return fp.read()


def version(path):
    """Obtain the packge version from a python file e.g. pkg/__init__.py
    See <https://packaging.python.org/en/latest/single_source_version.html>.
    """
    version_file = read(path)
    version_match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def package_files(root, package_data_dir):
    paths = []
    
    directory = os.path.join(root, package_data_dir)
    
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(path, filename)
            
            paths.append(os.path.relpath(full_path, root))
    return paths


java_files = package_files('pyNetLogo', 'java')
# java_files = [''.join(['connectors/', entry]) for entry in java_files]

NAME = 'pyNetLogo'
pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
pkg_root = pjoin(here, NAME)

packages = []
for d, _, _ in os.walk(pjoin(here, NAME)):
    if os.path.exists(pjoin(d, '__init__.py')):
        packages.append(d[len(here)+1:].replace(os.path.sep, '.'))


VERSION = version('pyNetLogo/__init__.py')
LONG_DESCRIPTION ="""Project Documentation: https://pyNetLogo.readthedocs.io/"""

JAVA = java_files
PACKAGES = packages



setup(
    name            = NAME,
    version         = VERSION,
    description     = 'Python interface to NetLogo',
    long_description= LONG_DESCRIPTION,
    author          = 'Jan Kwakkel',
    author_email    = 'j.h.kwakkel@tudelft.nl',
    packages        = PACKAGES,
    package_data    = {NAME: JAVA},
    url             = 'https://github.com/quaquel/pyNetLogo',
    license         = 'BSD 3-Clause',
    platforms       = "Linux, Mac OS X, Windows",
)