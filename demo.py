'''


'''
from __future__ import (unicode_literals, print_function, absolute_import,
                                        division)
import logging
import sys

import pyNetLogo.pyNetLogo as netlogo



# Created on 1 Nov 2016
#
# .. codeauthor::jhkwakkel <j.h.kwakkel (at) tudelft (dot) nl>

__all__ = []

# logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stderr)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(' %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


# on mac there is a stupid issue with getting the default jvm path
# this is related to some mac bug in java 8
jvm_home = '/Library/Java/JavaVirtualMachines/jdk1.8.0_101.jdk/Contents/Home/jre/lib/server/libjvm.dylib'
link = netlogo.NetLogoLink(jvm_home=jvm_home)
link.load_model('Wolf Sheep Predation.nlogo')