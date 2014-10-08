==============================================
telex - Remote execution of command line tools
==============================================

A REST service for remote execution of command line tools based on
`everest <https://github.com/cenix/everest>`_ .

Quick installation instructions
===============================

1. Create and activate a virtual environment for your ``telex`` server

::

  $ virtualenv --no-site-packages telexenv 
  $ source telexenv/bin/activate

2. Check out the sources of the ``telex`` project

::

  $ mkdir telexenv/src
  $ cd telexenv/src
  $ git clone https://github.com/fogathmann/telex.git``

3. Install the ``telex`` server

::

  $ cd telex
  $ pip install --allow-external python-graph-core --allow-unverified python-graph-core --find-links=https://github.com/cenix/everest/archive/master.zip#egg=everest-1.1dev .
  
  (the `--allow-external` and --`allow-unverified` options are to allow 
  installing the `python-graph-core` package which has not been maintained in
  a while).

4. Start the ``telex`` server

``$ paster serve telex.ini``
