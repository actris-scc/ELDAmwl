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
