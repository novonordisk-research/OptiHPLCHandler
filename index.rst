.. OptiHPLCHandler documentation master file, created by
   sphinx-quickstart on Mon Dec 18 15:10:02 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to OptiHPLCHandler's documentation!
===========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

OptiHPLCHandler is a simplified proxy API for interacting with the Waters Empower Web
API. It aims to make putting data into and getting data out of Empower easy, with the
aim of automating running samples. It will not feature changing data already in Empower.

.. image:: https://img.shields.io/pypi/v/Opti-HPLC-Handler.svg
        :target: https://pypi.python.org/pypi/Opti-HPLCH-andler
         :alt: PyPI Version

.. image:: https://img.shields.io/pypi/pyversions/Opti-HPLC-Handler.svg
         :target: https://pypi.python.org/pypi/Opti-HPLC-Handler
          :alt: PyPI Supported Versions

.. image:: https://img.shields.io/pypi/l/Opti-HPLC-Handler.svg
         :target: https://pypi.python.org/pypi/Opti-HPLC-Handler
          :alt: PyPI License

.. image:: https://img.shields.io/pypi/dm/Opti-HPLC-Handler.svg
         :target: https://pypi.python.org/pypi/Opti-HPLC-Handler
          :alt: PyPI Downloads

.. image:: https://img.shields.io/github/last-commit/novonordisk-research/OptiHPLCHandler.svg
         :target: https://github.com/novonordisk-research/OptiHPLCHandler
            :alt: GitHub last commit


Installation
============
The easiest way to install OptiHPLCHandler is using pip:

```
pip install Opti-HPLC-Handler
```

The source code is currently hosted on GitHub at:
https://github.com/novonordisk-research/OptiHPLCHandler

Basic Usage
===========
The main class is the EmpowerHandler class. This class is used to connect to Empower
and perform actions. The class is initialised with the Empower address, 
project, and optoinally the username. The project is the name of the project in Empower
that you want to use. The address is the address of the Empower Web API. The address
should be in the format https://<address>:<port>/. The username is the username of the
user you want to use. If no username is provided, the username will be inferred from the
user running the script.

When the class is initialised, you should use it with a context amnager to ensure that
the connection is closed properly. The context manager will also log you in and out of
Empower. If no password is given, `EmpowerHandler` will first try to use the password
stored in the keyring. If no password is stored in the keyring, it will prompt the user
for a password.

.. code-block:: python

    from OptiHPLCHandler import EmpowerHandler

   handler = EmpowerHandler(address, project)

    with handler:
        # Do stuff with empower

The EmpowerHandler class has a number of methods for interacting with Empower. These
methods are documented below.

Class EmpowerHandler
==========================

.. autoclass:: OptiHPLCHandler.EmpowerHandler
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__
    :exclude-members: AddMethod, GetSetup, Status, username, address, project

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`