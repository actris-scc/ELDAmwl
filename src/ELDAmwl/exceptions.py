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

    def __init__(self, factory_name):
        self.factory_name = factory_name

    def __str__(self):
        return('attempt to add more than one override to '
               'class registry for BaseOperationFactory {0}'
               .format(self.factory_name))


class NotFoundInStorage(ELDAmwlException):
    """
    Raised if the requested data are not found in data storage
    """
    return_value = 100

    def __init__(self, what, where):
        self.what = what
        self.where = where

    def __str__(self):
        return('cannot find {what} for {where} '
               'in data storage'.format(self.what, self.where))


class LogPathNotExists(ELDAmwlException):
    """raised when the path for writing the log file does not exists"""
    return_value = 6


class UseCaseNotImplemented(ELDAmwlException):
    """Raised if a usecase or BaseOperation is called but not yet implemented
    """
    return_value = 7

    def __init__(self, usecase, product_type, instead):
        self.usecase = usecase
        self.product = product_type
        self.instead = instead

    def __str__(self):
        msg = 'Usecase {0} of {1} not yet implemented. '\
            .format(self.usecase, self.product_type)
        if self.instead:
            msg.join('use {0} intsead.'.format(self.instead))
        return(msg)


class CalRangeHigherThanValid(ELDAmwlException):
    """raised when the range for finding the calibration window is higher
    than vertical range for product calculation"""
    return_value = 11

    def __init__(self, product_id):
        self.product_id = product_id

    def __str__(self):
        return('the upper end of the height interval for searching '
               'the calibration window is higher than the upper end '
               'of the valid vertical range of product {0}'.format(self.product_id))


class NoValidDataPointsForCalibration(ELDAmwlException):
    """
    Raised if a backscatter calibration value cannot be
    calculated within the requested uncertainty.
    """
    return_value = 13

    def __str__(self):
        return('error of calibration factor larger than '
               'maximum allowable backscatter uncertainty')


class NotEnoughMCIterations(ELDAmwlException):
    """raised when number of MC iterations is not >1"""
    return_value = 23


class DetectionLimitZero(ELDAmwlException):
    """raised when a detection limit = 0.0 . The value must be >0.0
    """
    return_value = 31

    def __init__(self, prod_id):
        self.prod_id = prod_id

    def __str__(self):
        return('detection limit of product {0} '
               'must be > 0'.format(self.prod_id))


class BscCalParamsNotEqual(ELDAmwlException):
    """raised when calibration params of backscatter products are not equal"""
    return_value = 38

    def __init__(self, prod_id_1, prod_id_2):
        self.pid1 = prod_id_1
        self.pid2 = prod_id_2

    def __str__(self):
        return('calibration params of products {0} and {1} '
               'are not equal.'.format(self.pid1, self.pid2))


class WrongCommandLineParameter(ELDAmwlException):
    """raised when wrong command line parameters are provided"""
    return_value = 35


class DifferentCloudMaskExists(ELDAmwlException):
    """
    Raised if a cloud_mask shall be written to the data storage
    but the existing one is different from the new one
    """
    return_value = 36

    def __str__(self):
        return('Another ELPP file with a different cloud mask '
               'has already been red')



class DifferentHeaderExists(ELDAmwlException):
    """
    Raised if a header shall be written to the data storage
    but the existing one is different from the new one
    """
    return_value = 37

    def __str__(self):
        return('Another ELPP file with different header information '
               'has already been red')

