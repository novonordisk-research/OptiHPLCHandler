.. OptiHPLCHandler documentation master file, created by
   sphinx-quickstart on Mon Dec 18 15:10:02 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

###########################################
Welcome to OptiHPLCHandler's documentation!
###########################################

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. image:: https://img.shields.io/pypi/v/Opti-HPLC-Handler.svg
   :alt: PyPI Version
   :target: https://pypi.python.org/pypi/Opti-HPLC-Handler

.. image:: https://img.shields.io/pypi/pyversions/Opti-HPLC-Handler.svg
   :alt: PyPI Supported Versions

.. image:: https://img.shields.io/pypi/l/Opti-HPLC-Handler.svg
   :alt: PyPI License
   :target: https://github.com/novonordisk-research/OptiHPLCHandler/blob/main/LICENSE

.. image:: https://img.shields.io/pypi/dm/Opti-HPLC-Handler.svg
   :alt: PyPI Downloads

.. image:: https://img.shields.io/github/last-commit/novonordisk-research/OptiHPLCHandler.svg
   :alt: GitHub last commit
   :target: https://github.com/novonordisk-research/OptiHPLCHandler

OptiHPLCHandler is a simplified proxy API for interacting with the Waters Empower Web
API. It aims to make putting data into and getting data out of Empower easy, with the
aim of automating running samples. It will not feature changing data already in Empower.

************
Installation
************
The easiest way to install OptiHPLCHandler is using pip:

.. code-block:: bash

   pip install Opti-HPLC-Handler

The source code is currently hosted on GitHub at:
https://github.com/novonordisk-research/OptiHPLCHandler

***********
Basic Usage
***********
The main class is :class:`EmpowerHandler<OptiHPLCHandler.EmpowerHandler>`. This class is
used to connect to Empower and perform actions. The class is initialised with the an
`address`, a `project`, and optionally a `username`. `project` is the name of the
Empower project that you want to log in to. `address` is the address of the Empower
Web API. The address should be in the format https://<address>:<port>/. `username` is
the Empower username you want to use to log in. If no username is provided, the username
will be inferred from the user running the script. For more information, see the
:meth:`__init__<OptiHPLCHandler.EmpowerHandler.__init__>` method.

When an :class:`EmpowerHandler<OptiHPLCHandler.EmpowerHandler>` has been initialised, you
should use it with a context manager to ensure that the connection is closed properly. 
The context manager will also log you in and out of Empower. If no password is given,
:class:`EmpowerHandler<OptiHPLCHandler.EmpowerHandler>` will first try to use the password
stored in the keyring. If no password is stored in the keyring, it will prompt the user
for a password.

.. code-block:: python

   from OptiHPLCHandler import EmpowerHandler

   handler = EmpowerHandler(address, project)

   with handler:
      # Do stuff with empower

The EmpowerHandler class has a number of methods for interacting with Empower. You can
get the available :meth:`nodes<OptiHPLCHandler.EmpowerHandler.GetNodeNames>`,
:meth:`plate type names<OptiHPLCHandler.EmpowerHandler.GetPlateTypeNames>`, a list of 
:meth:`sample set methods<OptiHPLCHandler.EmpowerHandler.GetSampleSetMethods>`, and a
list of :meth:`method set methods<OptiHPLCHandler.EmpowerHandler.>` without any 
arguments.

With the names of plate types and methodset methods, you can post
:meth:`sample set methods<OptiHPLCHandler.EmpowerHandler.PostExperiment>`.

Once you have a node name, you can get the
:meth:`systems on that node<OptiHPLCHandler.EmpowerHandler.GetSystemNames>`, and with
the system name, you can get the
:meth:`status<OptiHPLCHandler.EmpowerHandler.GetStatus>` of the system, and
:meth:`start running samples<OptiHPLCHandler.EmpowerHandler.RunExperiment>` if a
sample set has been defined.

**************
Detailed Usage
**************

Class EmpowerHandler
==========================

.. autoclass:: OptiHPLCHandler.EmpowerHandler
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__
    :exclude-members: AddMethod, GetSetup, Status, username, address, project

Empower instrument method
=============================

.. autoclass:: OptiHPLCHandler.EmpowerInstrumentMethod
   :show-inheritance:
   :special-members: __init__

Empower module methods
=============================

.. automodule:: OptiHPLCHandler.empower_module_method
   :members:
   :inherited-members:
   :exclude-members: current_method, alter_method, find_value
   
******************
Indices and tables
******************

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`