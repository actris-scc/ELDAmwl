# -*- coding: utf-8 -*-
"""functions for db handling"""
from addict import Dict
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.database.db import DBUtils
from ELDAmwl.database.tables.backscatter import BscCalibrLowestHeight
from ELDAmwl.database.tables.backscatter import BscCalibrRangeSearchMethod
from ELDAmwl.database.tables.backscatter import BscCalibrUpperHeight
from ELDAmwl.database.tables.backscatter import BscCalibrValue
from ELDAmwl.database.tables.backscatter import BscCalibrWindow
from ELDAmwl.database.tables.backscatter import ElastBackscatterOption
from ELDAmwl.database.tables.backscatter import ElastBscMethod
from ELDAmwl.database.tables.backscatter import IterBackscatterOption
from ELDAmwl.database.tables.backscatter import RamanBackscatterOption
from ELDAmwl.database.tables.backscatter import RamanBscMethod
from ELDAmwl.database.tables.channels import Channels
from ELDAmwl.database.tables.channels import ProductChannels
from ELDAmwl.database.tables.channels import Telescopes
from ELDAmwl.database.tables.depolarization import VLDROption
from ELDAmwl.database.tables.eldamwl_class_names import EldamwlClassNames
from ELDAmwl.database.tables.eldamwl_products import EldamwlProducts
from ELDAmwl.database.tables.extinction import ExtinctionOption
from ELDAmwl.database.tables.extinction import ExtMethod
from ELDAmwl.database.tables.extinction import OverlapFile
from ELDAmwl.database.tables.general import ELDAmwlLogs
from ELDAmwl.database.tables.lidar_constants import LidarConstants
from ELDAmwl.database.tables.lidar_ratio import ExtBscOption
from ELDAmwl.database.tables.measurements import Measurements
from ELDAmwl.database.tables.system_product import ErrorThresholds
from ELDAmwl.database.tables.system_product import MCOption
from ELDAmwl.database.tables.system_product import MWLproductProduct
from ELDAmwl.database.tables.system_product import PreparedSignalFile
from ELDAmwl.database.tables.system_product import PreProcOptions
from ELDAmwl.database.tables.system_product import Products
from ELDAmwl.database.tables.system_product import ProductTypes
from ELDAmwl.database.tables.system_product import SmoothMethod
from ELDAmwl.database.tables.system_product import SmoothOptions
from ELDAmwl.database.tables.system_product import SystemProduct
from ELDAmwl.errors.exceptions import NoBscCalOptions
from ELDAmwl.errors.exceptions import NOMCOptions
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import MWL
from ELDAmwl.utils.constants import RBSC
from sqlalchemy.orm import aliased
from zope import component
from zope import interface


def register_db_func(connect_string=None):
    db_func = DBFunc(connect_string)
    component.provideUtility(db_func, IDBFunc)
    return db_func


@interface.implementer(IDBFunc)
class DBFunc(DBUtils):

    def __init__(self, connect_string=None):
        super(DBFunc, self).__init__(connect_string)

    def db_log(self, level, datetime, measurement_id, product_id, module_version, msg):
        log_msg = ELDAmwlLogs(
            measurements_id=measurement_id,
            level=level,
            datetime=datetime,
            product_id=product_id,
            module_version=module_version,
            message=msg,
        )
        self.session.add(log_msg)
        self.session.commit()

    def read_classname(self, method):
        """reads from db in which python class the method is implemented
            Args:
                method (str): the method name

            Returns:
                str: name of the BaseOperation class to be used
         """
        classes = self.session.query(EldamwlClassNames)\
            .filter(EldamwlClassNames.method == method)

        if classes.count() == 1:
            return classes.first().classname
        else:
            self.logger.error('wrong number {0} of class names for method {1}'
                              .format(classes.count(), method))

    def read_algorithm(self, method_id, method_table):
        """ read from db which algorithm shall be used for product retrieval.

            Args:
                method_id (int): the id of the method for product retrieval
                method_table(Base): class which represents the db table with available methods

            Returns:
                str: name of the BaseOperation class to be used

            """
        methods = self.session.query(method_table)\
            .filter(method_table.ID == method_id)

        if methods.count() == 1:
            result = self.read_classname(methods.first().method)
            return result
        else:
            self.logger.error(
                'wrong number ({0}) of available methods'.format(methods.count()),
            )

    def read_effbin_algorithm(self, method_id, method_table):
        """ read from db which algorithm shall be used for the
        calculation of the effective bin resolution from the number of
        bins used for calculation in optical retrievals.

            Args:
                method_id (int): the id of the method for product retrieval
                method_table(Base): class which represents the db table with available methods

            Returns:
                str: name of the BaseOperation class to be used

            """
        methods = self.session.query(method_table)\
            .filter(method_table.ID == method_id)

        if methods.count() == 1:
            result = self.read_classname(methods.first().method_for_getting_effective_binres)
            return result
        else:
            self.logger.error(
                'wrong number ({0}) of available methods'.format(methods.count()),
            )

    def read_usedbin_algorithm(self, method_id, method_table):
        """ read from db which algorithm shall be used to calculate how
        many bins have to be used in the product
        retrievals in order to achieve a given effective resolution.
            Args:
                method_id (int): the id of the method for product retrieval
                method_table(Base): class which represents the db table with available methods

            Returns:
                str: name of the BaseOperation class to be used

            """
        methods = self.session.query(method_table)\
            .filter(method_table.ID == method_id)

        if methods.count() == 1:
            result = self.read_classname(methods.first().method_for_getting_used_binres)
            return result
        else:
            self.logger.error(
                'wrong number ({0}) of available methods'.format(methods.count()),
            )

    def read_algorithm_options(self, method_table):
        """read id's and names of all algorithm options from table
            Args:
                method_table(Base): class which represents the db table with available methods

            Returns:
                addict.Dict: keys= id's, values = names

        """
        options = self.session.query(method_table)

        if options.count() > 0:
            result = {}
            for o in options:
                result[o.ID] = o.method
            return Dict(result)
        else:
            self.logger.error('found no algorithms in db')

    def read_ext_method_id(self, product_id):
        """
        read from db which algorithm (id) shall be used for the retrieval of this extinction product
            Args:
                product_id (int): the id of the actual extinction product

            Returns:
                int: id of the algorithm in table _extinction_methods

        """
        options = self.session.query(ExtinctionOption)\
            .filter(ExtinctionOption.product_id == product_id)

        if options.count() == 1:
            result = options.first().ext_method_id
            return result
        else:
            self.logger.error(
                'wrong number of extinction options ({0})'.format(options.count()),
            )

    def read_extinction_algorithm(self, product_id):
        """ read from db which algorithm shall be used for the slope
            calculation in extinction retrievals.

            Args:
                product_id (int): the id of the actual extinction product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_ext_method_id(product_id)
        return self.read_algorithm(method_id, ExtMethod)

    def read_ext_effbin_algorithm(self, product_id):
        """ read from db which algorithm shall be used for the
        calculation of the effective bin resolution from the number of
        bins used for the slope calculation in extinction retrievals.

            Args:
                product_id (int): the id of the actual extinction product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_ext_method_id(product_id)
        return self.read_effbin_algorithm(method_id, ExtMethod)

    def read_ext_usedbin_algorithm(self, product_id):
        """ read from db which algorithm shall be used to calculate how
        many bins have to be used in the slope calculation of the extinction
        retrievals in order to achieve a given effective resolution.

            Args:
                product_id (int): the id of the actual extinction product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_ext_method_id(product_id)
        return self.read_usedbin_algorithm(method_id, ExtMethod)

    def read_raman_bsc_method_id(self, product_id):
        """
        read from db which algorithm (id) shall be used for the retrieval of this Raman bsc product
            Args:
                product_id (int): the id of the actual Raman bsc product

            Returns:
                int: id of the algorithm in table _ram_bsc_methods

        """
        options = self.session.query(RamanBackscatterOption)\
            .filter(RamanBackscatterOption.product_id == product_id)

        if options.count() == 1:
            result = options.first().ram_bsc_method_id
            return result
        else:
            self.logger.error(
                'wrong number of Raman bsc options ({0})'.format(options.count()),
            )

    def read_raman_bsc_smooth_method_id(self, product_id):
        """
        read from db which algorithm (id) shall be used for smoothing in the retrieval of this Raman bsc product
            Args:
                product_id (int): the id of the actual Raman bsc product

            Returns:
                int: id of the algorithm in table _ram_bsc_methods

        """
        options = self.session.query(RamanBackscatterOption)\
            .filter(RamanBackscatterOption.product_id == product_id)

        if options.count() == 1:
            result = options.first().smooth_method_id
            return result
        else:
            self.logger.error(
                'wrong number of Raman bsc options ({0})'.format(options.count()),
            )

    def read_raman_bsc_algorithm(self, product_id):
        """ read from db which algorithm shall be used for
            calculation in Raman backscatter retrievals.

            Args:
                product_id (int): the id of the actual Raman bsc product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_raman_bsc_method_id(product_id)
        return self.read_algorithm(method_id, RamanBscMethod)

    def read_raman_bsc_effbin_algorithm(self, product_id):
        """ read from db which algorithm shall be used for the
        calculation of the effective bin resolution from the number of
        bins used in Raman backscatter retrievals.

            Args:
                product_id (int): the id of the actual Raman bsc product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_raman_bsc_smooth_method_id(product_id)
        return self.read_effbin_algorithm(method_id, SmoothMethod)

    def read_raman_bsc_usedbin_algorithm(self, product_id):
        """ read from db which algorithm shall be used to calculate how
        many bins have to be used in Raman backscatter retrievals
        in order to achieve a given effective resolution.

            Args:
                product_id (int): the id of the actual Raman bsc product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_raman_bsc_smooth_method_id(product_id)
        return self.read_usedbin_algorithm(method_id, SmoothMethod)

    def read_elast_bsc_method_id(self, product_id):
        """
        read from db which algorithm (id) shall be used for the retrieval of this elastic bsc product
            Args:
                product_id (int): the id of the actual elastic bsc product

            Returns:
                int: id of the algorithm in table _elast_bsc_methods

        """
        options = self.session.query(ElastBackscatterOption)\
            .filter(ElastBackscatterOption.product_id == product_id)

        if options.count() == 1:
            result = options.first().elast_bsc_method_id
            return result
        else:
            self.logger.error(
                'wrong number of elastic bsc options ({0})'.format(options.count()),
            )

    def read_elast_bsc_smooth_method_id(self, product_id):
        """
        read from db which algorithm (id) shall be used for smoothing in the retrieval of this elastic bsc product
            Args:
                product_id (int): the id of the actual elastic bsc product

            Returns:
                int: id of the algorithm in table _elast_bsc_methods

        """
        options = self.session.query(ElastBackscatterOption)\
            .filter(ElastBackscatterOption.product_id == product_id)

        if options.count() == 1:
            result = options.first().smooth_method_id
            return result
        else:
            self.logger.error(
                'wrong number of elastic bsc options ({0})'.format(options.count()),
            )

    def read_elast_bsc_algorithm(self, product_id):
        """ read from db which algorithm shall be used for
            calculation in elastic backscatter retrievals.

            Args:
                product_id (int): the id of the actual elastic bsc product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_elast_bsc_method_id(product_id)
        return self.read_algorithm(method_id, ElastBscMethod)

    def read_elast_bsc_effbin_algorithm(self, product_id):
        """ read from db which algorithm shall be used for the
        calculation of the effective bin resolution from the number of
        bins used in elastic backscatter retrievals.

            Args:
                product_id (int): the id of the actual elastic bsc product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_elast_bsc_smooth_method_id(product_id)
        return self.read_effbin_algorithm(method_id, SmoothMethod)

    def read_elast_bsc_usedbin_algorithm(self, product_id):
        """ read from db which algorithm shall be used to calculate how
        many bins have to be used in elastic backscatter retrievals
        in order to achieve a given effective resolution.

            Args:
                product_id (int): the id of the actual elastic bsc product

            Returns:
                str: name of the BaseOperation class to be used

            """
        method_id = self.read_elast_bsc_smooth_method_id(product_id)
        return self.read_usedbin_algorithm(method_id, SmoothMethod)

    def read_lidar_ratio_params(self, product_id):
        """ function to read options of an lidar ratio product from db.

            This function reads from db with which parameters an
            lidar ratio product shall be derived.

            Args:
                product_id (int): the id of the actual extinction product

            Returns:
                ??: options

            """
        options = self.session.query(ExtBscOption)\
            .filter(ExtBscOption.product_id == product_id)

        if options.count() == 1:
            return options[0]
        else:
            self.logger.error(
                'wrong number of lidar ratio options ({0})'.format(options.count()),
            )

    def read_extinction_params(self, product_id):
        """ function to read options of an extinction product from db.

            This function reads from db with which parameters an
            extinction product shall be derived.

            Args:
                product_id (str): the id of the actual extinction product

            Returns:
                ??: options

            """
        options = self.session.query(ExtMethod, ExtinctionOption) \
            .filter(ExtMethod.ID == ExtinctionOption.ext_method_id) \
            .filter(ExtinctionOption.product_id == product_id)

        if options.count() == 1:
            if options.first().ExtinctionOption.overlap_file_id == -1:
                overlap_correction = False
                overlap_file = None
            else:
                o_file = self.session.query(OverlapFile, ExtinctionOption) \
                    .filter(OverlapFile.ID == ExtinctionOption.overlap_file_id) \
                    .filter(ExtinctionOption.product_id == product_id)
                if o_file.count() == 1:
                    overlap_correction = True
                    overlap_file = o_file.first().OverlapFile.filename
                else:
                    overlap_file = None
                    overlap_correction = False
                    self.logger.error(
                        'cannot find overlap file with id {0} in db'.format(options('_overlap_file_ID')),
                    )

            result = {'angstroem': float(options.first().ExtinctionOption.angstroem),
                      'ext_method': options.first().ExtinctionOption.ext_method_id,
                      'overlap_correction': overlap_correction,
                      'overlap_file': overlap_file,
                      'error_method': options.first().ExtinctionOption.error_method_id,
                      }
            return result
        else:
            self.logger.error(
                'wrong number of extinction options ({0})'.format(options.count()),
            )

    def get_basic_products_query(self, mwl_prod_id, measurement_id):
        """ read from db which of the products correlated to
            this system is the mwl product.

            Args:
                mwl_prod_id (int): product id of mwl product
                measurement_id(str): id of measurement

            Returns:
                list of individual product IDs corresponding to this mwl product

            """
        # todo: keep this ErrorThreshold tables in this query. we might need it when
        #  we implement automatic smoothing later. but for the moment, keep the lines inactive
        # ErrorThresholdsLow = aliased(ErrorThresholds,
        #                              name='ErrorThresholdsLow')
        # ErrorThresholdsHigh = aliased(ErrorThresholds,
        #                               name='ErrorThresholdsHigh')

        products = self.session.query(
            MWLproductProduct,
            Products,
            ProductTypes,
            SmoothOptions,
            PreProcOptions,
            # ErrorThresholdsLow,
            # ErrorThresholdsHigh,
            PreparedSignalFile,
            ProductChannels,
            Channels,
        ).filter(
            MWLproductProduct.mwl_product_id == mwl_prod_id,
        ).filter(
            MWLproductProduct.product_id == Products.ID,
        ).filter(
            Products.prod_type_id == ProductTypes.ID,
        ).filter(
            ProductTypes.is_in_mwl_products == 1,
        ).filter(
            ProductTypes.is_basic_product == 1,
        ).filter(
            SmoothOptions.product_id == Products.ID,
        ).filter(
            PreProcOptions.product_id == Products.ID,
        # ).filter(
        #     SmoothOptions.lowrange_error_threshold_id == ErrorThresholdsLow.ID,
        # ).filter(
        #     SmoothOptions.highrange_error_threshold_id == ErrorThresholdsHigh.ID,
        ).filter(
            ProductChannels.prod_id == Products.ID,
        ).filter(
            ProductChannels.channel_id == Channels.ID,
        ).filter(
            PreparedSignalFile.product_id == Products.ID,
        ).filter(
            PreparedSignalFile.measurements_id == measurement_id,
        ).group_by(Products.ID)

        if products.count() > 0:
            return products
        else:
            self.logger.error('no individual products for mwl product')

    def get_derived_products_query(self, mwl_prod_id):
        """ read from db which of the products correlated to
            this system is the mwl product.

            Args:
                mwl_prod_id (int): product id of mwl product

            Returns:
                list of individual product IDs corresponding to this mwl product

            """

        products = self.session.query(
            MWLproductProduct,
            Products,
            ProductTypes,
        ).filter(
            MWLproductProduct.mwl_product_id == mwl_prod_id,
        ).filter(
            MWLproductProduct.product_id == Products.ID,
        ).filter(
            Products.prod_type_id == ProductTypes.ID,
        ).filter(
            ProductTypes.is_in_mwl_products == 1,
        ).filter(
            ProductTypes.is_basic_product == 0,
        ).group_by(Products.ID)

        if products.count() > 0:
            return products
        else:
            self.logger.warning('no derived products for mwl product')

    def get_extended_general_params_query(self, prod_id):
        """ read general params of a product from db

            Args:
                prod_id (int): id of the product

            Returns:
                general products

            """
        # todo: same as in self.get_basic_products_query()
        # ErrorThresholdsLow = aliased(ErrorThresholds,
        #                              name='ErrorThresholdsLow')
        # ErrorThresholdsHigh = aliased(ErrorThresholds,
        #                               name='ErrorThresholdsHigh')

        options = self.session.query(
            Products,
            ProductTypes,
            PreProcOptions,
            SmoothOptions,
            # ErrorThresholdsLow,
            # ErrorThresholdsHigh,
            ProductChannels,
            Channels,
        ).filter(
            PreProcOptions.product_id == Products.ID,
        ).filter(
            SmoothOptions.product_id == Products.ID,
        ).filter(
            Products.prod_type_id == ProductTypes.ID,
        ).filter(
            ProductTypes.is_in_mwl_products == 1,
        # ).filter(
        #     SmoothOptions.lowrange_error_threshold_id == ErrorThresholdsLow.ID,
        # ).filter(
        #     SmoothOptions.highrange_error_threshold_id == ErrorThresholdsHigh.ID,
        ).filter(
            ProductChannels.prod_id == Products.ID,
        ).filter(
            ProductChannels.channel_id == Channels.ID,
        ).filter(
            Products.ID == prod_id,
        ).group_by(Products.ID)

        if options.count() == 1:
            return options[0]
        else:
            self.logger.error(
                'wrong number of product options ({0})'.format(options.count()),
            )

    def get_smooth_params_query(self, prod_id):
        """ read smooth params of a product from db

            Args:
                prod_id (int): id of the product

            Returns:
                query with smooth params

            """

        options = self.session.query(
            SmoothOptions,
        ).filter(
            SmoothOptions.product_id == prod_id)

        if options.count() == 1:
            return options[0]
        else:
            self.logger.error(
                'wrong number of product options ({0})'.format(options.count()),
            )

    def get_quality_params_query(self, prod_id):
        """ read quality params of a product from db

            Args:
                prod_id (int): id of the product

            Returns:
                query with smooth params

            """

        ErrorThresholdsLow = aliased(ErrorThresholds,
                                     name='ErrorThresholdsLow')
        ErrorThresholdsHigh = aliased(ErrorThresholds,
                                      name='ErrorThresholdsHigh')

        options = self.session.query(
            SmoothOptions,
            ErrorThresholdsLow,
            ErrorThresholdsHigh,
        ).filter(
            SmoothOptions.product_id == prod_id,
        ).filter(
            SmoothOptions.lowrange_error_threshold_id == ErrorThresholdsLow.ID,
        ).filter(
            SmoothOptions.highrange_error_threshold_id == ErrorThresholdsHigh.ID)

        if options.count() == 1:
            return options[0]
        else:
            self.logger.error(
                'wrong number of product options ({0})'.format(options.count()),
            )

    def read_elast_bsc_params(self, product_id):
        """ function to read options of an elast bsc product from db.

            This function reads from db with which parameters an
            elast bsc product shall be derived.

            Args:
                product_id (str): the id of the actual elast bsc product

            Returns:
                options : {'elast_bsc_method', 'lr_input_method'}

            """
        options = self.session.query(ElastBackscatterOption)\
            .filter(ElastBackscatterOption.product_id == product_id)

        if options.count() == 1:
            result = {'elast_bsc_method': options.first().elast_bsc_method_id,
                      'lr_input_method': options.first().lr_input_method_id,
                      'error_method': options.first().error_method_id,
                      'smooth_method': options.first().smooth_method_id,
                      'fixed_lr': options.first().fixed_lr,
                      'fixed_lr_error': options.first().fixed_lr_error,
                      }

            # if options.first()._lr_input_method_id == PROFILE:
            #     lr_file = self.session.query(LRFile) \
            #         .filter(LRFile.ID == ElastBackscatterOption._lr_file_ID) \
            #         .filter(ElastBackscatterOption._product_ID == product_id)
            #     if lr_file.count() == 1:
            #         result['lr_file'] = lr_file
            #     else:
            #         logger.error('cannot find lidar ratio file with id {0} in db'
            #                      .format(options('_lr_file_ID')))

            return result
        else:
            self.logger.error(
                'wrong number of elast bsc options ({0})'.format(options.count()),
            )

    def read_iter_bsc_params(self, product_id):
        """ function to read options of an iterative bsc product from db.

            This function reads from db with which parameters an
            iterative bsc product shall be derived.

            Args:
                product_id (str): the id of the actual iterative bsc product

            Returns:
                options : {'conv_crit', 'max_iteration_count', 'ram_bsc_method'}

            """
        options = self.session.query(IterBackscatterOption, ElastBackscatterOption) \
            .filter(ElastBackscatterOption.product_id == product_id) \
            .filter(ElastBackscatterOption.iter_bsc_options_id == IterBackscatterOption.ID)

        if options.count() == 1:
            result = {'conv_crit': options.first().IterBackscatterOption.iter_conv_crit,
                      'max_iteration_count': options.first().IterBackscatterOption.max_iteration_count,
                      'ram_bsc_method': options.first().IterBackscatterOption.ram_bsc_method_id,
                      }

            return result
        else:
            self.logger.error(
                'wrong number of iterative bsc options ({0})'.format(options.count()),
            )

    def read_raman_bsc_params(self, product_id):
        """ function to read options of a Raman bsc product from db.

            This function reads from db with which parameters a
            Raman bsc product shall be derived.

            Args:
                product_id (str): the id of the actual Raman bsc product

            Returns:
                options : {'ram_bsc_method'}

            """
        options = self.session.query(RamanBackscatterOption)\
            .filter(RamanBackscatterOption.product_id == product_id)

        if options.count() == 1:
            result = {'ram_bsc_method': options.first().ram_bsc_method_id,
                      'error_method': options.first().error_method_id,
                      'smooth_method': options.first().smooth_method_id,
                      }
            return result
        else:
            self.logger.error(
                'wrong number of Raman bsc options ({0})'.format(options.count()),
            )

    def read_vldr_params(self, product_id):
        """ function to read options of a VLDR product from db.

            This function reads from db with which parameters a
            VLDR product shall be derived.

            Args:
                product_id (str): the id of the actual Raman bsc product

            Returns:
                options : {'ram_bsc_method'}

            """
        options = self.session.query(VLDROption)\
            .filter(VLDROption.product_id == product_id)

        if options.count() == 1:
            result = {'vldr_method': options.first().vldr_method_id,
                      'error_method': options.first().error_method_id,
                      'smooth_method': options.first().smooth_method_id,
                      }
            return result
        else:
            self.logger.error(
                'wrong number of VLDR options ({0})'.format(options.count()),
            )

    def get_mc_params_query(self, prod_id):
        """read from db which params shall be used for the Monte-Carlo error retrieval
        Args:
            prod_id (int): product id

        """
        mc_params = self.session.query(MCOption) \
            .filter(MCOption.product_id == prod_id)

        if mc_params.count() == 1:
            return mc_params[0]
        else:
            raise(NOMCOptions, prod_id)

    def get_bsc_cal_params_query(self, bsc_prod_id, bsc_type):
        """ read from db which params shall be used to get the calibration of a sc product.

            Args:
                bsc_prod_id (int): product id of the bsc product
                bsc_type (int): must be 0 (Raman bsc) or 3 (elast bsc)

            Returns:
                calibration parameter

            """
        BackscatterOption = None

        if bsc_type == EBSC:
            BackscatterOption = aliased(ElastBackscatterOption,
                                        name='BackscatterOption')
        if bsc_type == RBSC:
            BackscatterOption = aliased(RamanBackscatterOption,
                                        name='BackscatterOption')

        cal_params = self.session.query(
            BscCalibrLowestHeight,
            BscCalibrUpperHeight,
            BscCalibrWindow,
            BscCalibrValue,
            BscCalibrRangeSearchMethod,
            BackscatterOption,
        ).filter(
            BackscatterOption.bsc_calibration_lowestheight_id == BscCalibrLowestHeight.ID
        ).filter(
            BackscatterOption.bsc_calibration_upperheight_id == BscCalibrUpperHeight.ID
        ).filter(
            BackscatterOption.bsc_calibration_window_id == BscCalibrWindow.ID
        ).filter(
            BackscatterOption.bsc_calibration_value_id == BscCalibrValue.ID
        ). filter(
            BackscatterOption.bsc_calibration_range_search_method_id == BscCalibrRangeSearchMethod.ID
        ).filter(BackscatterOption.product_id == bsc_prod_id)

        if cal_params.count() > 0:
            return cal_params[0]
        else:
            raise(NoBscCalOptions(bsc_prod_id))

    def read_mwl_product_id(self, system_id):
        """ read from db which of the products correlated
            to this system is the mwl product.

            Args:
                system_id (int): the id of the actual lidar system

            Returns:
                product id of mwl product

            """
        products = self.session.query(SystemProduct, Products) \
            .filter(SystemProduct.system_id == system_id) \
            .filter(SystemProduct.product_id == Products.ID) \
            .filter(Products.prod_type_id == MWL)

        if products.count() == 1:
            return products.first().Products.ID
        else:
            self.logger.error(
                'wrong number of mwl products ({0})'.format(products.count()),
            )

    def read_system_id(self, measurement_id):
        """ function to read from db which products shall be derived .

            This function reads from db which products
              (as product IDs) shall be derived.

            Args:
                measurement_id (str): the id string of the
                actual measurement

            Returns:
                list: List of product ids (int)

            """
        sys_id = self.session.query(Measurements)\
            .filter(Measurements.ID == measurement_id)

        if sys_id.count() == 1:
            return sys_id.first().hoi_system_id
        else:
            self.logger.error('wrong number of system IDs ({0})'.format(sys_id.count()))

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

    def read_smooth_routine(self, method_id):
        """ read from db which routine shall be used for smoothing

            Args:
                method_id (int): the id of the smooth method

            Returns:
                str: name of the BaseOperation class to be used

            """
        return self.read_algorithm(method_id, SmoothMethod)

    def read_full_overlap(self, channel_id):
        """ read height of full overlap of a channel

            Args:
                channel_id (int): the id of the channel

            Returns:
                float: height of the full overlap in m a.g.

        """
        ovl_heights = self.session.query(
            Channels, Telescopes,
        ).filter(
            Channels.ID == channel_id,
        ).filter(Channels.telescope_id == Telescopes.ID)

        if ovl_heights.count() > 0:
            return ovl_heights.first().Telescopes.full_overlap_height_m
        else:
            self.logger.error('wrong number of overlap heights ({0}) for channel {1}'.
                              format(ovl_heights.count(),
                                     channel_id))

    def register_mwl_file_to_db(self, meas_id, prod_id, scc_version_id, nowtime, filename):
        mwl_file = self.session.query(EldamwlProducts)\
            .filter(EldamwlProducts.filename == filename)

        db_entry = EldamwlProducts(
            measurements_id=meas_id,
            product_id=prod_id,
            scc_version_id=scc_version_id,
            inscribed_at=nowtime,
            filename=filename,
        )
        if mwl_file.count() == 0:
            self.session.add(db_entry)
        elif mwl_file.count() == 1:
            mwl_file.update({'scc_version_id': scc_version_id,
                             'inscribed_at': nowtime,
                             },
                            synchronize_session=False)
        else:
            self.logger.error('wrong number ({0}) of ELDAmwl product files in db '.format(mwl_file.count()))

        self.session.commit()

    def write_lidar_constant_in_db(self, meas_id, prod_id, chan_id, hoi_system_id, detection_wl,
                                   filename, processor_version,
                                   nowtime, profile_start, profile_end,
                                   new_lc, new_lc_sys_err, new_lc_stat_err,
                                   calibr_window_bottom, calibr_window_top,
                                   ):
        lidar_const = self.session.query(LidarConstants)\
            .filter(LidarConstants.measurements_id == meas_id)\
            .filter(LidarConstants.product_id == prod_id)\
            .filter(LidarConstants.channel_id == chan_id)\
            .filter(LidarConstants.profile_start_time == profile_start)\
            .filter(LidarConstants.profile_end_time == profile_end)\
            .filter(LidarConstants.is_latest_value == 1)

        new_db_entry = LidarConstants(
            measurements_id=meas_id,
            product_id=prod_id,
            channel_id=chan_id,
            hoi_system_id=hoi_system_id,
            inscribed_at=nowtime,
            profile_start_time=profile_start,
            profile_end_time=profile_end,
            filename=filename,
            ELDA_version=processor_version,
            lidar_const=new_lc,
            lidar_const_sys_err=new_lc_sys_err,
            lidar_const_stat_err=new_lc_stat_err,
            calibr_window_bottom=calibr_window_bottom,
            calibr_window_top=calibr_window_top,
            detection_wavelength=detection_wl,
            is_latest_value=1
        )
        if lidar_const.count() == 0:
            self.session.add(new_db_entry)
        elif lidar_const.count() == 1:
            lidar_const.update({'is_latest_value': 0,
                                },
                               synchronize_session=False)
        else:
            self.logger.error('wrong number ({0}) of lidar constants in db '.format(lidar_const.count()))

        self.session.commit()
