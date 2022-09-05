syslog2 - An improved SysLogHandler for Python
==============================================

.. image:: https://badge.fury.io/py/syslog2.svg
    :target: https://pypi.python.org/pypi/syslog2/
    :alt: Version on Pypi

.. image:: https://github.com/andy-maier/syslog2/workflows/test/badge.svg?branch=master
    :target: https://github.com/andy-maier/syslog2/actions/
    :alt: Actions status

.. image:: https://readthedocs.org/projects/syslog2/badge/?version=latest
    :target: https://readthedocs.org/projects/syslog2/builds/
    :alt: Docs build status (master)

.. image:: https://coveralls.io/repos/github/andy-maier/syslog2/badge.svg?branch=master
    :target: https://coveralls.io/github/andy-maier/syslog2?branch=master
    :alt: Test coverage (master)


Overview
--------

The syslog2 package provides a `syslog2.SysLogHandler`_ class that has some
improvements over the standard Python `logging.handlers.SysLogHandler`_ class:

* It supports a new value "local" for the `address` init parameter that
  automatically does the right thing for logging to the local system log,
  without requiring additional syslog demons or the like (other than what is
  built in to the operating system).

* When a syslog target is used, it supports the log formats defined in
  `RFC3164 <https://www.ietf.org/rfc/rfc3164.html>`_ and
  `RFC5424 <https://www.ietf.org/rfc/rfc5424.html>`_ via a new new optional
  init parameter `format`.

* It supports placing a program name into the log record via a new optional
  init parameter `program`.

* It supports adding a 0x00 Byte at the end of the log message for compatibility
  with older syslog environments, via a new optional init parameter
  `append_nul` that defaults to adding the Byte. This was previously an
  undocumented class attribute (with the same default).

* The previously undocumented class attribute `facility_names` is now
  officially available for callers to determine valid Syslog facility names
  and to map them to facility codes.

* A new class attribute `severity_names` has been added for callers to determine
  valid Syslog severity names and to map them to severity codes.

* The reachability of the targeted system log is verified already during
  creation of the SysLogHandler object, and not only when logging a message
  like the standard Python SysLogHandler class does. Issues with the system
  log are raised through a new `syslog2.SysLogTargetError`_ exception.

The new SysLogHandler class is mostly backwards compatible with the standard
Python SysLogHandler. There are some incompatibilities, though:

* The undocumented class attribute `append_nul` has been removed. This
  feature is now available as a new optional init parameter `append_nul`.

* The undocumented class attributes `priority_map` and `priority_names`
  have been removed or made private.

* The new SysLogTargetError exception needs to be handled.

Migration to use the new SysLogHandler class is easy as long as you did not
use any of the undocumented features:

Old code:

.. code-block:: python

    from logging.handlers import SysLogHandler

    # ... use it

New code:

.. code-block:: python

    from syslog2 import SysLogHandler

    # ... use it

.. _syslog2.SysLogHandler: https://syslog2.readthedocs.io/en/stable/reference.html#syslog2.SysLogHandler
.. _syslog2.SysLogTargetError: https://syslog2.readthedocs.io/en/stable/reference.html#syslog2.SysLogTargetError
.. _logging.handlers.SysLogHandler: https://docs.python.org/3/library/logging.handlers.html#sysloghandler


Installation
------------

To install the latest released version of the syslog2 package into your
active Python environment:

.. code-block:: bash

    $ pip install syslog2

This will also install any prerequisite Python packages.

For more details and alternative ways to install, see `Installation`_.

.. _Installation: https://syslog2.readthedocs.io/en/stable/intro.html#installation


Documentation
-------------

* `Documentation <https://syslog2.readthedocs.io/en/stable/>`_


Change History
--------------

* `Change history <https://syslog2.readthedocs.io/en/stable/changes.html>`_


Contributing
------------

For information on how to contribute to the syslog2 project, see
`Contributing <https://syslog2.readthedocs.io/en/stable/development.html#contributing>`_.


License
-------

The syslog2 project is provided under the
`Apache Software License 2.0 <https://raw.githubusercontent.com/andy-maier/syslog2/master/LICENSE>`_.
