# -*- coding: utf-8 -*-
"""ELDA exceptions"""
from ELDAmwl.errors.error_codes import CAL_RANGE_HIGHER_THAN_VALID, WRONG_TYPE_BASIC_PRODUCT_FOR_DERIVED_PRODUCT
from ELDAmwl.errors.error_codes import CLASS_REGISTRY_TOO_MAY_OVERRIDES
from ELDAmwl.errors.error_codes import COULD_NOT_FIND_CALIBR_WINDOW
from ELDAmwl.errors.error_codes import DATA_NOT_IN_STORAGE
from ELDAmwl.errors.error_codes import DB_ERROR
from ELDAmwl.errors.error_codes import DIFFERENT_BSC_OPTIONS_IN_MEASUREMENT
from ELDAmwl.errors.error_codes import DIFFERENT_CLOUD_MASK_EXISTS
from ELDAmwl.errors.error_codes import DIFFERENT_HEADER_EXISTS
from ELDAmwl.errors.error_codes import DIFFERENT_PRODUCT_TYPE_FOR_AE
from ELDAmwl.errors.error_codes import DIFFERENT_WL_IN_EXT_AND_BSC_FOR_LR
from ELDAmwl.errors.error_codes import ERR_INVALID_NB_OF_MC_ITERATIONS
from ELDAmwl.errors.error_codes import ERROR_LOG_DIR_NOT_EXISTS
from ELDAmwl.errors.error_codes import ERROR_SIG_FILE_NOT_EXISTS
from ELDAmwl.errors.error_codes import INTEGRATION_FAILED
from ELDAmwl.errors.error_codes import NC_OPEN_ERROR
from ELDAmwl.errors.error_codes import NEG_BSC_FOR_LIDAR_CONSTANT
from ELDAmwl.errors.error_codes import NO_BASIC_PRODUCT_FOR_DERIVED_PRODUCT
from ELDAmwl.errors.error_codes import NO_BSC_CAL_OPTIONS_IN_DB
from ELDAmwl.errors.error_codes import NO_BSC_FOR_LIDAR_CONSTANT
from ELDAmwl.errors.error_codes import NO_MC_OPTIONS_IN_DB
from ELDAmwl.errors.error_codes import NO_MWL_PRODUCT_DEFINED
from ELDAmwl.errors.error_codes import NO_PARAMS_FOR_DEPOL_UNCERTAINTY_IN_DB
from ELDAmwl.errors.error_codes import NO_PRODUCT_OPTIONS_IN_DB
from ELDAmwl.errors.error_codes import NO_PRODUCTS_GENERATED
from ELDAmwl.errors.error_codes import NO_STABLE_SOLUTION_FOR_KLETT
from ELDAmwl.errors.error_codes import NO_VALID_POINTS_FOR_CAL
from ELDAmwl.errors.error_codes import NOT_ENOUGH_MC_SAMPLES
from ELDAmwl.errors.error_codes import REPEATED_ATTEMPT_TO_CORRECT_MOL_TRANSM
from ELDAmwl.errors.error_codes import REPEATED_ATTEMPT_TO_NORMALZE_BY_SHOTS
from ELDAmwl.errors.error_codes import SAME_WL_FOR_AE
from ELDAmwl.errors.error_codes import USE_CASE_NOT_IMPLEMENTED
from ELDAmwl.errors.error_codes import WRONG_COMMAND_LINE_PARAM
from ELDAmwl.errors.error_codes import ZERO_DETECTION_LIMIT
from ELDAmwl.errors.error_codes import DIFFERENT_PRODS_RESOLUTION, COULD_NOT_FIND_PRODS_RESOLUTION

class ELDAmwlException(BaseException):
    """
    base class of exceptions raised by ELDAmwl
    """
    return_value = None
    prod_id = None

    def __init__(self, prod_id):
        self.prod_id = prod_id


class ELDAmwlConfigurationException(ELDAmwlException):
    """
    base class of exceptions raised by ELDAmwl if an error in configuration is found
    """
    return_value = None
    prod_id = None

    def __init__(self, prod_id):
        self.prod_id = prod_id


class Terminating(BaseException):
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


class ConfigFileNotFound(ELDAmwlException):
    """
    Raised when the csv file is not found; can occur only while testing
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return 'Config file {} not found'.format(self.file_path)


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


class RepeatedNormalizeByshots(ELDAmwlException):
    """
    Raised on attempt to normalize a signal by number of laser shots if it was already normalized before
    """
    return_value = REPEATED_ATTEMPT_TO_NORMALZE_BY_SHOTS

    def __init__(self, channel_id):
        self.signal = channel_id

    def __str__(self):
        return('attempt to normalize signal {0} by number of laser shots.'
               'But it was already normalized before'
               .format(self.channel_id))


class RepeatedCorrectMolTransm(ELDAmwlException):
    """
    Raised on attempt to correct a signal for molecular transmission it was already corrected before
    """
    return_value = REPEATED_ATTEMPT_TO_CORRECT_MOL_TRANSM

    def __init__(self, channel_id):
        self.signal = channel_id

    def __str__(self):
        return('attempt to correct signal {0} for molecular transmission.'
               'But it was already corrected before'
               .format(self.channel_id))


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


class ProductNotUnique(ELDAmwlConfigurationException):
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
    """raised when the requested ELPP file is not found on disc
    """

    return_value = ERROR_SIG_FILE_NOT_EXISTS

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'ELPP file {0} not found'.format(self.filename)


class CannotOpenELLPFile(ELDAmwlException):
    """raised when an ELPP file cannot be opened"""

    return_value = NC_OPEN_ERROR

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'cannot open ELPP file {0}'.format(self.filename)


class NoELPPFileInDB(ELDAmwlException):
    """raised when a measurement has no attributed ELPP files in database
    """

    return_value = ERROR_SIG_FILE_NOT_EXISTS

    def __init__(self, meas_id):
        self.meas_id = meas_id

    def __str__(self):
        return f'no ELPP file in database for measurement{self.meas_id}'


class NoBasicProductsInDB(ELDAmwlConfigurationException):
    """raised when no basic products are attributed to a mwl product in database
    """

    return_value = NO_PRODUCT_OPTIONS_IN_DB

    def __str__(self):
        return f'no basic products are defined for mwl product{self.prod_id}'


class LogPathNotExists(ELDAmwlException):
    """raised when the path for writing the log file does not exists"""
    return_value = ERROR_LOG_DIR_NOT_EXISTS


class UseCaseNotImplemented(ELDAmwlConfigurationException):
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


class DifferentWlForLR(ELDAmwlConfigurationException):
    """raised when the backscatter and extinction products for a lidar ratio
    retrieval have different wavelengths"""
    return_value = DIFFERENT_WL_IN_EXT_AND_BSC_FOR_LR

    def __init__(self, product_id):
        self.product_id = product_id

    def __str__(self):
        return('the extinction and backscatter products '
               'for the retrieval of lidar ratio (product_id={0}) '
               'have different wavelengths'.format(self.product_id))


class BasicProductMissingForDerivedProduct(ELDAmwlConfigurationException):
    """raised when one of the necessary basic products of a derived product was not attributed to the mwl product """
    return_value = NO_BASIC_PRODUCT_FOR_DERIVED_PRODUCT

    def __init__(self, product_id, missing_product_id):
        self.product_id = product_id
        self.missing_id = missing_product_id

    def __str__(self):
        return(f'the basic product {self.missing_id} '
               f'for the retrieval of the derived product {self.product_id} '
               f'was not attributed to the mwl product')


class WrongBasicProductForDerivedProduct(ELDAmwlConfigurationException):
    """raised when one of the necessary basic products of a derived product
    has the wrong product type (e.g. elast bsc for lidar ratio) """
    return_value = WRONG_TYPE_BASIC_PRODUCT_FOR_DERIVED_PRODUCT

    def __init__(self, product_id, wrong_product_id):
        self.product_id = product_id
        self.wrong_id = wrong_product_id

    def __str__(self):
        return(f'the basic product {self.wrong_id} '
               f'for the retrieval of the derived product {self.product_id} '
               f'has the wrong type (e.g. Elastic backscatter is not allowed for lidar ratio).')


class CalRangeHigherThanValid(ELDAmwlConfigurationException):
    """raised when the range for finding the calibration window is higher
    than vertical range for product calculation"""
    return_value = CAL_RANGE_HIGHER_THAN_VALID

    def __init__(self, product_id):
        self.product_id = product_id

    def __str__(self):
        return('the upper end of the height interval for searching '
               'the calibration window is higher than the upper end '
               'of the valid vertical range of product {0}'.format(self.product_id))


class IntegrationFailed(ELDAmwlException):
    """raised when integration failed"""
    return_value = INTEGRATION_FAILED

    def __init__(self, product_id):
        self.product_id = product_id

    def __str__(self):
        return('integration during retrieval of product {0} failed'.format(self.product_id))


class NoKlettSolution(ELDAmwlException):
    """raised when no stable solution for Klett retrieval can be found"""
    return_value = NO_STABLE_SOLUTION_FOR_KLETT

    def __init__(self, product_id):
        self.product_id = product_id

    def __str__(self):
        return('Klett retrieval of product {0} failed'.format(self.product_id))


class NoValidDataPointsForCalibration(ELDAmwlException):
    """
    Raised if a backscatter calibration value cannot be
    calculated within the requested uncertainty.
    """
    return_value = NO_VALID_POINTS_FOR_CAL

    def __str__(self):
        return('error of calibration factor larger than '
               'maximum allowable backscatter uncertainty')


class NotEnoughMCSamples(ELDAmwlException):
    """
    Raised if a Monte-Carlo error retrieval could not collect enough samples
    """
    return_value = NOT_ENOUGH_MC_SAMPLES

    def __str__(self):
        return('the MC error retrieval could not obtain enough samples')


class NoCalibrWindowFound(ELDAmwlException):
    """
    Raised if no calibration window could be found for a
    backscatter retrieval.
    """
    return_value = COULD_NOT_FIND_CALIBR_WINDOW

    def __str__(self):
        return('no calibration window could be found for product {0}'.
               format(self.prod_id))


class NotEnoughMCIterations(ELDAmwlConfigurationException):
    """raised when number of MC iterations is not >1"""
    return_value = ERR_INVALID_NB_OF_MC_ITERATIONS

    def __str__(self):
        return('Product {0} has wrong number of MonteCarlo '
               'iterations (must be larger than 1).'
               .format(self.prod_id))


class DetectionLimitZero(ELDAmwlConfigurationException):
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


class BscCalParamsNotEqual(ELDAmwlConfigurationException):
    """raised when calibration params of backscatter products are not equal"""
    return_value = DIFFERENT_BSC_OPTIONS_IN_MEASUREMENT

    def __init__(self, prod_id_1, prod_id_2):
        self.pid1 = prod_id_1
        self.pid2 = prod_id_2

    def __str__(self):
        return('calibration params of products {0} and {1} '
               'are not equal.'.format(self.pid1, self.pid2))


class NOMCOptions(ELDAmwlConfigurationException):
    """raised when no MonteCarlo options are provided in SCC db
    for a product with error_method == mc
    """

    return_value = NO_MC_OPTIONS_IN_DB

    def __str__(self):
        return('no MonteCarlo options are provided in SCC db'
               'for product {0} which has error_method = mc'
               .format(self.prod_id))


class NoBscCalOptions(ELDAmwlConfigurationException):
    """raised when a backscatter product has no calibration options in SCC db
    """

    return_value = NO_BSC_CAL_OPTIONS_IN_DB

    def __str__(self):
        return('no backscatter calibration options are '
               'provided in SCC db for product {0}'
               .format(self.prod_id))


class NoProductsGenerated(ELDAmwlException):
    """raised when no products were generated
    """

    return_value = NO_PRODUCTS_GENERATED

    def __str__(self):
        return('no individual products were generated'
               .format(self.prod_id))


class NegBscForLidarconst(ELDAmwlException):
    """raised when a negative backscatter profile shall be used for retrieval of lidar constant
    """

    return_value = NEG_BSC_FOR_LIDAR_CONSTANT

    def __str__(self):
        return('cannot calculate lidar constant from negative backscatter value'
               .format(self.prod_id))

class NoBscForLidarconst(ELDAmwlException):
    """raised when no bsc profile is available for retrieval of lidar constant
    """

    return_value = NO_BSC_FOR_LIDAR_CONSTANT

    def __str__(self):
        return('cannot calculate lidar constant without backscatter profile'
               .format(self.prod_id))

class SciPyWrapperAxisError(ELDAmwlException):
    """Raised when the scipy axis wrapper detects more than one dimension
    """

    def __init__(self):
        pass


class NoParamsForDepolUncertainty(ELDAmwlException):
    """raised when no parameters for depolarization uncertainty for a product and time are in the database
    """

    return_value = NO_PARAMS_FOR_DEPOL_UNCERTAINTY_IN_DB

    def __init__(self, prod_id, measurement_date):
        super(NoParamsForDepolUncertainty, self).__init__(prod_id)
        self.measurement_date = measurement_date

    def __str__(self):
        return ('no matching parameter for depolarization uncertainty for product {0} '
                'and measurement time{1} in database'.format(self.prod_id, self.measurement_date))

class NoMwlProductDefined(ELDAmwlConfigurationException):
    """raised when no multi-wavelength product is defined for the measurement
    """

    return_value = NO_MWL_PRODUCT_DEFINED

    def __init__(self, system_id):
        super(NoMwlProductDefined, self).__init__(None)
        self.system_id = system_id

    def __str__(self):
        return ('no multi-wavelength product is defined for the system_id {0}'.format(self.system_id))

class DifferentProductsResolution(ELDAmwlConfigurationException):
    """raised when the temporal and/or vertical resolutions are not the same for all the products of a mwl_product_id"""
    return_value = DIFFERENT_PRODS_RESOLUTION

    def __init__(self, mwl_product_id):
        self.mwl_product_id = mwl_product_id

    def __str__(self):
        return('the temporal and/or vertical resolutions are '
               'not consistent for all the products configured (mwl_product_id={0})'
               .format(self.mwl_product_id))

class CouldNotFindProductsResolution(ELDAmwlConfigurationException):
    """raised when the temporal and vertical resolutions are not defined for a mwl_product_id"""
    return_value = COULD_NOT_FIND_PRODS_RESOLUTION

    def __init__(self, mwl_product_id):
        self.mwl_product_id = mwl_product_id

    def __str__(self):
        return('the temporal and vertical resolutions are '
               'not available for mwl_product_id={0}'
               .format(self.mwl_product_id))

class SameWlForAE(ELDAmwlConfigurationException):
    """raised when the two products for the angstroem exponent
    retrieval have the same wavelength"""
    return_value = SAME_WL_FOR_AE

    def __init__(self, mwl_product_id):
        self.mwl_product_id = mwl_product_id

    def __str__(self):
        return('the products for the retrieval '
               'of angstroem exponent (product_id={0}) '
               'have the same wavelength'.format(self.mwl_product_id))

class DifferentProductTypeForAE(ELDAmwlConfigurationException):
    """raised when the two products for the angstroem exponent
    retrieval are not of the same type (b/e)"""
    return_value = DIFFERENT_PRODUCT_TYPE_FOR_AE

    def __init__(self, mwl_product_id):
        self.mwl_product_id = mwl_product_id

    def __str__(self):
        return('the products for the retrieval '
               'of angstroem exponent (product_id={0}) '
               'are not of the same type'.format(self.mwl_product_id))
