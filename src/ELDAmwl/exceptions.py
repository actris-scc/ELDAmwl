# -*- coding: utf-8 -*-
"""ELDA exceptions"""


class CsvFileNotFound(Exception):
    """
    Raised when the csv file is not found
    """


class FillTableFailed(Exception):
    """
    Raised when the import of a DB table failed
    """


class OnlyOneOverrideAllowed(Exception):
    """
    Raised on attempt to add more than one override to class registry
    """


class NotFoundInStorage(Exception):
    """
    Raised if the requested data are not found in data storage
    """


class DifferentCloudMaskExists(Exception):
    """
    Raised if a cloud_mask shall be written to the data storage
    but the existing one is different from the new one
    """


class DifferentHeaderExists(Exception):
    """
    Raised if a header shall be written to the data storage
    but the existing one is different from the new one
    """
