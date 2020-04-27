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


class NoValidDataPointsForCalibration(Exception):
    """
    Raised if a backscatter calibration value cannot be
    calculated within the requested uncertainty.
    """
    # return value = 13


class UseCaseNotImplemented(Exception):
    """Raised if a usecase or BaseOperation is called but not yet implemented
    """
    # return value = 7


class CalRangeHigherThanValid(Exception):
    """raised when the range for finding the calibration window is higher
    than vertical range for product calculation"""
    # return value = 11


class BscCalParamsNotEqual(Exception):
    """raised when calibration params of backscatter products are not equal"""
