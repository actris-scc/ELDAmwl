# -*- coding: utf-8 -*-
"""ELDA exceptions"""

NO_ERROR = 0
UNKNOWN_EXCEPTION = 22


class ELDAmwlException(Exception):
    """
    base class of exceptions raised by ELDAmwl
    """
    return_value = None
    prod_id = None

    def __init__(self, prod_id):
        self.prod_id = prod_id


class CsvFileNotFound(ELDAmwlException):
    """
    Raised when the csv file is not found; can occur only while testing
    """


class FillTableFailed(ELDAmwlException):
    """
    Raised when the import of a DB table failed; can occur only while testing
    """


class SizeMismatch(ELDAmwlException):
    """
    Raised when profiles of different sizes are to be combined
    """
    def __init__(self, profile1_name, profile2_name, function_name):
        self.profile1_name = profile1_name
        self.profile2_name = profile2_name
        self.function_name = function_name

    def __str__(self):
        return('sizes of profiles {0} and {1} do not fit in function{2}'
               .format(self.profile1_name,
                       self. profile2_name,
                       self.function_name))


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
        return('cannot find {0} for {1} '
               'in data storage'.format(self.what, self.where))


class ProductNotUnique(ELDAmwlException):
    """
    Raised if there is more than one product defined with the same type and wavelength
    """
    def __init__(self, typ, wl):
        self.typ = typ
        self.wl = wl

    def __str__(self):
        return('more than one product of type {0} and wavelength {1} '
               .format(self.typ, self.wl))


class ELPPFileNotFound(ELDAmwlException):
    """raised when the requested ELPP file is not found
    """

    return_value = 3

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'ELPP file {0} not found'.format(self.filename)


class CannotOpenELLPFile(ELDAmwlException):
    """raised when an eLPP file cannot be opened"""

    return_value = 10

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'cannot open ELPP file {0}'.format(self.filename)


class LogPathNotExists(ELDAmwlException):
    """raised when the path for writing the log file does not exists"""
    return_value = 6


class UseCaseNotImplemented(ELDAmwlException):
    """Raised if a usecase or BaseOperation is called but not yet implemented
    """
    return_value = 7

    def __init__(self, usecase, product_type, instead):
        self.usecase = usecase
        self.product_type = product_type
        self.instead = instead

    def __str__(self):
        msg = 'Usecase {0} of {1} not yet implemented. '\
            .format(self.usecase, self.product_type)
        if self.instead:
            msg.join('use {0} instead.'.format(self.instead))
        return msg


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

    def __str__(self):
        return('Product {0} has wrong number of MonteCarlo '
               'iterations (must be larger than 1).'
               .format(self.prod_id))


class DetectionLimitZero(ELDAmwlException):
    """raised when a detection limit = 0.0 . The value must be >0.0
    """
    return_value = 31

    def __str__(self):
        return('detection limit of product {0} '
               'must be > 0'.format(self.prod_id))


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
    return_value = 40

    def __str__(self):
        return('Another ELPP file with different header information '
               'has already been red')


class BscCalParamsNotEqual(ELDAmwlException):
    """raised when calibration params of backscatter products are not equal"""
    return_value = 41

    def __init__(self, prod_id_1, prod_id_2):
        self.pid1 = prod_id_1
        self.pid2 = prod_id_2

    def __str__(self):
        return('calibration params of products {0} and {1} '
               'are not equal.'.format(self.pid1, self.pid2))


class NOMCOptions(ELDAmwlException):
    """raised when no MonteCarlo options are provided in SCC db
    for a product with error_method == mc
    """

    return_value = 42

    def __str__(self):
        return('no MonteCarlo options are provided in SCC db'
               'for product {0} which has error_method = mc'
               .format(self.prod_id))


class NoBscCalOptions(ELDAmwlException):
    """raised when a backscatter product has no calibration options in SCC db
    """

    return_value = 43

    def __str__(self):
        return('no backscatter calibration options are '
               'provided in SCC db for product {0}'
               .format(self.prod_id))
