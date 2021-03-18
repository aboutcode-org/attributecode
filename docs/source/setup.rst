=====
Setup
=====

.. contents::
   :depth: 3

This Section covers the installation/setup process.

Requirement
===========
Python3.6

Setup
=====

INSTALLATION
------------
To install all the needed dependencies in a virtualenv, run (on posix):

.. code-block:: none

    source configure

or on windows:

.. code-block:: none

    configure

Activate the virtualenv
-----------------------
To activate the virtualenv, run (on posix):

.. code-block:: none

    source bin/activate

or on windows:

.. code-block:: none

    bin\\activate

TESTS and DEVELOPMENT
---------------------
To install all the needed development dependencies, run (on posix):

.. code-block:: none

    source configure etc/conf/dev

or on windows:

.. code-block:: none

    configure etc/conf/dev

To verify that everything works fine you can run the test suite with:

.. code-block:: none

    py.test
