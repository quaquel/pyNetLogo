Installation
============

pynetlogo requires the NumPy, SciPy and pandas packages, which are
included in most scientific Python distributions.

In addition, pynetlogo depends on `jpype <https://jpype.readthedocs.io/en/latest/>`_.
When installing pynetlogo, jpype will be installed as well. However,
if you want to have full control over how jpype is installed, check
their installation details and install jpype before installing
pynetlogo.

pyNetLogo can be installed using the pip package manager, with the 
following command from a terminal:

	``pip install pynetlogo``

By default, pynetlogo and jpype will attempt to automatically identify
the NetLogo version and installation directory on Mac or Windows, as well
as the Java home directory. On Linux, or in case of issues (e.g. if NetLogo 
was installed in a different directory, or if the Java path is not found on a 
Mac), these parameters can be passed directly to the NetLogoLink class as 
described in the module documentation.

Known bugs and limitations
--------------------------
-	On a Mac, only headless mode (without GUI) is supported.
-	pynetlogo can be used to control NetLogo from within Python. Calling Python
	from within NetLogo is not supported by this library. However, this can be achieved
	using the `Python extension for NetLogo <https://github.com/qiemem/PythonExtension>`_.
-	See `jpype limitations <https://jpype.readthedocs.io/en/latest/install.html#known-bugs-limitations>`_
	for additional limitations. 
-	Mixing 32-bit and 64-bit versions of Java, Python, and NetLogo will 
	crash Python.
-   on M1 macs, your java architecture must match your python architecture. So you cannot use
    AArch64 (ARM) java with an x64 python install or the other way around. Use `jvm_path` to
    control which jvm pynetlogo will use.