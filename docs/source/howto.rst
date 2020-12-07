=======
HOW TO
=======

.. contents::
   :depth: 3

This Section covers the basic usage of the commands and options.


Command
=======

.. code-block:: none

    Usage: attributecode [OPTIONS] INPUT OUTPUT
    
    Options:
      --version                    Show the version and exit.
      -c, --configuration FILE     Path to an optional YAML configuration file for
                                   renaming fields name.
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
This configuration file is a YAML formatted file.

The syntax is
<current>: <new>

For instance,

.. code-block:: none

    Component: name
    Confirmed Version: version
    License Expression: license_expression

--scancode
----------

As state in the description, this is to tell the tool that the input is from ScanCode toolkit.
Note that we, currently, only accept JSON from ScanCode toolkit.


--min-license-score
-------------------

This is used when we have a scancode's JSON input and want to show licenses that have score higher than the `--min-license-score`.
For instance, if we want to show everything that has license score larger than 40

.. code-block:: none

    attributecode --min-license-score 40 --scancode <input.json> <output.html>

Others detected licenses which license scores are less than 40 will not be collected.
This option can only work with the scancode's JSON input, and therefore, the `--scancode` option flag is needed.

.. Note:: The DEFAULT_LICENSE_SCORE is set to 100


--reference
-----------

When the input has "license_file" or "notice_file" fields set, the tool needs to know where to read these files.

.. code-block:: none

    attributecode --reference ~/project/license_notices/ <input.csv> <output.csv>


--template
----------

Point to the custom template

.. code-block:: none

    attributecode --template templates/scancode.template --scancode <input.json> <output.html>

.. Note:: "templates/scancode.template" is a custom template specifically for scancode's JSON input. 


--vartext <key>=<value>
-----------------------

Pass the varaiable(s) to Jinja2 template

.. code-block:: none

    attributecode --vartext "subtitle=THIS IS A SUBTITLE" <input.csv> <output.csv>

The above code pass the variable "subtitles" to Jinja2 template. If users want to
access this variable, the user can simply use {{ variables['subtitle'] }} to get the data.


Examples
========
Some sample input files are under the samples/:
 - simple_sample.csv
 - report_sample.xlsx
 - clean-text-0.3.0-lceupi.json


Sample commands
---------------

.. code-block:: none

    attributecode samples/simple_sample.csv <output.html>
    attributecode --vartext "subtitle=THIS IS A SUBTITLE" samples/simple_sample.csv <output.html>
    attributecode -c templates/sample.MAPPING samples/report_sample.xlsx <output.html>
    attributecode --template templates/scancode.template --scancode samples/clean-text-0.3.0-lceupi.json <output.html>
    attributecode --template templates/scancode.template --scancode --min-license-score 30 samples/clean-text-0.3.0-lceupi.json <output.html>