
.. _`Introduction`:

Introduction
============


.. _`Functionality`:

Functionality
-------------

The syslog2 package provides a :class:`syslog2.SysLogHandler` class that has
some improvements over the standard Python
:class:`py:logging.handlers.SysLogHandler` class:

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

* The previously undocumented class attribute
  :data:`~syslog2.SysLogHandler.facility_names` is now officially available for
  callers to determine valid Syslog facility names and to map them to facility
  codes.

* A new class attribute `severity_names` has been added for callers to determine
  valid Syslog severity names and to map them to severity codes.

* The reachability of the targeted system log is verified already during
  creation of the SysLogHandler object, and not only when logging a message
  like the standard Python SysLogHandler class does. Issues with the system
  log are raised through a new :exc:`syslog2.SysLogTargetError` exception.

The new SysLogHandler class is mostly backwards compatible with the standard
Python SysLogHandler. There are some incompatibilities, though:

* The undocumented class attribute `append_nul` has been removed. This
  feature is now available as a new optional init parameter `append_nul`.

* The undocumented class attributes `priority_map` and `priority_names`
  have been removed or made private.

* The new :exc:`syslog2.SysLogTargetError` exception needs to be handled.

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


.. _`Installation`:

Installation
------------


.. _`Supported environments`:

Supported environments
^^^^^^^^^^^^^^^^^^^^^^

The package is supported on the following combinations of operating systems
and Python versions:

===================  ========================
Operating system     Suported Python versions
===================  ========================
Linux                2.7, 3.4 and higher
UNIX                 2.7, 3.4 and higher
macOS                3.5 and higher (1)
Windows              2.7, 3.5 and higher (2)
CygWin               2.7, 3.4 and higher
other                2.7, 3.4 and higher
===================  ========================

Notes:

* (1) The underlying `macos-oslog <https://pypi.org/project/macos-oslog/>`_
  package supports only Python 3.5 and higher.
* (2) The underlying `pywin32 <https://pypi.org/project/pywin32/>`_
  package does not support Python 3.4.

The package is regularly tested in CI systems with a number of different Python
versions on Ubuntu, Windows, and macOS.


.. _`Installing`:

Installing
^^^^^^^^^^

* Prerequisites:

  - The Python environment into which you want to install must be the current
    Python environment, and must have at least the following Python packages
    installed:

    - setuptools
    - wheel
    - pip

* Install the syslog2 package and its prerequisite
  Python packages into the active Python environment:

  .. code-block:: bash

      $ pip install syslog2


.. _`Installing a different version`:

Installing a different version
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The examples in the previous sections install the latest version of
syslog2 that is released on `PyPI`_.
This section describes how different versions of syslog2
can be installed.

* To install an older released version of syslog2,
  Pip supports specifying a version requirement. The following example installs
  syslog2 version 0.1.0
  from PyPI:

  .. code-block:: bash

      $ pip install syslog2==0.1.0

* If you need to get a certain new functionality or a new fix that is
  not yet part of a version released to PyPI, Pip supports installation from a
  Git repository. The following example installs syslog2
  from the current code level in the master branch of the
  `syslog2 repository`_:

  .. code-block:: bash

      $ pip install git+https://github.com/andy-maier/syslog2.git@master#egg=syslog2

.. _syslog2 repository: https://github.com/andy-maier/syslog2

.. _PyPI: https://pypi.python.org/pypi


.. _`Verifying the installation`:

Verifying the installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can verify that syslog2 is installed correctly by
importing the package into Python (using the Python environment you installed
it to):

.. code-block:: bash

    $ python -c "import syslog2; print('ok')"
    ok


.. _`Package version`:

Package version
---------------

The version of the syslog2 package can be accessed by
programs using the ``syslog2.__version__`` variable:

.. autodata:: syslog2._version.__version__

Note: For tooling reasons, the variable is shown as
``syslog2._version.__version__``, but it should be used as
``syslog2.__version__``.


.. _`Compatibility and deprecation policy`:

Compatibility and deprecation policy
------------------------------------

The syslog2 project uses the rules of
`Semantic Versioning 2.0.0`_ for compatibility between versions, and for
deprecations. The public interface that is subject to the semantic versioning
rules and specificically to its compatibility rules are the APIs and commands
described in this documentation.

.. _Semantic Versioning 2.0.0: https://semver.org/spec/v2.0.0.html

The semantic versioning rules require backwards compatibility for new minor
versions (the 'N' in version 'M.N.P') and for new patch versions (the 'P' in
version 'M.N.P').

Thus, a user of an API or command of the syslog2 project
can safely upgrade to a new minor or patch version of the
syslog2 package without encountering compatibility
issues for their code using the APIs or for their scripts using the commands.

In the rare case that exceptions from this rule are needed, they will be
documented in the :ref:`Change log`.

Occasionally functionality needs to be retired, because it is flawed and a
better but incompatible replacement has emerged. In the
syslog2 project, such changes are done by deprecating
existing functionality, without removing it immediately.

The deprecated functionality is still supported at least throughout new minor
or patch releases within the same major release. Eventually, a new major
release may break compatibility by removing deprecated functionality.

Any changes at the APIs or commands that do introduce
incompatibilities as defined above, are described in the :ref:`Change log`.

Deprecation of functionality at the APIs or commands is
communicated to the users in multiple ways:

* It is described in the documentation of the API or command

* It is mentioned in the change log.

* It is raised at runtime by issuing Python warnings of type
  ``DeprecationWarning`` (see the Python :mod:`py:warnings` module).

Since Python 2.7, ``DeprecationWarning`` messages are suppressed by default.
They can be shown for example in any of these ways:

* By specifying the Python command line option: ``-W default``
* By invoking Python with the environment variable: ``PYTHONWARNINGS=default``

It is recommended that users of the syslog2 project
run their test code with ``DeprecationWarning`` messages being shown, so they
become aware of any use of deprecated functionality.

Here is a summary of the deprecation and compatibility policy used by
the syslog2 project, by version type:

* New patch version (M.N.P -> M.N.P+1): No new deprecations; no new
  functionality; backwards compatible.
* New minor release (M.N.P -> M.N+1.0): New deprecations may be added;
  functionality may be extended; backwards compatible.
* New major release (M.N.P -> M+1.0.0): Deprecated functionality may get
  removed; functionality may be extended or changed; backwards compatibility
  may be broken.


.. _'Python namespaces`:

Python namespaces
-----------------

This documentation describes only the external APIs of the
syslog2 project, and omits any internal symbols and
any sub-modules.
