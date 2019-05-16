from logging import ERROR
from attrdict import AttrDict

from ELDAmwl import log
from ELDAmwl.constants import PRODUCT_TYPES
from ELDAmwl.database.db import DBUtils
from ELDAmwl.database.tables.measurements import Measurements
from ELDAmwl.database.tables.system_product import SystemProduct, MWLproductProduct, Products, ProductTypes
from ELDAmwl.database.tables.extinction import ExtinctionOption, ExtMethod, OverlapFile

dbutils = DBUtils()

def read_extinction_algorithm(product_id):
    """ read from db which algorithm shall be used for the slope calculation in extinction retrievals.

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
    else:
        log(ERROR, 'wrong number of extinction options ({})'.format(options.count()))


def read_extinction_options(product_id):
    """ function to read options of an extinction product from db.

        This function reads from db with which options an extinction product shall be derived.

        Args:
            product_id (int): the id of the actual extinction product

        Returns:
            ??: options

        """
    options = dbutils.session.query(ExtMethod,
                               ExtinctionOption)\
        .filter(ExtMethod.ID == ExtinctionOption._ext_method_ID)\
        .filter(ExtinctionOption._product_ID == product_id)

    if options.count() == 1:
        if options('_overlap_file_ID') == -1:
            overlap_correction = False
            overlap_file = None
        else:
            o_file = dbutils.session.query(OverlapFile,
                                            ExtinctionOption) \
                .filter(OverlapFile.ID == ExtinctionOption._overlap_file_ID) \
                .filter(ExtinctionOption._product_ID == product_id)
            if o_file.count() == 1:
                overlap_correction = True
                overlap_file = o_file('filename')
            else:
                log(ERROR, 'cannot find overlap file with id {} in db'.format( options('_overlap_file_ID') ))

        result = {'angstroem': options.value('angstroem'),
                  'python_classname': options.value('python_classname'),
                  'overlap_correction': overlap_correction,
                  'overlap_file': overlap_file
                  }
    else:
        log(ERROR, 'wrong number of extinction options ({})'.format(options.count()))


def get_products_query(mwl_prod_id):
    """ read from db which of the products correlated to this system is the mwl product.

        Args:
            mwl_prod_id (int): product id of mwl product

        Returns:
            list of individual product IDs corresponding to this mwl product

        """
    products = dbutils.session.query(MWLproductProduct, Products,
                                     ProductTypes)\
        .filter(MWLproductProduct._mwl_product_ID == mwl_prod_id)\
        .filter(MWLproductProduct._Product_ID == Products.ID)\
        .filter(Products._prod_type_ID == ProductTypes.ID)\
        .filter(ProductTypes.is_in_mwl_products == 1)

    if products.count() >0:
        return products
    else:
        log(ERROR, 'no individual products for mwl product')


def read_mwl_product_id(system_id):
    """ read from db which of the products correlated to this system is the mwl product.

        Args:
            system_id (int): the id of the actual lidar system

        Returns:
            product id of mwl product

        """
    products = dbutils.session.query(SystemProduct,
                                     Products)\
        .filter(SystemProduct._system_ID == system_id)\
        .filter(SystemProduct._Product_ID == Products.ID)\
        .filter(Products._prod_type_ID == PRODUCT_TYPES.mwl)

    if products.count() == 1:
        return products.value('_Product_ID')
    else:
        log(ERROR, 'wrong number of mwl products ({})'.format(products.count()))


def read_system_id(measurement_id):
    """ function to read from db which products shall be derived .

        This function reads from db which products (as product IDs) shall be derived.

        Args:
            measurement_id (str): the id string of the actual measurement

        Returns:
            list: List of product ids (int)

        """
    sys_id = dbutils.session.query(Measurements)\
        .filter(Measurements.meas_id == measurement_id)

    if sys_id.count() == 1:
        return sys_id.value('_hoi_system_ID')
    else:
        log(ERROR, 'wrong number of system IDs ({})'.format(sys_id.count()))

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

