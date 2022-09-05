
.. _`API Reference`:

API Reference
=============


.. _`Class SysLogHandler`:

Class SysLogHandler
-------------------

.. autoclass:: syslog2.SysLogHandler
   :members:
   :special-members: __getitem__

   .. # Note, we want to exclude __init__. Specifying one other special member
   .. # ba name causes __init__ to be excluded and all other special methods to
   .. # be included.

   .. rubric:: Methods

   .. autoautosummary:: syslog2.SysLogHandler
      :methods:
      :nosignatures:

   .. rubric:: Attributes

   .. autoautosummary:: syslog2.SysLogHandler
      :attributes:

   .. rubric:: Details


.. _`Class SysLogTargetError`:

Class SysLogTargetError
-----------------------

.. autoclass:: syslog2.SysLogTargetError
   :members:

   .. rubric:: Methods

   .. autoautosummary:: syslog2.SysLogTargetError
      :methods:
      :nosignatures:

   .. rubric:: Attributes

   .. autoautosummary:: syslog2.SysLogTargetError
      :attributes:


.. _`SysLogHandler Details`:

SysLogHandler Details
---------------------


.. _`Local system log targets`:

Local system log targets
^^^^^^^^^^^^^^^^^^^^^^^^

When the "address" parameter is set to "local", the system log on the local
system is automatically targeted:

* On Linux, a UNIX domain socket of datagram type to "/dev/log" is tried first.
  If that does not work, an Internet domain socket of UDP type to "localhost"
  on port 514 is tried.

* On UNIX, an Internet domain socket of UDP type to "localhost" on port 514 is
  used.

* On macOS 10.12 and later, the unified logging system is used by directly
  interfacing with its API.

* On macOS 10.11 and earlier, a UNIX domain socket of datagram type to
  "/var/run/syslog" is used (which is handled by the macOS system without
  requiring any additional syslog demon packages).

* On Windows, the event log is used by directly interfacing with its API.

* On CygWin, a UNIX domain socket of datagram type to "/dev/log" is used. This
  requires the "syslog-ng" package to be installed on CygWin.

* On other systems, an Internet domain socket of UDP type to "localhost" on
  port 514 is used.


.. _`Use of the syslog facility`:

Use of the syslog facility
^^^^^^^^^^^^^^^^^^^^^^^^^^

The syslog facility is used in the log message dependent on the target system
log:

* When targeting the local system log on macOS or Windows, the syslog facility
  is not used.

* Otherwise the target system log is handled by a syslog server, and the
  syslog facility is used to encode the priority value that is at the begin
  of the log message as ``<PRI>``.


.. _`Use of the program identifier`:

Use of the program identifier
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The program identifier is used in the log message dependent on the target system
log:

* When targeting the local system log on macOS 10.12 or later, the program
  identifier is used to set the "subsystem" parameter of the log entry.

* When targeting the local system log on macOS 10.11 or earlier, the program
  identifier is not used.

* When targeting the local system log on Windows, the program identifier
  is used to set the application name of the log entry.

* Otherwise the target system log is handled by a syslog server, and the
  program identifier is used dependent on the specified ``format`` argument:

  - For ``format="rfc5424"``, the program identifier is used for the "APP-NAME"
    field of the log message.
  - For ``format="rfc3164"``, the program identifier is not used in the log
    message.
  - Other formats are controlled by the logging formatter.
