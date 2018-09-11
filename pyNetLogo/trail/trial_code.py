'''
Created on Dec 2, 2013

@author: jhkwakkel
'''
from __future__ import print_function
from pyNetLogo import NetLogoLink

import os

link = NetLogoLink()


print("netlogo link instantiated")
print(link.netlogo_home)

# assumes netlogo 6.0.3
modelpath = os.path.join(link.netlogo_home, 
         './models/Sample Models/Biology/Wolf Sheep Predation.nlogo')
print(modelpath)
print("does modelpath exist? " + str(os.path.exists(modelpath)))

link.load_model(modelpath)

print("model loaded successfully")
