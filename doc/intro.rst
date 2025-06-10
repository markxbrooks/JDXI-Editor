.. mxpandda documentation master file, created by
   sphinx-quickstart on Sat May 11 10:48:11 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction to the CLI
=======================

These scripts are a collection of Python and BASH scripts which are intended to automate crystallographic data processing.

Ideally, 400 datasets can be processed in around 2 hours and the intention is to reduce this time further as mxpipe and mxpandda improves.

Namespace
---------

The scripts have a prefix "mxpipe_" ... to give them a 'namespace'.

Scripts specifically for panddas may have a prefix "mxpipe_pandda_" e.g.:

.. code-block:: console

   $ mxpipe_pandda_dimple.py
..

Similarly, scripts to assist in file transfer, may have a prefix "mxpipe_file_" e.g.:

.. code-block:: console

   $ mxpipe_file_copy.py
..

Global-Phasing-related scripts may have a prefix "mxpipe_gphl_" e.g.:

.. code-block:: console

   $ mxpipe_gphl_grade2.py
..

CCP4-related scripts may have a prefix "mxpipe_ccp4_" e.g.:

.. code-block:: console

   $ mxpipe_ccp4_xia2.py
..

Command-Line Options
--------------------

The programs use command-line options to specify the necessary parameters.

Commonly used arguments are:


.. option:: -r <dir>, --root <dir>

      Specify the root directory of the datasets

      Default: Current directory

.. option:: -d <True/False>, --dry_run <True/False>

      Specify whether a dry run should be performed. This is useful to test whether command line arguments are correct or not.

      Default: False

.. option:: -s <True/False>, --slurmify <True/False>

      Specify whether runs should be submitted via SLURM.
      It is generally recommended to test that one or two jobs run correctly before submitting ~400 jobs via SLURM.

      Default: False


The program SVIEW can be used to see the status of SLURM jobs

.. image:: images/sview.png
  :width: 400
  :alt: sview SLURM job


The mxpipe SLURM commands are shown below.

mxpipe.slurmify module
----------------------

.. automodule:: mxpipe.slurmify
   :members:
   :undoc-members:
   :show-inheritance: