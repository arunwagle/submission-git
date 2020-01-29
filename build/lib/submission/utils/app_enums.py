"""
All module level enums reside here.

Use the following Python documentation
as a reference on using Enums

https://docs.python.org/3/library/enum.html
"""

from enum import Enum, auto


class AutoName(Enum):
    """
    This class enables us to customize/enhance the basic
    functionality of Enum. Please prefer to extend AutoName
    class instead of Enum when creating your own Enums.
    """
    def _generate_next_value_(self, start, count, last_values):
        """
        This method is over-ridden from original definition
        in order to return enum_member.name when auto() is
        called to assign values to enum members. It will
        keep values more consistent across the project
        without hard-coding them. Saves refactoring effort.
        """
        return self


class DocumentStatus(AutoName):
    """
    All RequestStatus .
    """
    NEW = 1
    CONTENT_EXTRACTION_COMPLETE = 2
    WDS_TRAINING_DATA_UPLOADED = 3
    WKS_TRAINING_DATA_CREATED = 4
    COMPLETE = 5
