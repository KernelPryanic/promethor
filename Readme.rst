|language| |license|

=========
promethor
=========

Description
~~~~~~~~~~~

This is a bunch of custom prometheus collectors.

Installation
~~~~~~~~~~~~

``python setup.py install``

or

``pip install -e .``

or

``pip install promethor``

How to use
~~~~~~~~~~

Run ``promethor -c lvm -t 30 -p 9000``

Also checkout list of `arguments`_

arguments
^^^^^^^^^

* ``-t, --timeout`` - Monitoring timeout
* ``-c, --collectors`` - List of collectors. Choose from: ``lvm, sentry, sql, mongo``
* ``-p, --port`` - Port to run on
* ``--loglevel`` - Level of logging. Choose from: ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``, ``DEBUG``, ``NOTSET``
* ``-l, --log`` - Redirect logging to file

.. |language| image:: https://img.shields.io/badge/language-python-blue.svg
.. |license| image:: https://img.shields.io/badge/license-Apache%202-blue.svg

