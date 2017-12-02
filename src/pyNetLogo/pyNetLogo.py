"""
To do: check Mac support and handling of custom directories

"""

from __future__ import unicode_literals, absolute_import
import os
import re
import sys

import logging
from logging import Handler, DEBUG, INFO

import numpy as np
import pandas as pd
import jpype


__all__ = ['NetLogoException',
           'NetLogoLink']
    
PYNETLOGO_HOME = os.path.dirname(os.path.abspath(__file__))

#Jar supports NetLogo 5.2 or 6.0
module_name = {'5':'netlogoLink_v52.NetLogoLink',
               '6':'netlogoLink_v6.NetLogoLink'}
jar_sep ={'win32':';',
          'darwin':':'}

_logger = None
LOGGER_NAME = "EMA"
DEFAULT_LEVEL = DEBUG
INFO = INFO

def find_netlogo(path):
    """Find the most recent version of NetLogo in the specified directory
    
    Parameters
    ----------
    path : str
        Path to the root programs directory

    Returns
    -------    
    str
        Path to the most recent NetLogo installation directory (assuming
        default NetLogo directory names)

    Raises
    ------
    IndexError
        If no NetLogo version is found in path
    
    """
    
    path = os.path.abspath(path)
    netlogo_versions = [entry for entry in os.listdir(path) if 'netlogo' in 
                        entry.lower()]
    
    # sort handles version numbers properly as long as pattern of 
    # directory name is not changed
    netlogo_versions.sort(reverse=True)
    
    return netlogo_versions[0]


def find_jars(path):
    """Find all jar files in directory and return as list
    
    Parameters
    ----------
    path : str
        Path in which to find jar files
    
    Returns
    -------    
    str
        List of jar files

    """
    
    jars = []
    for root, _, files in os.walk(path):
        for file in files:  # @ReservedAssignment
            if file.endswith(".jar"):
                jars.append(os.path.join(root, file))
    return jars


def establish_netlogoversion(path):
    # TODO: python3 compliance
    pattern = re.compile(r'(?:(\d+)\.)?(?:(\d+)\.)?(\*|\d+)$')
    
    netlogo = os.path.basename(os.path.normpath(path))
    match = pattern.search(netlogo)
    version = match.group()
    
    main_version = version[0]

    return main_version


def find_netlogo_windows():
    netlogo = None
    if os.environ['PROGRAMW6432']:
        paths = [os.environ['PROGRAMFILES(X86)'],
                 os.environ['PROGRAMW6432']] 
        for path in paths:
            try:
                netlogo = find_netlogo(path)
            except IndexError:
                pass
            else:
                netlogo = os.path.join(path, netlogo)
    else:
        path = os.environ['PROGRAMFILES']
        try:
            netlogo = find_netlogo(path)
        except IndexError:
            pass
        else:
            netlogo = os.path.join(path, netlogo)
    
    return netlogo


def find_netlogo_mac():
    paths = ['/Applications', 
             os.path.join(os.getenv('HOME'), 'Applications')]
    netlogo = None
    for path in paths:
        try:
            netlogo = find_netlogo(path)
        except IndexError:
            pass
        else:
            netlogo = os.path.join(path, netlogo)
        
    return netlogo


def find_netlogo_linux():
    raise NotImplementedError

def get_netlogo_home():
    if sys.platform=='win32':
        netlogo_home = find_netlogo_windows()
    elif sys.platform=='darwin':
        netlogo_home = find_netlogo_mac()
    else:
        netlogo_home = find_netlogo_linux()
        
    return netlogo_home
    

class NetLogoException(Exception):
    """Basic project exception

    """
    
    pass

    
class NetLogoLink(object):
    """Create a link with NetLogo. Underneath, the NetLogo JVM is started through Jpype.
    
    If `netlogo_home`, `netlogo_version`, or `jvm_home` are not provided, the link
    will try to identify the correct parameters automatically.

    Parameters
    ----------
    gui : bool, optional
        If true, displays the NetLogo GUI (not supported on Mac)
    thd : bool, optional
        If true, use NetLogo 3D
    netlogo_home : str, optional
        Path to the NetLogo installation directory
    netlogo_version : {'6','5'}, optional
        Used to choose appropriate command syntax for the link methods
    jvm_home : str, optional
        Java home directory for Jpype

    """

    def __init__(self, gui=False, thd=False, netlogo_home=None, 
                 netlogo_version=None, jvm_home=None):

        if not netlogo_home:
            netlogo_home = get_netlogo_home()
        if not netlogo_version:
            netlogo_version = establish_netlogoversion(netlogo_home)
        if not jvm_home:
            jvm_home = jpype.getDefaultJVMPath()

        self.netlogo_home = netlogo_home
        self.netlogo_version = netlogo_version
        self.jvm_home = jvm_home
        
        if not jpype.isJVMStarted():
            jars = find_jars(netlogo_home)
            jars.append(os.path.join(PYNETLOGO_HOME, 'java', 'netlogoLink_combined.jar'))     
            joined_jars = jar_sep[sys.platform].join(jars)
            jarpath = '-Djava.class.path={}'.format(joined_jars)
            try:
                jpype.startJVM(jvm_home, jarpath)
            except RuntimeError as e:
                raise e

            #Causes problems with 6.0?
            #jpype.java.lang.System.setProperty('user.dir', netlogo_home)

            if sys.platform=='darwin':
                jpype.java.lang.System.setProperty("java.awt.headless", "true");
    
        link = jpype.JClass(module_name[self.netlogo_version])

        if sys.platform == 'darwin' and gui:
            #info('on mac only Headless mode is supported')
            gui=False
        
        self.link = link(jpype.java.lang.Boolean(gui),jpype.java.lang.Boolean(thd))
        
            
    def load_model(self, path):
        """Load a NetLogo model.
        
        Parameters
        ----------
        path : str
            Path to the NetLogo model

        Raises
        ------
        IOError
            In case the model is not found
        NetLogoException
            In case of a NetLogo exception
        
        """

        try:
            self.link.loadModel(path)
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())


    def kill_workspace(self):
        """Close NetLogo and shut down the JVM.
        
        """
        
        self.link.killWorkspace()
        
        
    def command(self, netlogo_command):
        """Execute the supplied command in NetLogo
        
        Parameters
        ----------
        netlogo_command : str
            Valid NetLogo command

        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo
        
        """
        
        try:
            self.link.command(netlogo_command)
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())

            
    def report(self, netlogo_reporter):
        """Return values from a NetLogo reporter

        Any reporter (command which returns a value) that can be called
        in the NetLogo Command Center can be called with this method.
        
        Parameters
        ----------
        netlogo_reporter : str
            Valid NetLogo reporter 

        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo   

        """
        
        try:
            result = self.link.report(netlogo_reporter)
            return self._cast_results(result)
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())
        
        
    def patch_report(self, attribute):
        """Return patch attributes from NetLogo

        Returns a pandas DataFrame with same dimensions as the NetLogo world,
        with column labels and row indices following pxcor and pycor patch
        coordinates. Values of the dataframe correspond to patch attributes.
        
        Parameters
        ----------
        attribute : str
            Valid NetLogo patch attribute 
        
        Returns
        -------
        pandas DataFrame
            DataFrame containing patch attributes
        
        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo        

        """

        try:
            extents = self.link.report('(list min-pxcor max-pxcor min-pycor max-pycor)')
            extents = self._cast_results(extents).astype(int)

            results_df = pd.DataFrame(index=range(extents[2],extents[3]+1,1),
                                      columns=range(extents[0],extents[1]+1,1))
            results_df.sort_index(ascending=False, inplace=True)
            if self.netlogo_version == '6':
                resultsvec = self.link.report('map [[?1] -> [{0}] of ?1] sort patches'.format(attribute))
            else:
                resultsvec = self.link.report('map [[{0}] of ?] sort patches'.format(attribute))
            resultsvec = self._cast_results(resultsvec)
            results_df.ix[:,:] = resultsvec.reshape(results_df.shape)
            
            return results_df
            
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())
            
    
    def patch_set(self, attribute, data):
        """Set patch attributes in NetLogo

        Inverse of the `patch_report` method. Sets a patch attribute using values
        from a pandas DataFrame with the same dimensions as the NetLogo world.
        
        Parameters
        ----------
        attribute : str
            Valid NetLogo patch attribute
        data : Pandas DataFrame
            DataFrame with same dimensions as NetLogo world

        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo        
        
        """
    
        try:
            np.set_printoptions(threshold = np.prod(data.shape))
            datalist = '['+str(data.as_matrix().flatten()).strip('[ ')
            datalist = ' '.join(datalist.split())
            if self.netlogo_version == '6':
                command = '(foreach map [[?1] -> [pxcor] of ?1] sort patches map [[?2] -> [pycor] of ?2] \
                            sort patches {0} [[?1 ?2 ?3 ] -> ask patch ?1 ?2 [set {1} ?3]])'.format(datalist, attribute)
            else:
                command = '(foreach map [[pxcor] of ?] sort patches map [[pycor] of ?] \
                            sort patches {0} [ask patch ?1 ?2 [set {1} ?3]])'.format(datalist, attribute)

            self.link.command(command)
            
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())
        
        
    def repeat_command(self, netlogo_command, reps):
        """Execute the supplied command in NetLogo a given number of times
        
        Parameters
        ----------
        netlogo_command : str
            Valid NetLogo command
        reps : int
            Number of repetitions for which to repeat commands
        
        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo 
        
        """
    
        try:
            commandstr = 'repeat {0} [{1}]'.format(reps, netlogo_command)
            self.link.command(commandstr)
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())
        

    def repeat_report(self, netlogo_reporter, reps):
        """Return values from a NetLogo reporter over a number of ticks.

        Assumes the model can be run using the default `go` command.
        Can be used with multiple reporters by passing a list of strings.
        
        Parameters
        ----------
        netlogo_reporter : str or list of str
            Valid NetLogo reporter(s)
        reps : int
            Number of NetLogo ticks for which to return values

        Returns
        -------
        pandas DataFrame
            DataFrame of reported values indexed by ticks, with columns
            for each reporter

        Raises
        ------
        NetLogoException
            If reporters are not in a valid format, or if a LogoException
            or CompilerException is raised by NetLogo 
        
        """
        
        if isinstance(netlogo_reporter, str):
            cols = [netlogo_reporter]
        elif isinstance(netlogo_reporter, list):
            cols = netlogo_reporter   
        else:
            raise NetLogoException("Unknown datatype")
        
        results_df = pd.DataFrame(columns=cols)
        
        for _ in range(reps):    
            tick = self._cast_results(self.link.report('ticks'))
            for reporter in results_df.columns:
                try:
                    result = self.link.report(reporter)
                    results_df.loc[tick, reporter] = self._cast_results(result)
                except jpype.JavaException as ex :
                    raise NetLogoException(ex.message())

            
            self.link.command('go')
                
        return results_df


    def write_NetLogo_attriblist(self, agent_data, agent_name):
        """Update attributes of a set of NetLogo agents from a DataFrame

        Assumes a set of NetLogo agents of the same type. Attribute values
        can be numerical or strings.
        
        Parameters
        ----------
        agent_data : pandas DataFrame
            DataFrame indexed with a row for each agent, and columns for
            each attribute to update. Requires a 'who' column for the
            NetLogo agent ID
        agent_name : str
            Name of the NetLogo agent type to update (singular, e.g. a-sheep)
        
        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo 
        
        """

        try:
            #Get list of agent IDs to update, and convert to a Python string to pass to NetLogo
            whostr = ' '.join(map(str, agent_data['who']))

            #Name of NetLogo agent attributes to update
            attribs_to_update = [str(i) for i in agent_data.columns if i != 'who']

            #Convert the agent data to Python lists, then to strings to pass to NetLogo
            attribstr = []
            for attrib in attribs_to_update:
                #Check if we have string or numerical data and format values accordingly
                if (agent_data[attrib].dtype == object):
                    values = ' '.join(map(lambda x: '"{0}"'.format(x), list(agent_data[attrib])))
                else:
                    values = ' '.join(map(str, list(agent_data[attrib]))) 
                #Then format the values string to look like a NetLogo list
                liststr=['[{0}]'.format(values)]
                attribstr.append(''.join(liststr))
                
            #Join the strings for all the attributes
            attribstr = ' '.join(attribstr)

            #Set up the "foreach" NetLogo command string
            askstr = []
            setstr = []
            for i, attrib_name in enumerate(attribs_to_update):
                askstr.extend(('?{0} '.format(i+2)))
                setstr.extend(('set {0} ?{1} '.format(attrib_name, i+2)))
            askstr = ''.join(askstr)
            setstr = ''.join(setstr)

            if self.netlogo_version == '6':
                commandstr = ['(foreach [{0}] {1} [ [?1 {2}] -> ask {3} ?1 [{4}]])'.format(whostr, attribstr, askstr,
                                                                                           agent_name, setstr)]
            elif self.netlogo_version == '5':
                commandstr = ['(foreach [{0}] {1} [ask {2} ?1 [{3}]])'].format(whostr, attribstr, agent_name, setstr)
                
            commandstr = ''.join(commandstr)
            
            self.link.command(commandstr)
            
        except jpype.JavaException as ex :
            raise NetLogoException(ex.message())



    def _cast_results(self, results):
        """Convert results to the proper python data type. The NLResults
        object knows its datatype and has converter methods for each.
        
        Parameters
        ----------
        results : bool, str, int, double, boollist, stringlist, integerlist, doublelist
        
        Returns
        -------
        Corresponding python version of the results
        
        """
        
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
            return np.array(results.getResultAsDoubleArray())
        else:
            raise NetLogoException("Unknown datatype")