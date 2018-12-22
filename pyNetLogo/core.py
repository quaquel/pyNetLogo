"""


"""

from __future__ import unicode_literals, absolute_import
import os
import re
import tempfile
import string
import sys


from logging import DEBUG, INFO

import numpy as np
import pandas as pd
import jpype
import warnings


__all__ = ['NetLogoLink',
           'NetLogoException']

PYNETLOGO_HOME = os.path.dirname(os.path.abspath(__file__))

# Jar supports NetLogo 5.x or 6.0
module_name = {'5': 'NetLogoLinkV5.NetLogoLink',
               '6': 'NetLogoLinkV6.NetLogoLink'}

_logger = None
LOGGER_NAME = "EMA"
DEFAULT_LEVEL = DEBUG
INFO = INFO

valid_chars = '[]-_.() {}{}'.format(string.ascii_letters, string.digits)

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
            if file == 'NetLogo.jar':
                jars.insert(0, os.path.join(root, file))
            elif file.endswith(".jar"):
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
    raise NotImplementedError(('NetLogoLink requires the netlogo_home '
                               'and netlogo_version parameters on Linux'))


def get_netlogo_home():
    if sys.platform == 'win32':
        netlogo_home = find_netlogo_windows()
    elif sys.platform == 'darwin':
        netlogo_home = find_netlogo_mac()
    else:
        netlogo_home = find_netlogo_linux()

    return netlogo_home


class NetLogoException(Exception):
    """Basic project exception

    """

    pass


class NetLogoLink(object):
    """Create a link with NetLogo. Underneath, the NetLogo JVM
    is started through Jpype.

    If `netlogo_home`, `netlogo_version`, or `jvm_home` are not provided,
    the link will try to identify the correct parameters automatically on Mac
    or Windows. `netlogo_home` and `netlogo_version` are required on Linux.

    Parameters
    ----------
    gui : bool, optional
        If true, displays the NetLogo GUI (not supported on Mac)
    thd : bool, optional
        If true, use NetLogo 3D
    netlogo_home : str, optional
        Path to the NetLogo installation directory (required on Linux)
    netlogo_version : {'6','5'}, optional
        Used to choose command syntax for link methods (required on Linux)
    jvm_home : str, optional
        Java home directory for Jpype
    jvmargs : list of str, optional
              additional arguments that should be used when starting
              the jvm

    """

    def __init__(self, gui=False, thd=False, netlogo_home=None,
                 netlogo_version=None, jvm_home=None,
                 jvmargs=[]):

        if not netlogo_home:
            netlogo_home = get_netlogo_home()
        if not netlogo_version:
            netlogo_version = establish_netlogoversion(netlogo_home)
        if not jvm_home:
            jvm_home = jpype.getDefaultJVMPath()

        self.netlogo_home = netlogo_home
        self.netlogo_version = netlogo_version
        self.jvm_home = jvm_home

        if sys.platform == 'win32':
            jar_sep = ';'
        else:
            jar_sep = ':'

        if not jpype.isJVMStarted():
            jars = find_jars(netlogo_home)
            jars.append(os.path.join(PYNETLOGO_HOME,
                                     'java', 'netlogolink.jar'))
            joined_jars = jar_sep.join(jars)
            jarpath = '-Djava.class.path={}'.format(joined_jars)

            jvm_args = [jarpath, ] + jvmargs

            try:
                jpype.startJVM(jvm_home, *jvm_args)
            except RuntimeError as e:
                raise e
            
            # enable extensions
            if sys.platform == 'darwin':
                exts = os.path.join(netlogo_home, 'extensions')
            elif sys.platform == 'win32':
                exts = os.path.join(netlogo_home, 'app', 'extensions')        
            else:
                exts = os.path.join(netlogo_home, 'app', 'extensions')        

            # check if default extension folder exists, raise
            # a warning otherwise
            if os.path.exists(exts):
                jpype.java.lang.System.setProperty('netlogo.extensions.dir',
                                               exts)
            else:
                warnings.warn(('could not find default NetLogo ',
                               'extensions folder. Extensions not ',
                               'available'))
                
            
            if sys.platform == 'darwin':
                jpype.java.lang.System.setProperty('java.awt.headless',
                                                   'true')

        link = jpype.JClass(module_name[self.netlogo_version])

        if sys.platform == 'darwin' and gui:
            gui = False

        self.link = link(jpype.java.lang.Boolean(gui),
                         jpype.java.lang.Boolean(thd))

    def load_model(self, path):
        """Load a NetLogo model.

        Parameters
        ----------
        path : str
            Path to the NetLogo model

        Raises
        ------
        FileNotFoundError
            in case path does not exist
        NetLogoException
            In case of a NetLogo exception

        """
        if not os.path.isfile(path):
            raise FileNotFoundError()

        try:
            self.link.loadModel(path)
        except jpype.JavaException as ex:
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
        except jpype.JavaException as ex:
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
        except jpype.JavaException as ex:
            raise NetLogoException(ex.message())

    def report_while(self, netlogo_reporter, condition, command='go', max_seconds=0):
        """Return values from a NetLogo reporter while a condition is true
        in the NetLogo model

        Parameters
        ----------
        netlogo_reporter : str
            Valid NetLogo reporter
        condition: str
            Valid boolean NetLogo reporter
        command: str
            NetLogo command used to execute the model
        max_seconds: int, optional
            Time limit used to break execution

        Raises
        ------
        NetLogoException
            If a LogoException or CompilerException is raised by NetLogo

        """

        try:
            result = self.link.doReportWhile(command, netlogo_reporter, condition, max_seconds)
            return self._cast_results(result)
        except jpype.JavaException as ex:
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
            extents = self.link.report('(list min-pxcor max-pxcor \
                                         min-pycor max-pycor)')
            extents = self._cast_results(extents).astype(int)

            results_df = pd.DataFrame(index=range(extents[2],
                                                  extents[3]+1, 1),
                                      columns=range(extents[0],
                                                    extents[1]+1, 1))
            results_df.sort_index(ascending=False, inplace=True)
            if self.netlogo_version == '6':
                resultsvec = self.link.report('map [p -> [{0}] of p] \
                                               sort patches'.format(attribute))
            else:
                resultsvec = self.link.report('map [[{0}] of ?] \
                                               sort patches'.format(attribute))
            resultsvec = self._cast_results(resultsvec)
            results_df.ix[:, :] = resultsvec.reshape(results_df.shape)

            return results_df

        except jpype.JavaException as ex:
            raise NetLogoException(ex.message())

    def patch_set(self, attribute, data):
        """Set patch attributes in NetLogo

        Inverse of the `patch_report` method. Sets a patch attribute using
        values from a pandas DataFrame of same dimensions as the NetLogo world.

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
            np.set_printoptions(threshold=np.prod(data.shape))
            datalist = '['+str(data.values.flatten()).strip('[ ')
            datalist = ' '.join(datalist.split())
            if self.netlogo_version == '6':
                command = '(foreach map [px -> [pxcor] of px] \
                            sort patches map [py -> [pycor] of py] \
                            sort patches {0} [[px py p ] -> ask patch px py \
                            [set {1} p]])'.format(datalist, attribute)
            else:
                command = '(foreach map [[pxcor] of ?] \
                            sort patches map [[pycor] of ?] \
                            sort patches {0} [ask patch ?1 ?2 \
                            [set {1} ?3]])'.format(datalist, attribute)

            self.link.command(command)

        except jpype.JavaException as ex:
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
        except jpype.JavaException as ex:
            raise NetLogoException(ex.message())

    def repeat_report(self, netlogo_reporter, reps, go='go'):
        """Return values from a NetLogo reporter over a number of ticks.

        Can be used with multiple reporters by passing a list of strings.
        The values of the returned DataFrame are formatted following the
        data type returned by the reporters (numerical or string data,
        with single or multiple values). If the reporter returns multiple
        values, the results are converted to a numpy array.

        Parameters
        ----------
        netlogo_reporter : str or list of str
            Valid NetLogo reporter(s)
        reps : int
            Number of NetLogo ticks for which to return values
        go : str, optional
            NetLogo command for running the model ('go' by default)

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

        tick = self._cast_results(self.link.report('ticks'))
        results_df = pd.DataFrame(columns=cols,
                                  index=np.arange(tick, tick+reps))

        prefix = ''.join([os.getcwd(), os.sep])
        tempfolder = tempfile.mkdtemp(prefix=prefix)

        commands = []
        fns = {}
        for variable in cols:
            fn = r'{0}/{1}{2}'.format(tempfolder,
                                      variable,
                                      '.txt')
            fns[variable] = fn
            fn = '"{}"'.format(fn)
            fn = fn.replace(os.sep, '/')

            nc = r'{0} {1} {2} {3}'.format('file-open', fn,
                                           'file-write', variable)
            commands.append(nc)

        c_start = "repeat {} [".format(reps)
        c_close = "{} ]".format(go)
        c_middle = " ".join(commands)

        command = " ".join((c_start, c_middle, c_close))

        self.command(command)
        self.command("file-close-all")

        for key, value in fns.items():
            with open(value) as fh:
                result = fh.readline()
                result = result.strip()

                # Check if the NetLogo reporter returns a list
                list_res = re.findall(r'\[([^]]*)\]', result)
                if list_res:
                    try:
                        # Try a numerical data type
                        result = np.array([np.array(e.split(),
                                           dtype=np.float) for e in list_res])
                    except:
                        # Otherwise, assume the reporter returns string values
                        result = np.array([np.array([b.strip('"')
                                                     for b in e.split()])
                                           for e in list_res])
                else:
                    try:
                        result = np.array([float(entry)
                                           for entry in result.split()])
                    except:
                        result = np.array([entry.strip('"')
                                           for entry in result.split()])

                results_df.loc[:, key] = result

            os.remove(value)

        os.rmdir(tempfolder)

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
            # Get list of agent IDs to update, and convert to a Python string
            # to pass to NetLogo
            whostr = ' '.join(map(str, agent_data['who']))

            # Name of NetLogo agent attributes to update
            attribs_to_update = [str(i) for i in agent_data.columns
                                 if i != 'who']

            # Convert agent data to Python lists, then to strings for NetLogo
            attribstr = []
            for attrib in attribs_to_update:
                # Check if string or numerical data and format accordingly
                if (agent_data[attrib].dtype == object):
                    values = ' '.join(map(lambda x: '"{0}"'.format(x),
                                          list(agent_data[attrib])))
                else:
                    values = ' '.join(map(str, list(agent_data[attrib])))
                # Then format the values string to look like a NetLogo list
                liststr = ['[{0}]'.format(values)]
                attribstr.append(''.join(liststr))

            # Join the strings for all the attributes
            attribstr = ' '.join(attribstr)

            # Set up the "foreach" NetLogo command string
            askstr = []
            setstr = []
            for i, attrib_name in enumerate(attribs_to_update):
                askstr.extend(('?{0} '.format(i+2)))
                setstr.extend(('set {0} ?{1} '.format(attrib_name, i+2)))
            askstr = ''.join(askstr)
            setstr = ''.join(setstr)

            if self.netlogo_version == '6':
                commandstr = ['(foreach [{0}] {1} [ [?1 {2}] \
                               -> ask {3} ?1 [{4}]])'.format(whostr,
                                                             attribstr,
                                                             askstr,
                                                             agent_name,
                                                             setstr)]
            elif self.netlogo_version == '5':
                commandstr = ['(foreach [{0}] {1} \
                               [ask {2} ?1 [{3}]])'.format(whostr,
                                                           attribstr,
                                                           agent_name,
                                                           setstr)]

            commandstr = ''.join(commandstr)

            self.link.command(commandstr)

        except jpype.JavaException as ex:
            raise NetLogoException(ex.message())

    def _cast_results(self, results):
        """Convert results to the proper python data type. The NLResults
        object knows its datatype and has converter methods for each.

        Parameters
        ----------
        results : bool, str, int, double, boollist,
                  stringlist, integerlist, doublelist

        Returns
        -------
        Corresponding python version of the results

        """

        try:
            converted_results = type_convert(results)
        except:
            converted_results=[]
            for i in results:
                converted_results.append(type_convert(i))

        return converted_results


def type_convert(results):
    '''Helper function for converting from Java datatypes to
    Python datatypes'''

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
