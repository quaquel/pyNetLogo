"""
Created on Dec 2, 2013

@author: jhkwakkel
"""
import os

from src.pynetlogo import NetLogoLink

jvm_path = "/Users/jhkwakkel/Downloads/jdk-19.0.2.jdk/Contents/MacOS/libjli.dylib"
# jvm_path = "//Users/jhkwakkel/Downloads/jdk-16.0.2+7/Contents/MacOS/libjli.dylib"
netlogo_home = "/Applications/NetLogo 6.3.0"
link = NetLogoLink(jvm_path=jvm_path, netlogo_home=netlogo_home)

print("netlogo link instantiated")
print(link.netlogo_home)

# assumes netlogo 6.0.3
# modelpath = os.path.join(
#     link.netlogo_home, "./models/Sample Models/Biology/Wolf Sheep Predation.nlogo"
# )

modelpath = "/Users/jhkwakkel/Documents/GitHub/pyNetLogo/docs/source/_docs/models//Wolf Sheep Predation_v6.nlogo"

print(modelpath)
print("does modelpath exist? " + str(os.path.exists(modelpath)))

link.load_model(modelpath)

print("model loaded successfully")

link.command("setup")

print("model setup")

energy_df = link.repeat_report(
    [
        "[energy] of wolves",
        "[energy] of sheep",
        "[sheep_str] of sheep",
        "count sheep",
        "glob_str",
    ],
    5,
)

print("model ran")
