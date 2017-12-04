'''
Created on Dec 2, 2013

@author: jhkwakkel
'''
import os
import jpype

NETLOGO_HOME = r'/Applications/NetLogo 5.0.4'
PYNETLOGO_HOME = r'/Domain/tudelft.net/Users/jhkwakkel/pyNetLogo/pyNetLogo/pyNetLogo'

jars = [NETLOGO_HOME + r'/lib/scala-library.jar',
        NETLOGO_HOME + r'/lib/asm-all-3.3.1.jar',
        NETLOGO_HOME + r'/lib/picocontainer-2.13.6.jar',
        NETLOGO_HOME + r'/lib/log4j-1.2.16.jar',
        NETLOGO_HOME + r'/lib/jmf-2.1.1e.jar',
        NETLOGO_HOME + r'/lib/pegdown-1.1.0.jar',
        NETLOGO_HOME + r'/lib/parboiled-core-1.0.2.jar',
        NETLOGO_HOME + r'/lib/parboiled-java-1.0.2.jar',
        NETLOGO_HOME + r'/lib/mrjadapter-1.2.jar',
        NETLOGO_HOME + r'/lib/jhotdraw-6.0b1.jar',
        NETLOGO_HOME + r'/lib/quaqua-7.3.4.jar',
        NETLOGO_HOME + r'/lib/swing-layout-7.3.4.jar',
        NETLOGO_HOME + r'/lib/jogl-1.1.1.jar',
        NETLOGO_HOME + r'/lib/gluegen-rt-1.1.1.jar',
        NETLOGO_HOME + r'/NetLogo.jar',
        PYNETLOGO_HOME + r'/java/netlogoLink.jar']

jarpath = ":".join(jars) 
jarpath = '-Djava.class.path={}'.format(jarpath)
jvm_handle = jpype.getDefaultJVMPath()

print jvm_handle

jpype.startJVM(jvm_handle, jarpath, "-Xmx1024m")
jpype.java.lang.System.setProperty('user.dir', NETLOGO_HOME)
jpype.java.lang.System.setProperty("java.awt.headless", "true");

print jpype.java.lang.System.getProperty("java.runtime.version")
     
link = jpype.JClass('netlogoLink.NetLogoLink')
link = link(False, False)

print "netlogo link instanciated"

link.loadModel(r'/Domain/tudelft.net/Users/jhkwakkel/EMAworkbench/models/predatorPreyNetlogo/Wolf Sheep Predation.nlogo')