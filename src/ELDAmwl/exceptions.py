# -*- coding: utf-8 -*-
"""ELDA exceptions"""

NO_ERROR = 0
UNKNOWN_EXCEPTION = 22


class ELDAmwlException(Exception):
    return_value = None


class CsvFileNotFound(ELDAmwlException):
    """
    Raised when the csv file is not found
    """


class FillTableFailed(ELDAmwlException):
    """
    Raised when the import of a DB table failed
    """


class OnlyOneOverrideAllowed(ELDAmwlException):
    """
    Raised on attempt to add more than one override to class registry
    """
    return_value = 101


class NotFoundInStorage(ELDAmwlException):
    """
    Raised if the requested data are not found in data storage
    """
    return_value = 100


class LogPathNotExists(ELDAmwlException):
    """raised when the path for writing the log file does not exists"""
    return_value = 6


class UseCaseNotImplemented(ELDAmwlException):
    """Raised if a usecase or BaseOperation is called but not yet implemented
    """
    return_value = 7


class CalRangeHigherThanValid(ELDAmwlException):
    """raised when the range for finding the calibration window is higher
    than vertical range for product calculation"""
    return_value = 11


class NoValidDataPointsForCalibration(ELDAmwlException):
    """
    Raised if a backscatter calibration value cannot be
    calculated within the requested uncertainty.
    """
    return_value = 13


class NotEnoughMCIterations(ELDAmwlException):
    """raised when number of MC iterations is not >1"""
    return_value = 23


class BscCalParamsNotEqual(ELDAmwlException):
    """raised when calibration params of backscatter products are not equal"""
    return_value = 38


class WrongCommandLineParameter(ELDAmwlException):
    """raised when wrong command line parameters are provided"""
    return_value = 35


class DifferentCloudMaskExists(ELDAmwlException):
    """
    Raised if a cloud_mask shall be written to the data storage
    but the existing one is different from the new one
    """
    return_value = 36


class DifferentHeaderExists(ELDAmwlException):
    """
    Raised if a header shall be written to the data storage
    but the existing one is different from the new one
    """
    return_value = 37
