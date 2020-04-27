# -*- coding: utf-8 -*-
"""functions for db handling"""

from ELDAmwl.constants import EBSC
from ELDAmwl.constants import MWL
from ELDAmwl.constants import RBSC
from ELDAmwl.database.db import DBUtils
from ELDAmwl.database.tables.backscatter import BscCalibrOption
from ELDAmwl.database.tables.backscatter import ElastBackscatterOption
from ELDAmwl.database.tables.backscatter import ElastBscMethod
from ELDAmwl.database.tables.backscatter import IterBackscatterOption
from ELDAmwl.database.tables.backscatter import RamanBackscatterOption
from ELDAmwl.database.tables.backscatter import RamanBscMethod
from ELDAmwl.database.tables.extinction import ExtinctionOption
from ELDAmwl.database.tables.extinction import ExtMethod
from ELDAmwl.database.tables.extinction import OverlapFile
from ELDAmwl.database.tables.lidar_ratio import ExtBscOption
from ELDAmwl.database.tables.measurements import Measurements
from ELDAmwl.database.tables.system_product import ErrorThresholds
from ELDAmwl.database.tables.system_product import MWLproductProduct
from ELDAmwl.database.tables.system_product import PreparedSignalFile
from ELDAmwl.database.tables.system_product import ProductOptions
from ELDAmwl.database.tables.system_product import Products
from ELDAmwl.database.tables.system_product import ProductTypes
from ELDAmwl.database.tables.system_product import SystemProduct
from ELDAmwl.log import logger
from sqlalchemy.orm import aliased


dbutils = DBUtils()


def read_signal_filenames(measurement_id):
    """

    Args:
        measurement_id:

    Returns:

    """
    signals = dbutils.session.query(PreparedSignalFile)\
        .filter(PreparedSignalFile._measurements_ID == measurement_id)

    if signals.count() > 0:
        return signals
    else:
        logger.error('no prepared signal files for measurement {0}'
                     .format(measurement_id))


def read_extinction_algorithm(product_id):
    """ read from db which algorithm shall be used for the slope
        calculation in extinction retrievals.

        Args:
            product_id (int): the id of the actual extinction product

        Returns:
            str: name of the BaseOperation class to be used

        """
    options = dbutils.session.query(ExtMethod,
                                    ExtinctionOption)\
        .filter(ExtMethod.ID == ExtinctionOption._ext_method_ID)\
        .filter(ExtinctionOption._product_ID == product_id)

    if options.count() == 1:
        result = options.value('python_classname')
        return result
    else:
        logger.error('wrong number of extinction options ({0})'
                     .format(options.count()))


def read_raman_bsc_algorithm(product_id):
    """ read from db which algorithm shall be used for
        calculation in Raman backscatter retrievals.

        Args:
            product_id (int): the id of the actual Raman bsc product

        Returns:
            str: name of the BaseOperation class to be used

        """
    options = dbutils.session.query(RamanBscMethod,
                                    RamanBackscatterOption)\
        .filter(RamanBscMethod.ID ==
                RamanBackscatterOption._ram_bsc_method_ID)\
        .filter(RamanBackscatterOption._product_ID == product_id)

    if options.count() == 1:
        result = options.value('python_classname')
        return result
    else:
        logger.error('wrong number of Raman bsc options ({0})'
                     .format(options.count()))


def read_elast_bsc_algorithm(product_id):
    """ read from db which algorithm shall be used for
        calculation in elastic backscatter retrievals.

        Args:
            product_id (int): the id of the actual elastic bsc product

        Returns:
            str: name of the BaseOperation class to be used

        """
    options = dbutils.session.query(ElastBscMethod,
                                    ElastBackscatterOption)\
        .filter(ElastBscMethod.ID == ElastBackscatterOption._ext_method_ID)\
        .filter(ElastBackscatterOption._product_ID == product_id)

    if options.count() == 1:
        result = options.value('python_classname')
        return result
    else:
        logger.error('wrong number of Raman bsc options ({0})'
                     .format(options.count()))


def read_lidar_ratio_params(product_id):
    """ function to read options of an lidar ratio product from db.

        This function reads from db with which parameters an
        lidar ratio product shall be derived.

        Args:
            product_id (int): the id of the actual extinction product

        Returns:
            ??: options

        """
    options = dbutils.session.query(ExtBscOption)\
        .filter(ExtBscOption._product_ID == product_id)

    if options.count() == 1:
        return options[0]
    else:
        logger.error('wrong number of lidar ratio options ({0})'
                     .format(options.count()))


def read_extinction_params(product_id):
    """ function to read options of an extinction product from db.

        This function reads from db with which parameters an
        extinction product shall be derived.

        Args:
            product_id (str): the id of the actual extinction product

        Returns:
            ??: options

        """
    options = dbutils.session.query(ExtMethod,
                                    ExtinctionOption)\
        .filter(ExtMethod.ID == ExtinctionOption._ext_method_ID)\
        .filter(ExtinctionOption._product_ID == product_id)

    if options.count() == 1:
        if options.value('_overlap_file_ID') == -1:
            overlap_correction = False
            overlap_file = None
        else:
            o_file = dbutils.session.query(OverlapFile,
                                           ExtinctionOption) \
                .filter(OverlapFile.ID == ExtinctionOption._overlap_file_ID) \
                .filter(ExtinctionOption._product_ID == product_id)
            if o_file.count() == 1:
                overlap_correction = True
                overlap_file = o_file.value('filename')
            else:
                logger.error('cannot find overlap file with id {0} in db'
                             .format(options('_overlap_file_ID')))

        result = {'angstroem': float(options.value('angstroem')),
                  'ext_method': options.value('_ext_method_ID'),
                  'overlap_correction': overlap_correction,
                  'overlap_file': overlap_file,
                  'error_method': options.value('_error_method_ID'),
                  }
        return result
    else:
        logger.error('wrong number of extinction options ({0})'
                     .format(options.count()))


def get_products_query(mwl_prod_id, measurement_id):
    """ read from db which of the products correlated to
        this system is the mwl product.

        Args:
            mwl_prod_id (int): product id of mwl product
            measurement_id(str): id of measurement

        Returns:
            list of individual product IDs corresponding to this mwl product

        """

    ErrorThresholdsLow = aliased(ErrorThresholds,
                                 name='ErrorThresholdsLow')
    ErrorThresholdsHigh = aliased(ErrorThresholds,
                                  name='ErrorThresholdsHigh')

    products = dbutils.session.query(
        MWLproductProduct,
        Products,
        ProductTypes,
        ProductOptions,
        ErrorThresholdsLow,
        ErrorThresholdsHigh,
        PreparedSignalFile,
    ).filter(
        MWLproductProduct._mwl_product_ID == mwl_prod_id,
    ).filter(
        MWLproductProduct._Product_ID == Products.ID,
    ).filter(
        Products._prod_type_ID == ProductTypes.ID,
    ).filter(
        ProductTypes.is_in_mwl_products == 1,
    ).filter(
        ProductOptions._product_ID == Products.ID,
    ).filter(
        ProductOptions._lowrange_error_threshold_ID == ErrorThresholdsLow.ID,
    ).filter(
        ProductOptions._highrange_error_threshold_ID == ErrorThresholdsHigh.ID,
    ).filter(
        PreparedSignalFile._Product_ID == Products.ID,
    ).filter(
        PreparedSignalFile._measurements_ID == measurement_id,
    )

    if products.count() > 0:
        return products
    else:
        logger.error('no individual products for mwl product')


def get_general_params_query(prod_id):
    """ read general params of a product from db

        Args:
            prod_id (int): id of the product

        Returns:
            general products

        """

    ErrorThresholdsLow = aliased(ErrorThresholds,
                                 name='ErrorThresholdsLow')
    ErrorThresholdsHigh = aliased(ErrorThresholds,
                                  name='ErrorThresholdsHigh')

    options = dbutils.session.query(
        Products,
        ProductTypes,
        ProductOptions,
        ErrorThresholdsLow,
        ErrorThresholdsHigh,
    ).filter(
        ProductOptions._product_ID == Products.ID,
    ).filter(
        Products._prod_type_ID == ProductTypes.ID,
    ).filter(
        ProductTypes.is_in_mwl_products == 1,
    ).filter(
        ProductOptions._lowrange_error_threshold_ID == ErrorThresholdsLow.ID,
    ).filter(
        ProductOptions._highrange_error_threshold_ID == ErrorThresholdsHigh.ID,
    ).filter(
        Products.ID == prod_id,
    )

    if options.count() == 1:
        return options[0]
    else:
        logger.error('wrong number of product options ({0})'
                     .format(options.count()))


def read_elast_bsc_params(product_id):
    """ function to read options of an elast bsc product from db.

        This function reads from db with which parameters an
        elast bsc product shall be derived.

        Args:
            product_id (str): the id of the actual elast bsc product

        Returns:
            options : {'elast_bsc_method', 'lr_input_method'}

        """
    options = dbutils.session.query(ElastBackscatterOption)\
        .filter(ElastBackscatterOption._product_ID == product_id)

    if options.count() == 1:
        result = {'elast_bsc_method': options.value('_elast_bsc_method_ID'),
                  'lr_input_method': options.value('_lr_input_method_id'),
                  }

        # if options.value('_lr_input_method_id') == PROFILE:
        #     lr_file = dbutils.session.query(LRFile) \
        #         .filter(LRFile.ID == ElastBackscatterOption._lr_file_ID) \
        #         .filter(ElastBackscatterOption._product_ID == product_id)
        #     if lr_file.count() == 1:
        #         result['lr_file'] = lr_file
        #     else:
        #         logger.error('cannot find lidar ratio file with id {0} in db'
        #                      .format(options('_lr_file_ID')))

        return result
    else:
        logger.error('wrong number of elast bsc options ({0})'
                     .format(options.count()))


def read_iter_bsc_params(product_id):
    """ function to read options of an iterative bsc product from db.

        This function reads from db with which parameters an
        iterative bsc product shall be derived.

        Args:
            product_id (str): the id of the actual iterative bsc product

        Returns:
            options : {'conv_crit', 'max_iteration_count', 'ram_bsc_method'}

        """
    options = dbutils.session.query(IterBackscatterOption,
                                    ElastBackscatterOption)\
        .filter(ElastBackscatterOption._product_ID == product_id)\
        .filter(ElastBackscatterOption._iter_bsc_options_id ==
                IterBackscatterOption.ID)

    if options.count() == 1:
        result = {'conv_crit': options.value('iter_conv_crit'),
                  'max_iteration_count': options.value('max_iteration_count'),
                  'ram_bsc_method': options.value('_ram_bsc_method_id'),
                  }

        return result
    else:
        logger.error('wrong number of iterative bsc options ({0})'
                     .format(options.count()))


def read_raman_bsc_params(product_id):
    """ function to read options of a Raman bsc product from db.

        This function reads from db with which parameters a
        Raman bsc product shall be derived.

        Args:
            product_id (str): the id of the actual Raman bsc product

        Returns:
            options : {'ram_bsc_method'}

        """
    options = dbutils.session.query(RamanBackscatterOption)\
        .filter(RamanBackscatterOption._product_ID == product_id)

    if options.count() == 1:
        result = {'ram_bsc_method': options.value('_ram_bsc_method_ID'),
                  }
        return result
    else:
        logger.error('wrong number of Raman bsc options ({0})'
                     .format(options.count()))


def get_bsc_cal_params_query(bsc_prod_id, bsc_type):
    """ read from db which shall be used to get the calibration of a sc product.

        Args:
            bsc_prod_id (int): product id of the bsc product
            bsc_type (int): must be 0 (Raman bsc) or 3 (elast bsc)

        Returns:
            calibration parameter

        """
    if bsc_type == EBSC:
        BackscatterOption = aliased(ElastBackscatterOption,
                                    name='BackscatterOption')
    if bsc_type == RBSC:
        BackscatterOption = aliased(RamanBackscatterOption,
                                    name='BackscatterOption')

    cal_params = dbutils.session.query(
        BscCalibrOption, BackscatterOption,
    ).filter(
        BscCalibrOption.ID == BackscatterOption._bsc_calibr_options_ID,
    ).filter(BackscatterOption._product_ID == bsc_prod_id)

    if cal_params.count() > 0:
        return cal_params[0]
    else:
        logger.error('no calibration params for bsc product')


def read_mwl_product_id(system_id):
    """ read from db which of the products correlated
        to this system is the mwl product.

        Args:
            system_id (int): the id of the actual lidar system

        Returns:
            product id of mwl product

        """
    products = dbutils.session.query(SystemProduct,
                                     Products)\
        .filter(SystemProduct._system_ID == system_id)\
        .filter(SystemProduct._Product_ID == Products.ID)\
        .filter(Products._prod_type_ID == MWL)

    if products.count() == 1:
        return products.value('_Product_ID')
    else:
        logger.error('wrong number of mwl products ({0})'
                     .format(products.count()))


def read_system_id(measurement_id):
    """ function to read from db which products shall be derived .

        This function reads from db which products
          (as product IDs) shall be derived.

        Args:
            measurement_id (str): the id string of the
            actual measurement

        Returns:
            list: List of product ids (int)

        """
    sys_id = dbutils.session.query(Measurements)\
        .filter(Measurements.ID == measurement_id)

    if sys_id.count() == 1:
        return sys_id.value('_hoi_system_ID')
    else:
        logger.error('wrong number of system IDs ({0})'.format(sys_id.count()))

#    for task in tasks:
#        pass
#        measurements = self.Base.classes.measurements
#        sypro = self.Base.classes.system_product
#        psf = self.Base.classes.prepared_signal_files

    # products_query = self.session.query(measurements, sypro).\
    #     filter(measurements.ID == measurement_id).\
    #     filter(sypro._system_ID == measurements._hoi_system_ID).all()
    #
    # for products in products_query:
    #     product_id = products.system_product._Product_ID
    #
    #     psf_query = self.session.query(psf).\
    #         filter(psf._Meas_ID == measurement_id).\
    #         filter(psf._Product_ID == product_id).all()
    #
    #     if psf_query == []:
    #         logger.notice('no file for product {p_id}'.
    #                       format(p_id=product_id))
    #     else:
    #         for filenames in psf_query:
    #             logger.notice(product_id, filenames.filename)
