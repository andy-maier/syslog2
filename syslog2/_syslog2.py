# Copyright 2022 Andreas Maier. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=c-extension-no-member

"""
An improved SysLogHandler class that is (mostly) backwards compatible with the
standard Python SysLogHandler class.

This is a new implementation that does not use any code from the standard Python
SysLogHandler implementation.
"""

import platform
import sys
import os
from datetime import datetime
import socket
import logging

import six
import pytz

# Determine the current operating system platform
_system = platform.system()
if _system == 'Linux':
    _PLATFORM = 'linux'
elif _system == 'Darwin':  # macOS
    if tuple(map(int, platform.mac_ver()[0].split('.'))) >= (10, 12):
        _PLATFORM = 'macos_unified'  # unified logging system
    else:
        _PLATFORM = 'macos_syslog'   # Apple system log
elif os.name == 'posix':  # Linux and macOS also have posix
    _PLATFORM = 'unix'
elif _system == 'Windows':
    _PLATFORM = 'windows'
elif _system.startswith('CYGWIN'):  # e.g. 'CYGWIN_NT-6.1'
    _PLATFORM = 'cygwin'
else:
    _PLATFORM = 'other'

if _PLATFORM == 'macos_unified':
    import macos_oslog  # noqa: F401 pylint: disable=import-error,unused-import
elif _PLATFORM == 'windows':
    import win32evtlog  # noqa: F401 pylint: disable=import-error,unused-import

__all__ = ['SysLogHandler', 'SYSLOG_UDP_PORT', 'SYSLOG_TCP_PORT']

# Default ports
SYSLOG_UDP_PORT = 514
SYSLOG_TCP_PORT = 514


class SysLogHandler(logging.Handler):
    """
    A logging handler that sends log records to the local system log or to
    a remote Syslog server.
    """

    # Valid values for the 'format' init parameter
    _valid_formats = (None, 'user', 'pri', 'rfc5424', 'rfc3164')

    # Targets when using the local system log (i.e. address='local')
    # Key: _PLATFORM
    # Value: A list of targets to try, in order. Each list item is a tuple
    #        (address, socktype, format) as defined for the init method, or
    #        None for special cases.
    _local_targets = {
        'linux': [
            ('/dev/log', socket.SOCK_DGRAM, 'rfc5424'),
            (('localhost', SYSLOG_UDP_PORT), None, 'rfc5424'),
        ],
        'unix': [
            (('localhost', SYSLOG_UDP_PORT), None, 'rfc5424'),
        ],
        'macos_unified': [
            (None, None, None),  # special-cased
        ],
        'macos_syslog': [
            ('/var/run/syslog', socket.SOCK_DGRAM, 'user'),
        ],
        'windows': [
            (None, None, None),  # special-cased
        ],
        'cygwin': [
            ('/dev/log', socket.SOCK_DGRAM, 'rfc5424'),
        ],
        'other': [
            (('localhost', SYSLOG_UDP_PORT), None, 'rfc5424'),
        ],
    }

    # Syslog severity codes.
    # As defined in https://www.rfc-editor.org/rfc/rfc5424.html#section-6.2.1
    #
    # Note: Some Syslog descriptions use the term "priority" for this, but
    # since RFC3264 and RFC5242 use the term "severity", we use that term as
    # well.
    # Note: Only a subset of these codes is used, see _level_map.
    LOG_EMERG = 0           # system is unusable
    LOG_ALERT = 1           # action must be taken immediately
    LOG_CRIT = 2            # critical conditions
    LOG_ERR = 3             # error conditions
    LOG_WARNING = 4         # warning conditions
    LOG_NOTICE = 5          # normal but significant condition
    LOG_INFO = 6            # informational
    LOG_DEBUG = 7           # debug-level messages

    #: Syslog facility codes.
    #: As defined in https://www.rfc-editor.org/rfc/rfc5424.html#section-6.2.1
    LOG_KERN = 0            # kernel messages
    LOG_USER = 1            # random user-level messages
    LOG_MAIL = 2            # mail system
    LOG_DAEMON = 3          # system daemons
    LOG_AUTH = 4            # security/authorization messages
    LOG_SYSLOG = 5          # messages generated internally by syslogd
    LOG_LPR = 6             # line printer subsystem
    LOG_NEWS = 7            # network news subsystem
    LOG_UUCP = 8            # UUCP subsystem
    LOG_CRON = 9            # clock daemon
    LOG_AUTHPRIV = 10       # security/authorization messages (private)
    LOG_FTP = 11            # FTP daemon
    LOG_NTP = 12            # NTP subsystem
    LOG_SECURITY = 13       # Log audit
    LOG_CONSOLE = 14        # Log alert
    LOG_SOLCRON = 15        # Scheduling daemon (Solaris)
    LOG_LOCAL0 = 16         # reserved for local use
    LOG_LOCAL1 = 17         # reserved for local use
    LOG_LOCAL2 = 18         # reserved for local use
    LOG_LOCAL3 = 19         # reserved for local use
    LOG_LOCAL4 = 20         # reserved for local use
    LOG_LOCAL5 = 21         # reserved for local use
    LOG_LOCAL6 = 22         # reserved for local use
    LOG_LOCAL7 = 23         # reserved for local use

    #: Mapping of Syslog severity names to their codes.
    _severity_names = {
        "alert": LOG_ALERT,
        "crit": LOG_CRIT,
        "critical": LOG_CRIT,
        "debug": LOG_DEBUG,
        "emerg": LOG_EMERG,
        "err": LOG_ERR,
        "error": LOG_ERR,           # Deprecated
        "info": LOG_INFO,
        "notice": LOG_NOTICE,
        "panic": LOG_EMERG,         # Deprecated
        "warn": LOG_WARNING,        # Deprecated
        "warning": LOG_WARNING,
    }

    #: Mapping of Syslog facility names to their codes.
    facility_names = {
        'kern': LOG_KERN,
        'user': LOG_USER,
        'mail': LOG_MAIL,
        'daemon': LOG_DAEMON,
        'auth': LOG_AUTH,
        'syslog': LOG_SYSLOG,
        'lpr': LOG_LPR,
        'news': LOG_NEWS,
        'uucp': LOG_UUCP,
        'cron': LOG_CRON,
        'authpriv': LOG_AUTHPRIV,
        'ftp': LOG_FTP,
        'ntp': LOG_NTP,
        'security': LOG_SECURITY,
        'console': LOG_CONSOLE,
        'solaris-cron': LOG_SOLCRON,
        'local0': LOG_LOCAL0,
        'local1': LOG_LOCAL1,
        'local2': LOG_LOCAL2,
        'local3': LOG_LOCAL3,
        'local4': LOG_LOCAL4,
        'local5': LOG_LOCAL5,
        'local6': LOG_LOCAL6,
        'local7': LOG_LOCAL7,
    }

    # Mapping of Python log levels to platform-specific log levels.
    # Deferred initialization in __init__().
    _level_map = None

    def __init__(self, address=('localhost', SYSLOG_UDP_PORT),
                 facility=LOG_USER, socktype=None, program=None,
                 format=None, append_nul=True):
        # pylint: disable=redefined-builtin
        """
        Initialize the handler.

        For socket-based communication with the syslog this includes creating
        the socket, and for stream-based sockets connecting to the socket.

        Parameters:

          address (str or tuple(host(str), port(int)): Address of the target
            Syslog, as follows:
              - string 'local': Targets the local system log. The `socktype`
                parameter is ignored. For details, see (TODO: Link).
              - other string: Address for a UNIX domain socket. The `socktype`
                parameter specifies the socket type.
              - tuple(host(str), port(int)): Hostname and port for an Internet
                domain socket. The `socktype` parameter specifies the socket
                type.

          facility (int or str): Syslog facility to be used, either the facility
            code as an integer, or the facility name as a string using the
            names defined in :attr:`SysLogHandler.facility_names`. For details
            on how this is used on macOS and Windows, see
            (TODO: Link).

          socktype (int or `None`): Socket type to be used when `address`
            specifies a socket:

            * `socket.SOCK_DGRAM` - datagram/UDP-based socket
            * `socket.SOCK_STREAM` - stream/TCP-based socket
            * `None` - The socket type is automatically selected as
              follows:

              - For UNIX domain sockets, `socket.SOCK_DGRAM` is tried first and
                then `socket.SOCK_STREAM`.
              - For Internet domain sockets, the socket type is determined
                when resolving the network address.

          program (str): Value to be used for the "program" Syslog field.
            If `None`, the base file name from `sys.args[0]` is used.
            For details on how this is used on macOS and Windows, see
            (TODO: Link).

          format (str): Selects the format of the log message that is sent to
            the system log, i.e. what is added to the message provided by the
            Python logging formatter. The Python logging formatter must match
            the selected format. Valid formats are:

              * 'user' - The logging formatter needs to create the complete log
                message that will be sent, and this class does not add or change
                anything. The ``append_nul`` argument is ignored.

              * 'pri' - The logging formatter needs to create the complete log
                message except for ``<PRI>`` which is added to the front of the
                log message by this class. A 0x00 Byte is appended as
                determined by the ``append_nul`` argument. This is what the
                standard Python SysLogHandler class does.

              * 'rfc5424' - Syslog format as defined in
                https://www.ietf.org/rfc/rfc5424.html. The logging formatter
                only creates the message field, and all other Syslog fields are
                automatically populated. A 0x00 Byte is appended as determined
                by the ``append_nul`` argument.

              * 'rfc3164' - Syslog format as defined in
                https://www.ietf.org/rfc/rfc3164.html. The logging formatter
                only creates the message field, and all other Syslog fields are
                automatically populated. A 0x00 Byte is appended as determined
                by the ``append_nul`` argument.

              * `None` - Dependent on the target, the right format is selected.
                The logging formatter only creates the message field.
                TODO: Implement.

          append_nul (bool): Boolean controlling whether a 0x00 Byte is
            appended to the log message for some log formats. Some older Syslog
            servers need this.

        Raises:
          Exception: None of the targets worked. TODO: Define exception
          OSError: Used for reporting errors with the target (socket errors, or
            API errors).
          TypeError: Argument has invalid type.
          ValueError: Argument has invalid value.
        """

        # Deferred initialization of mapping of Python log levels to
        # platform-specific log levels
        if SysLogHandler._level_map is None:
            if _PLATFORM == 'macos_unified':
                SysLogHandler._level_map = {
                    'DEBUG': macos_oslog.OS_LOG_TYPE_DEBUG,
                    'INFO': macos_oslog.OS_LOG_TYPE_INFO,
                    'WARNING': macos_oslog.OS_LOG_TYPE_DEFAULT,
                    'ERROR': macos_oslog.OS_LOG_TYPE_ERROR,
                    'CRITICAL': macos_oslog.OS_LOG_TYPE_FAULT,
                }
            elif _PLATFORM == 'windows':
                SysLogHandler._level_map = {
                    'DEBUG': None,  # TBD
                    'INFO': None,  # TBD
                    'WARNING': None,  # TBD
                    'ERROR': None,  # TBD
                    'CRITICAL': None,  # TBD
                }
            else:  # A syslog platform
                SysLogHandler._level_map = {
                    'DEBUG': SysLogHandler.LOG_DEBUG,
                    'INFO': SysLogHandler.LOG_INFO,
                    'WARNING': SysLogHandler.LOG_WARNING,
                    'ERROR': SysLogHandler.LOG_ERR,
                    'CRITICAL': SysLogHandler.LOG_CRIT,
                }

        # pylint: disable=super-with-arguments
        super(SysLogHandler, self).__init__()

        if not isinstance(facility, int):
            try:
                facility = SysLogHandler.facility_names[facility]
            except KeyError:
                # pylint: disable=raise-missing-from
                raise ValueError("Invalid facility name: {}".format(facility))

        if program is None:
            program = os.path.basename(sys.argv[0])

        if format not in SysLogHandler._valid_formats:
            raise ValueError("Invalid format: {}".format(format))

        self._facility = facility
        self._program = program
        self._append_nul = append_nul

        # Attributes that will be modified in _init_target():
        self._address = None
        self._socktype = None
        self._format = None
        self._macos_logs = None  # For macos_unified platform
        self._win32_eventlog = None  # For windows platform
        self._socket = None  # For all other platforms

        if address == 'local':
            last_exc = None
            for _address, _socktype, _format in \
                    SysLogHandler._local_targets[_PLATFORM]:
                try:
                    self._init_target(_address, _socktype, _format)
                    break
                except Exception as exc:  # pylint: disable=broad-except TODO
                    last_exc = exc
                    continue
            else:
                # TODO: Define exception
                raise Exception(
                    "No target worked, last error: {}".format(last_exc))
        else:
            # May raise exception
            self._init_target(address, socktype, format)

        print("Debug: init: _PLATFORM={!r}, final target: address={!r} "
              "socktype={!r} format={!r}".
              format(_PLATFORM, self._address, self._socktype, self._format))

    def _init_target(self, address, socktype, format):
        # pylint: disable=redefined-builtin
        """
        Attempts to initialize for the specified target (address, socktype,
        format).

        Raises:
          Exception: Initialization failed for this target
        """

        if _PLATFORM == 'macos_unified':
            if format is None:
                format = 'user'
            # The Log objects will be created deferred, in emit(), one per
            # logger name.
            self._macos_logs = {}  # dict of Log objects, by logger name

        elif _PLATFORM == 'windows':
            # self._win32_eventlog = ... # TODO: Implement
            raise NotImplementedError

        else:
            if format is None:
                format = 'rfc5424'
            # A syslog platform
            if isinstance(address, six.string_types):
                # UNIX domain socket
                self._socket, socktype = self._unix_socket(address, socktype)
            elif isinstance(address, tuple):
                # Internet domain socket
                self._socket, socktype = self._internet_socket(
                    address, socktype)
            else:
                raise TypeError("Invalid type for 'address': {}".
                                format(type(address)))

        # Save the target data
        self._format = format
        self._address = address
        self._socktype = socktype

    def _unix_socket(self, address, socktype):
        """
        Create a UNIX domain socket and connect to it.

        If `socktype` is `None`, first try with `socket.SOCK_DGRAM` and
        then with `socket.SOCK_STREAM`. Otherwise, use only the specified
        socket type.

        Returns:
          tuple (socket, socktype)

        Raises:
          Exception: Initialization failed for this target
        """
        if socktype is None:
            last_exc = None
            for _socktype in (socket.SOCK_DGRAM, socket.SOCK_STREAM):
                try:
                    return self._unix_socket2(address, _socktype)
                except Exception as exc:  # pylint: disable=broad-except TODO
                    last_exc = exc
                    continue
            else:  # pylint: disable=useless-else-on-loop
                raise last_exc
        return self._unix_socket2(address, socktype)

    @staticmethod
    def _unix_socket2(address, socktype):
        """
        Create a UNIX domain socket and connect to it.

        Returns:
          tuple (socket, socktype)

        Raises:
          Exception: Initialization failed for this target
        """
        sock = socket.socket(socket.AF_UNIX, socktype)
        assert sock is not None
        try:
            sock.connect(address)
        except OSError:
            sock.close()
            raise
        return (sock, socktype)

    @staticmethod
    def _internet_socket(address, socktype):
        """
        Create an Internet domain socket and connect to it.

        If `socktype` is `None`, try with all socket types when resolving the
        address. Otherwise, use only the specified socket type.

        Returns:
          tuple (socket, socktype)

        Raises:
          Exception: Initialization failed for this target
        """
        host, port = address
        if not (isinstance(host, six.string_types) and isinstance(port, int)):
            raise TypeError("Invalid types for tuple items in 'address': "
                            "({}, {})".format(type(host), type(port)))

        if socktype is None:
            addr_type = 0  # Get all socket types
        else:
            addr_type = socktype  # Limit to just this socket type
        addr_list = socket.getaddrinfo(host, port, type=addr_type)
        if not addr_list:
            raise OSError("Cannot resolve host {}".format(host))

        last_exc = None
        for _family, _socktype, _proto, _, _sockaddr in addr_list:
            try:
                sock = socket.socket(_family, _socktype, _proto)
            except OSError as exc:
                last_exc = exc
                continue
            if _socktype == socket.SOCK_STREAM:
                try:
                    sock.connect(_sockaddr)
                except OSError as exc:
                    last_exc = exc
                    sock.close()
                    continue
            return (sock, _socktype)

        raise OSError("Cannot create/connect socket for host {} "
                      "port {}, last error: {}".
                      format(host, port, last_exc))

    def _encode_priority(self, record):
        """
        Return the Syslog priority value from the facility code and the severity
        code. The severity code is mapped from the log level of the Python log
        record.
        """
        return self._facility * 8 + SysLogHandler._level_map[record.levelname]

    @staticmethod
    def _timestamp_str(tm_secs):
        """
        Parameters:
          tm_secs (float): Time in seconds since the epoch (as returned by
            `time.time()`). Note, this implies UTC as the timezone.
        Returns:
          str: Timestamp as a string, in the format needed for RFC3164/5424.
        """
        dt = datetime.fromtimestamp(tm_secs, tz=pytz.utc)
        ts_str = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        return ts_str

    def emit(self, record):
        """
        Emit a log record to the system log.

        The input record is formatted using the Python logging formatter, and
        then the log message is built dependent on the selected format.

        The record is then sent to the target.
        """
        try:

            msg = self.format(record)  # Python logging formatter

            if self._format == 'user':
                line = msg
            elif self._format == 'pri':
                pri = self._encode_priority(record)
                # pylint: disable=redundant-u-string-prefix
                line = u'<{pri}>{msg}'.format(pri=pri, msg=msg)
            else:
                pri = self._encode_priority(record)
                ts = self._timestamp_str(record.created)
                hostname = socket.getfqdn()
                if self._format == 'rfc3164':
                    # pylint: disable=redundant-u-string-prefix
                    line = u'<{pri}>{ts} {host} {msg}'. \
                        format(pri=pri, ts=ts, host=hostname, msg=msg)
                else:
                    assert self._format == 'rfc5424', \
                        "Invalid self._format={!r}".format(self._format)
                    version = 1
                    # pylint: disable=redundant-u-string-prefix
                    line = u'<{pri}>{v} {ts} {host} {app} {pid} {mid} {msg}'. \
                        format(pri=pri, v=version, ts=ts, host=hostname,
                               app=self._program, pid=record.process, mid='-',
                               msg=msg)

            print("Debug: emit: line={!r}".format(line))

            if _PLATFORM == 'macos_unified':

                # Deferred creation of log object
                logger_name = record.name
                if logger_name not in self._macos_logs:
                    self._macos_logs[logger_name] = macos_oslog.os_log_create(
                        subsystem=self._program, category=logger_name)
                macos_level = SysLogHandler._level_map[record.levelname]
                log = self._macos_logs[logger_name]

                macos_oslog.os_log(log=log, level=macos_level, message=line)

            elif _PLATFORM == 'windows':

                # TODO: Implement
                raise NotImplementedError

            else:  # A syslog platform

                line = line.encode('utf-8')
                if self._append_nul:
                    line += b'\x00'

                if isinstance(self._address, six.string_types):
                    # UNIX domain socket
                    try:
                        self._socket.send(line)
                    except OSError:
                        self._socket.close()
                        self._socket, self._socktype = \
                            self._unix_socket(self._address, self._socktype)
                        self._socket.send(line)
                else:
                    # Internet domain socket
                    if self._socktype == socket.SOCK_DGRAM:
                        self._socket.sendto(line, self._address)
                    else:
                        try:
                            self._socket.sendall(line)
                        except OSError:
                            self._socket.close()
                            self._socket, self._socktype = \
                                self._internet_socket(
                                    self._address, self._socktype)
                            self._socket.sendall(line)

        except Exception:  # pylint: disable=broad-except
            # pylint: disable=not-callable
            self.handleError(record)

    def close(self):
        """
        Close the Syslog handler.

        This method releases all resources acquired since init, and then calls
        the superclass close().
        """
        self.acquire()
        try:

            if _PLATFORM == 'macos_unified':
                for log in self._macos_logs.values():
                    macos_oslog.os_log_release(log)
            elif _PLATFORM == 'windows':
                # TODO: Implement
                raise NotImplementedError
            else:
                if self._socket is not None:
                    self._socket.close()

            # pylint: disable=super-with-arguments
            super(SysLogHandler, self).close()

        finally:
            self.release()
