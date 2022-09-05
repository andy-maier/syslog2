"""
Test import and versioning of the package.
"""


def test_import():
    """
    Test import of the package.
    """
    import syslog2  # noqa: F401 pylint: disable=import-outside-toplevel
    assert syslog2


def test_versioning():
    """
    Test import of the package.
    """
    import syslog2  # noqa: F401 pylint: disable=import-outside-toplevel
    assert syslog2.__version__
