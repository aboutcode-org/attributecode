=================================
General
=================================

.. contents::
   :depth: 3

Objective
=========
 
 - Create an Attribution Notice generation tool that can be used with many different types of input (e.g. spreadsheet, scan json, etc.)
 - Take the opportunity to create the best-in-class FOSS Attribution Notice generation tool
 - Provide a customizable Attribution Notice generation tool for DejaCode


Features
========

 - Accept data from multiple formats starting with:
    - A spreadsheet file (csv or xlsx)
    - A new JSON file format for Attribution that would have the primary Attribution fields
    - A ScanCode JSON file
 - Transform function to map incoming data to Attribution output fields.
 - Jinja templates to customize the Attribution Notice output
 - Access to a database of license texts based on ScanCode license keys
 