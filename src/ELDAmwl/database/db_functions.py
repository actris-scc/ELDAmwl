from logging import ERROR

from ELDAmwl import log
from ELDAmwl.database.db import DBUtils
from ELDAmwl.database.tables.system_product import SystemProduct
from ELDAmwl.database.tables.extinction import ExtinctionOption, ExtMethod


dbutils = DBUtils()

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
        result = {'angstroem': options.value('angstroem'),
                  'python_classname': options.value('python_classname'),
                  }
    else:
        log(ERROR, 'wrong number of extinction options ({})'.format(options.count()))


def read_tasks(measurement_id):
    """ function to read from db which products shall be derived .

        This function reads from db which products (as product IDs) shall be derived.

        Args:
            measurement_id (str): the id string of the actual measurement

        Returns:
            list: List of product ids (int)

        """
    tasks = dbutils.session.query(#Measurements,
                               SystemProduct)
        #.filter(SystemProduct._system_ID == Measurements._hoi_system_ID)
    for task in tasks:
        pass
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

