Installation
============

advice to use anaconda

In the foreseeable future, PyNetLogo will becomes installable from pip

	pip install pynetlogo

pyNetLogo depends on `JPype <https://jpype.readthedocs.io/en/latest/>`_. Please
follow the instruction provided there to install JPype.

explain mac problem with jpype and java_home

something on autodiscovery netlogo and java

Known bugs and limitations
--------------------------
-	on a mac, only headless is supported.
-	pyNetLogo enables controlling NetLogo from within Python. Calling Python
	from within NetLogo is not supported by this library.
-	see `JPype limitations <https://jpype.readthedocs.io/en/latest/install.html#known-bugs-limitations>`_ 
	for additional limitations 
-	mixing 32 bit and 64 bit versions of java, Python, and NetLogo will crash
	Python. 