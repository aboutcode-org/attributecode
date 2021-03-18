=======
General
=======

.. contents::
   :depth: 3

Objective
=========
- Create an Attribution Notice generation tool that can be used with different types of input (e.g., spreadsheet, json etc.).
- Take the opportunity to create the best-in-class FOSS Attribution Notice generation tool.
- Provide a customizable Attribution Notice generation tool for DejaCode.


Features
========
- Accept data from multiple formats starting with:

  - A spreadsheet file (csv or xlsx).
  - A JSON file format for Attribution that would have the primary Attribution fields.
  - A ScanCode JSON file.

- A configuration option to map input data to Attribution output fields.
- Jinja templates to customize the Attribution Notice output.
- Access to a database of license texts based on ScanCode license keys.


Input Requirement
=================
- Field/column names cannot contain any special characters or spaces. 

.. note::
   The following are special characters that the tool does not support:
   ['!', '@', '#', '$', '%', '^', '&', '*', '=', '{', '}', '|', '[', ']', '\\', ':', ';', '<', '>', '?', ',', '/']

- Field/column names will be automatically converted to lower case during the process.
- Technically, there are no required fields. However, if users want to extract license text from LicenseDB, users will want to fill in the ``license_expression`` fields with ScanCode's license key.

.. note::
    In the provided default template, the tool takes the following from the input: 'name', 'version', 'licesne_expression', 'copyright' etc. It is encourge to use the same keys in the input for the use of the default template, OR user can use the "-c, --configuration" option to do the key mapping, OR user can edit the template to use its own input keys.