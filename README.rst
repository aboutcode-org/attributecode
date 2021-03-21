=============
AttributeCode
=============

Tool for Attribution Notice generation.

Read more about AttributeCode `here <https://nexb-attributecode.readthedocs-hosted.com/en/latest/>`_.

Features
========

- Accept data from multiple formats:
   - A spreadsheet file (csv or xlsx)
   - A JSON file format for Attribution that would have the primary Attribution fields
   - A ScanCode JSON file.
 
- A configuration option to map input data to Attribution output fields.

- Jinja templates to customize the Attribution Notice output.

- Access to a database of license texts based on ScanCode license keys.

Build and tests status
======================

+-------+-----------------+
|Branch | **Linux/macOS** |
+=======+=================+
|Master | |master-posix|  |
+-------+-----------------+
|Develop| |devel-posix|   |
+-------+-----------------+


REQUIREMENTS
------------
Python3.6

On Linux and Mac, Python is typically pre-installed. To verify which
version may be pre-installed, open a terminal and type:

    python --version

On Windows or Mac, you can download the latest Python here:
    https://www.python.org/downloads/

Download the .msi installer for Windows or the .dmg archive for Mac.
Open and run the installer using all the default options.


INSTALLATION
------------
Checkout the AttributeCode from:
    https://github.com/nexB/attributecode


Read the `setup process <https://nexb-attributecode.readthedocs-hosted.com/en/latest/setup.html>`_.


HELP and SUPPORT
----------------
If you have a question or find a bug, enter a ticket at:

    https://github.com/nexB/attributecode

For issues, you can use:

    https://github.com/nexB/attributecode/issues


SOURCE CODE
-----------
The AttributeCode is available through GitHub. For the latest version visit:
    https://github.com/nexB/attributecode


HACKING
-------
We accept pull requests provided under the same license as this tool.
You agree to the http://developercertificate.org/ 


LICENSE
-------
The AttributeCode is released under the Apache 2.0 license.
See the about.ABOUT file for details.


.. |master-posix| image:: https://travis-ci.com/nexB/attributecode.svg?branch=main
    :target: https://travis-ci.com/github/nexB/attributecode
    :alt: Linux Master branch tests status
.. |devel-posix| image:: https://travis-ci.com/nexB/attributecode.svg?branch=develop
    :target: https://travis-ci.com/github/nexB/attributecode
    :alt: Linux Develop branch tests status
