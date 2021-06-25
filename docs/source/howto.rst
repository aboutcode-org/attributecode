======
HOW TO
======

.. contents::
   :depth: 3

This section covers the basic usage of the command and options.


Command
=======

.. code-block:: none

    Usage: attributecode [OPTIONS] INPUT OUTPUT

    Options:
      --version                    Show the version and exit.
      -c, --configuration FILE     Path to an optional YAML configuration file for
                                   renaming fields name.
      --licensedb-url URL          URL to the custom LicenseDB (default:
                                   https://scancode-licensedb.aboutcode.org/)
      --min-license-score INTEGER  Attribute components that have license score
                                   higher than the defined --min-license-score.
      --scancode                   Indicate the input JSON file is from
                                   scancode_toolkit.
      --reference DIR              Path to a directory with reference files where
                                   "license_file" and/or "notice_file" located.
      --template FILE              Path to an optional custom attribution template
                                   to generate the attribution document. If not
                                   provided the default built-in template is used.
      --vartext <key>=<value>      Add variable text as key=value for use in a
                                   custom attribution template.
      -q, --quiet                  Do not print error or warning messages.
      --verbose                    Show all error and warning messages.
      -h, --help                   Show this message and exit.

-c, --configuration
-------------------

This is used for field renaming purpose.
The configuration file has to be a YAML formatted file.

The syntax is
``<current>: <new>``

For instance,

.. code-block:: none

    Component: name
    Confirmed Version: version
    License Expression: license_expression

With the above configuration file, the tool will rename the ``Component`` to ``name``,
``Confirmed Version`` to ``version`` and ``License Expression`` to ``license_expression``.


--licensedb-url
---------------

This option allow user to define the URL for the LicenseDB.

.. code-block:: none

    attributecode --licensedb-url <LicenseDB URL> <input.json> <output.html>


--scancode
----------

This option is to tell the tool the input is the scan result from the ScanCode Toolkit.
Note that the tool only accept JSON formatted file.

.. code-block:: none

    attributecode --scancode <input.json> <output.html>


--min-license-score
-------------------

This is used when we have a ScanCode JSON input and want to show licenses that have a score higher than the ``--min-license-score``.
For instance, if we want to show everything that has a license score greater than or equal to 40:

.. code-block:: none

    attributecode --min-license-score 40 --scancode <input.json> <output.html>

Other detected licenses whose license scores are less than 40 will not be collected.
This option can only work with a ScanCode JSON input, and therefore the ``--scancode`` option flag is needed.

.. Note:: The ``DEFAULT_LICENSE_SCORE`` is set to 100. Meaning ``attributecode --scancode <input.json> <output.html>`` will only collect licenses that have detected license score = 100


--reference
-----------

When the input has "license_file" or "notice_file" fields set, the tool needs to know where to read/get these files.

.. code-block:: none

    attributecode --reference ~/project/license_notices/ <input.csv> <output.csv>


--template
----------

Point to the custom template.

.. code-block:: none

    attributecode --template templates/scancode.template --scancode <input.json> <output.html>

.. Note:: ``templates/scancode.template`` is a custom template specifically for ScanCode's JSON input. The ``templates/default_html.template`` will be used if no ``--template`` is provided.


--vartext <key>=<value>
-----------------------

Pass variable(s) to the Jinja2 template.

.. code-block:: none

    attributecode --vartext "subtitle=THIS IS A SUBTITLE" <input.csv> <output.csv>

The above command passes the variable ``subtitle`` to the Jinja2 template. If users want to
access this variable, they can use ``{{ variables['subtitle'] }}`` to get the data.


Examples
========

Some sample input files are under the ``samples/`` directory:

- ``simple_sample.csv``
- ``report_sample.xlsx``
- ``clean-text-0.3.0-lceupi.json``


Sample commands
---------------

.. code-block:: none

    attributecode samples/simple_sample.csv <output.html>
    attributecode --vartext "subtitle=THIS IS A SUBTITLE" samples/simple_sample.csv <output.html>
    attributecode -c templates/sample.MAPPING samples/report_sample.xlsx <output.html>
    attributecode --template templates/scancode.template --scancode samples/clean-text-0.3.0-lceupi.json <output.html>
    attributecode --template templates/scancode.template --scancode --min-license-score 30 samples/clean-text-0.3.0-lceupi.json <output.html>
