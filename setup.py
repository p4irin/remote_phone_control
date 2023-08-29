"""setup.py shim

This setup.py is needed to work arround this error:
'
ERROR: File "setup.py" not found. Directory cannot be installed in editable
mode: /path/to/project/root/directory (A "pyproject.toml" file was found,
but editable mode currently requires a setup.py based build.)
'
This is due to a limitation in Setuptools support for PEP 660.
This shim delegates the job of doing an editable install to Setuptools’ legacy
mechanism until native support for PEP 660 is available.
"""

from setuptools import setup

setup()