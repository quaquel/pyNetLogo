'''
Created on 21 mrt. 2013

@author: J.H. Kwakkel

This module allows controlling netlogo models from within Python. It is modeled
on the R-Netlogo package. On a mac, this package will work but only in 
Headless mode. This module requires jPype for connecting Python to Java.


'''
from __future__ import unicode_literals, absolute_import

import jpype
import os
import sys

from logging import debug, info, warning

__all__ = ['NetLogoException',
           'NetLogoLink']
    
PYNETLOGO_HOME = os.path.dirname(os.path.abspath(__file__))

#Jar supports NetLogo 5.2 or 6.0
netlogo_class = {'5.2':'netlogoLink_v52.NetLogoLink',
                 '6.0':'netlogoLink_v6.NetLogoLink'}

# TODO:: have a function that returns the most up to date netlogo version
# given a directory

def find_netlogo(path):
    '''find the most recent version of netlogo in the specified directory
    
    Parameters
    ----------
    path : str
    
    Returns
    -------
    str
    
    Raises
    ------
    IndexError if no netlogo version is found in path
    
    '''
    
    path = os.path.abspath(path)
    netlogo_versions = [entry for entry in os.listdir(path) if 'netlogo' in 
                        entry.lower()]
    
    # sort handles version numbers properly as long as pattern of 
    # directory name is not changed
    netlogo_versions.sort(reverse=True)
    
    return netlogo_versions[0]

def find_jars(path):
    '''find all jars in directory and return as list
    '''
    
    jars = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".jar"):
                jars.append(os.path.join(root, file))
    return jars


if sys.platform=='win32':
    jar_separator = ";"  
    
    #Try to find either NetLogo 5.2 or 6.0 in the program path, use 6.0 if available
    if os.environ['PROGRAMW6432']:
        path32 = os.environ['PROGRAMFILES(X86)']
        path64 = os.environ['PROGRAMW6432'] 
        
        try:
            
            netlogo = find_netlogo(path64)
        except IndexError:
            try:
                netlogo = find_netlogo(path32)
            except IndexError:
                netlogo = None
    else:
        path32 = os.environ['PROGRAMFILES']
        try:
            netlogo = find_netlogo(path32)
        except IndexError:
            netlogo = None
    
    # TODO:: will break in case of 5.6, should be done better
    if '6' in netlogo:
        NETLOGO_VERSION = '6.0'
        NETLOGO_HOME = os.path.join(netlogo, 'app')
        #Use all jars in the root of the /app directory (includes NetLogo.jar)
        jars = [os.path.join(NETLOGO_HOME, f) for f in os.listdir(NETLOGO_HOME) if f.endswith('.jar')]
        
    elif '5' in netlogo:
        NETLOGO_VERSION = '5.2'
        NETLOGO_HOME = netlogo
        #Use all jars in the root of the /lib directory
        v52_lib = os.path.join(NETLOGO_HOME, 'lib')
        jars = [os.path.join(v52_lib, f) for f in os.listdir(v52_lib) if f.endswith('.jar')]
        jars.append(os.path.join(NETLOGO_HOME, 'NetLogo.jar'))
        
    else:
        #Should be an exception
        warning('NetLogo not found')   
    
    #NETLOGO_HOME = r'C:/Program Files (x86)/NetLogo 5.1.0/lib'
    #NETLOGO_HOME = r'C:/Program Files/NetLogo 6.0-BETA1/app'
    
elif sys.platform=='darwin':
    jar_separator = ":"   
    NETLOGO_HOME = r'/Applications/NetLogo 5.2.1'
    NETLOGO_VERSION = '5.2'   
    
else:
    warning('NetLogo not supported on this platform')  


class NetLogoException(Exception):
    """Basic project specific exception """
    
    pass

class NetLogoLink():
    
    def __init__(self, gui=False, thd=False, nl_dir=None, nl_version=None):
        '''
        
        Create a link with Netlogo. Underneath, the netlogo jvm is started
        through jpype.
        
        
        :param gui: boolean, if true run netlogo with gui, otherwise run in 
                    headless mode. Defaults to false.
        :param thd: boolean, if thrue start netlogo in 3d mode. Defaults to 
                    false
        :param nl_dir: string - full path to NetLogo .jar directory, use if
                    NetLogo is not in the default location
        :param nl_version: string - NetLogo version under nl_dir (5.2 or 6.0)
        
        '''
        if not jpype.isJVMStarted():

        
#Not sure how to handle a custom path without using global variables
#or without setting the NETLOGO_HOME each time the class is instantiated

#             if (nl_dir and nl_version):
#                 debug('Using custom directory')
#                 NETLOGO_VERSION = nl_version
#                 if nl_version == '5.2':
#                     NETLOGO_HOME = nl_dir
#                     v52_lib = os.path.join(NETLOGO_HOME, 'lib')
#                     jars = [os.path.join(v52_lib, f) for f in os.listdir(v52_lib) if f.endswith('.jar')]
#                     jars.append(os.path.join(NETLOGO_HOME, 'NetLogo.jar'))
#                 elif nl_version == '6.0':
#                     NETLOGO_HOME = os.path.join(nl_dir, 'app')
#                     jars = [os.path.join(NETLOGO_HOME, f) for f in os.listdir(NETLOGO_HOME) if f.endswith('.jar')]                                        
                
            #debug('Using NetLogo.jar at ' + NETLOGO_HOME)
            #debug('NetLogo version ' + NETLOGO_VERSION)

            jars.append(PYNETLOGO_HOME + r'/netlogoLink_combined.jar')   
            joined_jars = jar_separator.join(jars)
            jarpath = '-Djava.class.path={}'.format(joined_jars)
            
            jvm_handle = jpype.getDefaultJVMPath()  
            jpype.startJVM(jvm_handle, jarpath)
              
            jpype.java.lang.System.setProperty('user.dir', NETLOGO_HOME)

            if sys.platform=='darwin':
                jpype.java.lang.System.setProperty("java.awt.headless", "true");            
            
            debug("JVM started")
        
        link = jpype.JClass(netlogo_class[NETLOGO_VERSION])
        debug('NetLogoLink class found')

        if sys.platform == 'darwin' and gui:
            info('on mac only Headless mode is supported')
            gui=False
        
        self.link = link(jpype.java.lang.Boolean(gui),jpype.java.lang.Boolean(thd))
        debug('NetLogoLink class instantiated')
        
            
    def load_model(self, path):
        '''
        
        load a netlogo model.
        
        :param path: the absolute path to the netlogo model
        :raise: IOError in case the  model is not found
        :raise: NetLogoException wrapped arround netlogo exceptions. 
        
        '''
        try:
            self.link.loadModel(path)
        except jpype.JException(jpype.java.io.IOException)as ex:
            raise IOError(ex.message())
        except jpype.JException(jpype.java.org.nlogo.api.LogoException) as ex:
            raise NetLogoException(ex.message())
        except jpype.JException(jpype.java.org.nlogo.api.CompilerException) as ex:
            raise NetLogoException(ex.message())
        except jpype.JException(jpype.java.org.nlogo.core.CompilerException) as ex:
            raise NetLogoException(ex.message())
        except jpype.JException(jpype.java.lang.InterruptedException) as ex:
            raise NetLogoException(ex.message())
        

    def kill_workspace(self):
        '''
        
        close netlogo and shut down the jvm
        
        '''
        
        self.link.killWorkspace()

        
    def command(self, netlogo_command):
        '''
        
        Execute the supplied command in netlogo
        
        :param netlogo_command: a string with a valid netlogo command
        :raises: NetLogoException in case of either a LogoException or 
                CompilerException being raised by netlogo.
        
        '''
        
        try:
            self.link.command(netlogo_command)
        except jpype.JException(jpype.java.org.nlogo.api.LogoException) as ex:
            raise NetLogoException(ex.message())
        except jpype.JException(jpype.java.org.nlogo.api.CompilerException) as ex:
            raise NetLogoException(ex.message())
        except jpype.JException(jpype.java.org.nlogo.core.CompilerException) as ex:
            raise NetLogoException(ex.message())   
        except jpype.JException(jpype.java.org.nlogo.nvm.EngineException) as ex:
            raise NetLogoException(ex.message())

    def report(self, netlogo_reporter):
        '''
        
        Every reporter (commands which return a value) that can be called in 
        the NetLogo Command Center can be called with this method.
        
        :param netlogo_reporter: a valid netlogo reporter 
        :raises: NetlogoException
        
        '''
        
        try:
            result = self.link.report(netlogo_reporter)
            return self._cast_results(result)
        except jpype.JException(jpype.java.org.nlogo.api.LogoException) as ex:
            raise NetLogoException(ex.message())
        except jpype.JException(jpype.java.org.nlogo.api.CompilerException) as ex:
            raise NetLogoException(ex.message()) 
        except jpype.JException(jpype.java.org.nlogo.core.CompilerException) as ex:
            raise NetLogoException(ex.message())    
        except jpype.JException(jpype.java.lang.Exception) as ex:
            raise NetLogoException(ex.message()) 


    def _cast_results(self, results):
        '''
        
        Convert the results to the proper Python data type. The NLResults
        object knows its data type and has converter methods for each.
        
        :param results; the results from report
        :returns: a correct Python version of the results
        
        '''
        
        java_dtype = results.type
        
        if java_dtype == "Boolean":
            results = results.getResultAsBoolean()
            if results == 1:
                return True
            else:
                return False
        elif java_dtype == "String":
            return results.getResultAsString()       
        elif java_dtype == "Integer":
            return results.getResultAsInteger()
        elif java_dtype == "Double":
            return results.getResultAsDouble()
        elif java_dtype == "BoolList":
            results = results.getResultAsBooleanArray()
            
            tr = []
            for entry in results:
                if entry == 1:
                    tr.append(True)
                else:
                    tr.append(False)
            return tr
        elif java_dtype == "StringList":
            return results.getResultAsStringArray()   
        elif java_dtype == "IntegerList":
            return results.getResultAsIntegerArray() 
        elif java_dtype == "DoubleList":
            return results.getResultAsDoubleArray() 
        else:
            raise NetLogoException("unknown datatype")