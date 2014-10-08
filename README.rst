==============================================
telex - Remote execution of command line tools
==============================================

A REST service for remote execution of command line tools based on
`everest <https://github.com/cenix/everest>`_ .

Quick installation instructions
===============================

1. Check out the sources of the ``telex`` project

``$ git clone https://github.com/gathmann/telex.git``

2. Create amd activate a virtual environment for your ``telex`` server

::

  $ virtualenv --no-site-packages --distribute telexenv $ source
  telexenv/bin/activate

3. Install the ``telex`` server

::

  $ cd telex
  $ pip install -e --allow-external python-graph-core --allow-unverified python-graph-core .

4. Start the ``telex`` server

``$ paster serve telex.ini``
