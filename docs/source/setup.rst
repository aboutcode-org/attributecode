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
.. warning::
   Make sure you're either building from a fully intact git repository or PyPI tarballs.
   Most other sources (such as GitHub's tarballs, a git checkout without the .git folder)
   don't contain the necessary metadata will not work.

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

    source tmp/bin/activate

or on windows:

.. code-block:: none

    tmp\\bin\\activate

TESTS and DEVELOPMENT
---------------------
To install all the needed development dependencies, run (on posix):

.. code-block:: none

    source configure --dev

or on windows:

.. code-block:: none

    configure --dev

To verify that everything works fine you can run the test suite with:

.. code-block:: none

    pytest
