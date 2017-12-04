Installation
============

pyNetLogo requires the numpy, scipy and pandas packages, which are included in most scientific Python distributions. The module has been tested using the Continuum Anaconda 2.7 and 3.6 distributions.

In addition, pyNetLogo depends on `JPype <https://jpype.readthedocs.io/en/latest/>`_. Please
follow the instructions provided there to install JPype; the conda package manager usually provides the easiest option.

pyNetLogo can be installed using the pip package manager, with the following command from a terminal:

	``pip install pynetlogo``

By default, pyNetLogo and Jpype will attempt to automatically identify the NetLogo version and installation directory, as well as the Java home directory. In case of issues (e.g. if NetLogo was installed in a different directory, or if the Java path is not found on a Mac), these parameters can be passed directly to the NetLogoLink class as described in the module documentation.

Known bugs and limitations
--------------------------
-	On a Mac, only headless mode (without GUI) is supported.
-	pyNetLogo can be used to control NetLogo from within Python. Calling Python
	from within NetLogo is not supported by this library. However, this can be achieved
	using the `Python extension for NetLogo <https://github.com/qiemem/PythonExtension>`_.
-	See `JPype limitations <https://jpype.readthedocs.io/en/latest/install.html#known-bugs-limitations>`_ 
	for additional limitations 
-	Mixing 32-bit and 64-bit versions of Java, Python, and NetLogo will crash
	Python. 