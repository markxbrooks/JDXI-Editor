.. mxpandda documentation master file, created by
   sphinx-quickstart on Sat May 11 10:48:11 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introduction
============
The document is a user guide for the MXPANDDA software, providing instructions on how to use the GUI and command line interface for processing X-ray fragment screening datasets.

The purpose of the MXPANDDA software is to provide a user-friendly interface and command line interface (CLI) for processing X-ray fragment screening datasets.

It automates and streamlines the processing of multiple datasets, guiding users through various data processing steps such as running DIMPLE for molecular replacement, filling in missing reflections, calculating Fcalc and Phicalc values, and conducting PANDDA analysis.

The software includes a GUI for an overview of processing steps and results, as well as a CLI for batch processing using Python functions and scripts. It also integrates with SLURM for efficient processing of large datasets.

Finally the datasets are subjected to PANDDA analysis and after completion of the run, PANDDA.INSPECT can be used to inspect the resulting maps.

The ultimate goal is to reduce processing time and improve the accuracy of X-ray fragment screening analysis.

The MXPANDDA Command Line Interface (CLI)
----------------
The MXPANDDA CLI provides a terminal-based mechanism to process many datasets at a time using Python functions modules and scripts as well as some BASH scripts.
These scripts will be described later-on in the document, since most tasks can be accomplished with the GUI.

The MXPANDDA GUI
----------------

Since processing of 4-500 datasets of an X-ray fragment screening campaign in a multi-step process is complicated and sometimes frustrating when using a series of scripts alone, a GUI has been developed.
This aids and is an expert system to:

1) Perform the data processing steps sequentially
2) Give an overview of the status of each step, including logs and displaying which files have been output
3) Display any HTML results

Ideally, and by using SLURM 400 datasets can be processed in around 2 hours, and a PANDDA job then started. This may take an additional 2-4 hours to run, even using SLURM.
The intention is to reduce this time further as mxpipe and mxpandda improves.

Usage on the CDC
----------------

1) On the CDC, go to the mxpipe directory

.. code-block:: console

   $ cd /data/teams/xray/software/mxpipe
..

2) Then activate the virtual environment "linux-venv" which contains the dependencies which are required.

.. code-block:: console

   $ source venv-linux/bin/activate
..

3) Also, start the GPHL module

.. code-block:: console

   $ module load GPHL/20230726

..
4) Add the following to your ~/.bashrc

.. code-block:: console

   export LD_LIBRARY_PATH=/data/teams/xray/software/mxpipe/libxcb-cursor0:$LD_LIBRARY_PATH
..

5) Source your .bashrc

.. code-block:: console

   source ~/.bashrc
..

6) Then the gui can be started using the following command:

.. code-block:: console

   $ python3.8 mxpandda.py
..

.. image:: images/mxpandda.png
  :width: 400
  :alt: mxpandda
*The MXPANDDA GUI running*
