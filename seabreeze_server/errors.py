"""
:Author: Jonathan D. B. Van Schenck
"""
from remote_object.errors import CallMethodError

__all__ = ['SeaBreezeServerError','CallMethodError']

class SeaBreezeServerError(Exception):
    """Base `SeaBreezeServerError`

    This is the main exception class which is raised for
    all errors resulting from server issues.
    """
    pass
