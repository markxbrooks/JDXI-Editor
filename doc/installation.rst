.. mxpandda documentation master file, created by
   sphinx-quickstart on Sat May 11 10:48:11 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Installation of the Command Line Interface (CLI)
================================================

1) Set up your BASH environment appropriately.

Some example aliases as well as locations of the files being sourced during my login sessions is shown below.

.. code-block:: console

      source /data/teams/xray/software/ccp4-8.0.004-pandda-pri/ccp4/bin/ccp4.setup-sh
      source '/data/teams/xray/env_setup.sh'
      export BDG_GRADE2_PYTHON_VERSION="3.9"
      module load GPHL/20230726
      . /apps/xray/GPHL/20230726/setup.sh
      module load /apps/modulefiles/xray/ccp4/8.0.004
      module load pandda/extras
      export PATH=$PATH:"/data/teams/xray/software/mxpipe/scripts:/home/mbrooks/.local/bin"
      alias python="/data/teams/xray/software/ccp4-8.0.004-pandda-pri/ccp4/bin/ccp4-python"
      alias sshgpu="ssh co-fr7-sgpu03"
      alias sshpri="ssh 192.168.56.243"
      alias cdpanddas="cd /data/sbio/xray/us-pri/XRay-Raw/panddas"
      alias cdmxpipe="cd /data/teams/xray/software/mxpipe"


2) Change directory to the mxpandda directory

.. code-block:: console

   $ cdmxpandda

This is an alias to cd to the mxpandda directory

3) Install the python module by running the script "setup.py". Usually we want to install it into ccp4-python:

.. code-block:: console

   $ ccp4-python setup.py install