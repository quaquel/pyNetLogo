"""


"""
import jpype
import jpype.imports
import numpy as np
import os
import pandas as pd
import re
import string
import sys
import tempfile
import warnings
from logging import DEBUG, INFO

__all__ = ["NetLogoLink", "NetLogoException"]

PYNETLOGO_HOME = os.path.dirname(os.path.abspath(__file__))


_logger = None
LOGGER_NAME = "EMA"
DEFAULT_LEVEL = DEBUG
INFO = INFO

valid_chars = "[]-_.() {}{}".format(string.ascii_letters, string.digits)


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
    netlogo_versions = [entry for entry in os.listdir(path) if "netlogo" in entry.lower()]

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
            if file == "NetLogo.jar":
                jars.insert(0, os.path.join(root, file))
            elif file.endswith(".jar"):
                jars.append(os.path.join(root, file))

    return jars


def find_netlogo_windows():
    netlogo = None
    if os.environ["PROGRAMW6432"]:
        paths = [os.environ["PROGRAMFILES(X86)"], os.environ["PROGRAMW6432"]]
        for path in paths:
            try:
                netlogo = find_netlogo(path)
            except IndexError:
                pass
            else:
                netlogo = os.path.join(path, netlogo)
    else:
        path = os.environ["PROGRAMFILES"]
        try:
            netlogo = find_netlogo(path)
        except IndexError:
            pass
        else:
            netlogo = os.path.join(path, netlogo)

    return netlogo


def find_netlogo_mac():
    paths = ["/Applications", os.path.join(os.getenv("HOME"), "Applications")]
    netlogo = None
    for path in paths:
        try:
            netlogo = find_netlogo(path)
        except IndexError:
            pass
        except OSError:
            pass
        else:
            netlogo = os.path.join(path, netlogo)

    return netlogo


def find_netlogo_linux():
    raise NotImplementedError(
        ("NetLogoLink requires the netlogo_home on Linux")
    )


def get_netlogo_home():
    if sys.platform == "win32":
        netlogo_home = find_netlogo_windows()
    elif sys.platform == "darwin":
        netlogo_home = find_netlogo_mac()
    else:
        netlogo_home = find_netlogo_linux()

    return netlogo_home


class NetLogoException(Exception):
    """Base project exception"""

    pass


class NetLogoLink:
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
    jvm_path : str, optional
        path of the jvm
    jvmargs : list of str, optional
              additional arguments that should be used when starting
              the jvm

    """

    def __init__(
        self,
        gui=False,
        thd=False,
        netlogo_home=None,
        jvm_path=None,
        jvmargs=[],
    ):

        if netlogo_home is None:
            netlogo_home = get_netlogo_home()

            if netlogo_home is None:
                warnings.warn("netlogo home not found")
        if not jvm_path:
            jvm_path = jpype.getDefaultJVMPath()

        self.netlogo_home = netlogo_home
        self.jvm_home = jvm_path

        if not jpype.isJVMStarted():
            jars = find_jars(netlogo_home)
            jars.append(os.path.join(PYNETLOGO_HOME, "java", "netlogolink.jar"))

            try:
                jpype.startJVM(*jvmargs, jvmpath=jvm_path, classpath=jars)
            except RuntimeError as e:
                raise e

        # enable extensions
        for path, dirs, files in os.walk(self.netlogo_home):
            if "extensions" in dirs:
                exts = os.path.join(self.netlogo_home, "extensions")
                jpype.java.lang.System.setProperty("netlogo.extensions.dir", exts)
                break
        else:
            warnings.warn(
                (
                    "could not find default NetLogo "
                    "extensions folder. Extensions not "
                    "available"
                )
            )

        if sys.platform == "darwin":
            jpype.java.lang.System.setProperty("java.awt.headless", "true")
            gui = False
        if not gui:
            jpype.java.lang.System.setProperty("org.nlogo.preferHeadless", "true")

        from netLogoLink import NetLogoLink
        self.link = NetLogoLink(jpype.java.lang.Boolean(gui), jpype.java.lang.Boolean(thd))

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
        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

    def kill_workspace(self):
        """Close NetLogo and shut down the JVM."""

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
        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

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
        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

    def report_while(self, netlogo_reporter, condition, command="go", max_seconds=10):
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
            result = self.link.doReportWhile(
                command,
                netlogo_reporter,
                condition,
                jpype.java.lang.Integer(max_seconds),
            )
            return self._cast_results(result)
        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

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
            extents = self.link.report(
                "(list min-pxcor max-pxcor \
                                         min-pycor max-pycor)"
            )
            extents = self._cast_results(extents).astype(int)
            shape = (extents[3] - extents[2] + 1, extents[1] - extents[0] + 1)

            resultsvec = self.link.report(
                "map [p -> [{0}] of p] \
                                           sort patches".format(
                    attribute
                )
            )
            resultsvec = self._cast_results(resultsvec)
            results_df = pd.DataFrame(
                resultsvec.reshape(shape),
                index=reversed(range(extents[2], extents[3] + 1, 1)),
                columns=range(extents[0], extents[1] + 1, 1),
            )

            return results_df

        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

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
            datalist = "[" + str(data.values.flatten()).strip("[ ")
            datalist = " ".join(datalist.split())

            command = "(foreach map [px -> [pxcor] of px] \
                        sort patches map [py -> [pycor] of py] \
                        sort patches {0} [[px py p ] -> ask patch px py \
                        [set {1} p]])".format(
                datalist, attribute
            )

            self.link.command(command)

        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

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
            commandstr = "repeat {0} [{1}]".format(reps, netlogo_command)
            self.link.command(commandstr)
        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

    def repeat_report(self, netlogo_reporter, reps, go="go", include_t0=True):
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
         include_t0 : boolean, optional
             include the value of the reporter at t0, prior to running the
             go command

         Returns
         -------
        dict
             key is the reporter, and the value is a list order by ticks

         Raises
         ------
         NetLogoException
             If reporters are not in a valid format, or if a LogoException
             or CompilerException is raised by NetLogo

         Notes
         -----
         This method relies on files to send results from netlogo back to
         Python. This is slow and can break when used at scale. For such
         use cases, you are better of using a model specific way of interfacing.
         For example, have a go routine which accumulates the relevant
         reporters into lists. First run the model for the required time steps
         using command, and next retrieve the lists through report.

        """

        if isinstance(netlogo_reporter, str):
            cols = [netlogo_reporter]
        elif isinstance(netlogo_reporter, list):
            cols = netlogo_reporter
        else:
            raise NetLogoException("Unknown datatype")

        tick = self._cast_results(self.link.report("ticks"))

        if include_t0:
            index = np.arange(tick, tick + reps + 1)
        else:
            index = np.arange(tick, tick + reps)

        prefix = "".join([os.getcwd(), os.sep])
        tempfolder = tempfile.mkdtemp(prefix=prefix)

        # TODO move to tempfile and keep track of variable tempfile mapping
        # TODO issue #55
        commands = []
        fns = {}
        for variable in cols:
            fh, fn = tempfile.mkstemp(suffix=".txt", dir=tempfolder)
            os.close(fh) #immediately free up file handle for re-use
            fns[variable] = fn
            fn = '"{}"'.format(fn)
            fn = fn.replace(os.sep, "/")

            nc = r"{0} {1} {2} {3}".format("file-open", fn, "file-write", variable)
            commands.append(nc)

        c_start = "repeat {} [ {}".format(reps, go)
        c_close = "] file-close-all"
        c_write = " ".join(commands)

        if include_t0:
            command = " ".join((c_write, c_start, c_write, c_close))
        else:
            command = " ".join((c_start, c_write, c_close))

        self.command(command)

        results = {}
        for key, value in fns.items():
            with open(value) as fh:
                result = fh.readline()
                result = result.strip()

                # Check if the NetLogo reporter returns a list
                list_res = re.findall(r"\[([^]]*)\]", result)
                if list_res:
                    try:
                        # Try a numerical data type
                        result = [np.array(e.split(), dtype=float) for e in list_res]
                    except ValueError:
                        # Otherwise, assume the reporter returns string values
                        result = [np.array([b.strip('"') for b in e.split()]) for e in list_res]
                else:
                    try:
                        result = np.array([float(entry) for entry in result.split()])
                    except ValueError:
                        result = np.array([entry.strip('"') for entry in result.split()])

                results[key] = result
        
        # cleanup temp files and folders
        for key, value in fns.items():
             os.remove(value) #delete file by name

        os.rmdir(tempfolder) #remove folder

        return results

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
            whostr = " ".join(map(str, agent_data["who"]))

            # Name of NetLogo agent attributes to update
            attribs_to_update = [str(i) for i in agent_data.columns if i != "who"]

            # Convert agent data to Python lists, then to strings for NetLogo
            attribstr = []
            for attrib in attribs_to_update:
                # Check if string or numerical data and format accordingly
                if agent_data[attrib].dtype == object:
                    values = " ".join(map(lambda x: '"{0}"'.format(x), list(agent_data[attrib])))
                else:
                    values = " ".join(map(str, list(agent_data[attrib])))
                # Then format the values string to look like a NetLogo list
                liststr = ["[{0}]".format(values)]
                attribstr.append("".join(liststr))

            # Join the strings for all the attributes
            attribstr = " ".join(attribstr)

            # Set up the "foreach" NetLogo command string
            askstr = []
            setstr = []
            for i, attrib_name in enumerate(attribs_to_update):
                askstr.extend(("?{0} ".format(i + 2)))
                setstr.extend(("set {0} ?{1} ".format(attrib_name, i + 2)))
            askstr = "".join(askstr)
            setstr = "".join(setstr)

            commandstr = [
                "(foreach [{0}] {1} [ [?1 {2}] \
                           -> ask {3} ?1 [{4}]])".format(
                    whostr, attribstr, askstr, agent_name, setstr
                )
            ]
            commandstr = "".join(commandstr)

            self.link.command(commandstr)

        except jpype.JException as ex:
            print(ex.stacktrace())
            raise NetLogoException(str(ex))

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
        except AttributeError:
            converted_results = []
            for entry in results:
                converted_results.append(self._cast_results(entry))

        return converted_results


def type_convert(results):
    """Helper function for converting from Java datatypes to
    Python datatypes"""

    java_dtype = str(results.getType())

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
    elif java_dtype == "NestedList":
        result = results.getResultAsObject()
        value = []
        for entry in result:
            value.append(type_convert(entry))
        return np.asarray(value)
    else:
        raise NetLogoException("Unknown datatype: {}".format(java_dtype))
