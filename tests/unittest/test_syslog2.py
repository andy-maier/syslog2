"""
Unit tests for the syslog2 module.
"""

import logging

import syslog2


def test_platform():
    """
    Debug the platform.
    """
    # pylint: disable=protected-access
    print("Debug: _PLATFORM={!r}".format(syslog2._syslog2._PLATFORM))


def test_syslog_rfc5424():
    """
    Simple test to start with, needs improvement.
    """
    facility = 'local0'
    logger_name = 'test_syslog2_logger'
    program = 'test_syslog2'

    handler = syslog2.SysLogHandler(address='local', facility=facility,
                                    program=program, format=None)

    handler.setFormatter(
        logging.Formatter(fmt='%(message).2048s'))

    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    logger.log(logging.ERROR, "test error")
    logger.log(logging.WARNING, "test warning")
    logger.log(logging.INFO, "test info")
    logger.log(logging.DEBUG, "test debug")
