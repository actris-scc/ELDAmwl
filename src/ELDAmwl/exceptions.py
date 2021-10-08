# -*- coding: utf-8 -*-
"""ELDA exceptions"""
from ELDAmwl.error_codes import DB_ERROR, CLASS_REGISTRY_TOO_MAY_OVERRIDES, DATA_NOT_IN_STORAGE, \
    ERROR_SIG_FILE_NOT_EXISTS, NC_OPEN_ERROR, ERROR_LOG_DIR_NOT_EXISTS, USE_CASE_NOT_IMPLEMENTED, \
    CAL_RANGE_HIGHER_THAN_VALID, NO_VALID_POINTS_FOR_CAL, ERR_INVALID_NB_OF_MC_ITERATIONS, ZERO_DETECTION_LIMIT, \
    WRONG_COMMAND_LINE_PARAM, DIFFERENT_CLOUD_MASK_EXISTS, DIFFERENT_HEADER_EXISTS, \
    DIFFERENT_BSC_OPTIONS_IN_MEASUREMENT, NO_MC_OPTIONS_IN_DB, NO_BSC_CAL_OPTIONS_IN_DB


class ELDAmwlException(Exception):
    """
    base class of exceptions raised by ELDAmwl
    """
    return_value = None
    prod_id = None

    def __init__(self, prod_id):
        self.prod_id = prod_id


class Terminating(Exception):
    """
    Marker Exception mixing for terminating Exceptions
    """


class DBErrorTerminating(ELDAmwlException):
    """
    Raised when a terminating DB problem occurs
    """

    return_value = DB_ERROR

    def __init__(self):
        pass


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
    return_value = CLASS_REGISTRY_TOO_MAY_OVERRIDES

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
    return_value = DATA_NOT_IN_STORAGE

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

    return_value = ERROR_SIG_FILE_NOT_EXISTS

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'ELPP file {0} not found'.format(self.filename)


class CannotOpenELLPFile(ELDAmwlException):
    """raised when an eLPP file cannot be opened"""

    return_value = NC_OPEN_ERROR

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'cannot open ELPP file {0}'.format(self.filename)


class LogPathNotExists(ELDAmwlException):
    """raised when the path for writing the log file does not exists"""
    return_value = ERROR_LOG_DIR_NOT_EXISTS


class UseCaseNotImplemented(ELDAmwlException):
    """Raised if a usecase or BaseOperation is called but not yet implemented
    """
    return_value = USE_CASE_NOT_IMPLEMENTED

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
    return_value = CAL_RANGE_HIGHER_THAN_VALID

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
    return_value = NO_VALID_POINTS_FOR_CAL

    def __str__(self):
        return('error of calibration factor larger than '
               'maximum allowable backscatter uncertainty')


class NotEnoughMCIterations(ELDAmwlException):
    """raised when number of MC iterations is not >1"""
    return_value = ERR_INVALID_NB_OF_MC_ITERATIONS

    def __str__(self):
        return('Product {0} has wrong number of MonteCarlo '
               'iterations (must be larger than 1).'
               .format(self.prod_id))


class DetectionLimitZero(ELDAmwlException):
    """raised when a detection limit = 0.0 . The value must be >0.0
    """
    return_value = ZERO_DETECTION_LIMIT

    def __str__(self):
        return('detection limit of product {0} '
               'must be > 0'.format(self.prod_id))


class WrongCommandLineParameter(ELDAmwlException):
    """raised when wrong command line parameters are provided"""
    return_value = WRONG_COMMAND_LINE_PARAM


class DifferentCloudMaskExists(ELDAmwlException):
    """
    Raised if a cloud_mask shall be written to the data storage
    but the existing one is different from the new one
    """
    return_value = DIFFERENT_CLOUD_MASK_EXISTS

    def __str__(self):
        return('Another ELPP file with a different cloud mask '
               'has already been red')


class DifferentHeaderExists(ELDAmwlException):
    """
    Raised if a header shall be written to the data storage
    but the existing one is different from the new one
    """
    return_value = DIFFERENT_HEADER_EXISTS

    def __str__(self):
        return('Another ELPP file with different header information '
               'has already been red')


class BscCalParamsNotEqual(ELDAmwlException):
    """raised when calibration params of backscatter products are not equal"""
    return_value = DIFFERENT_BSC_OPTIONS_IN_MEASUREMENT

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

    return_value = NO_MC_OPTIONS_IN_DB

    def __str__(self):
        return('no MonteCarlo options are provided in SCC db'
               'for product {0} which has error_method = mc'
               .format(self.prod_id))


class NoBscCalOptions(ELDAmwlException):
    """raised when a backscatter product has no calibration options in SCC db
    """

    return_value = NO_BSC_CAL_OPTIONS_IN_DB

    def __str__(self):
        return('no backscatter calibration options are '
               'provided in SCC db for product {0}'
               .format(self.prod_id))
