# -*- coding: utf-8 -*-
"""ELDAmwl operations"""
from addict import Dict
from ELDAmwl.backscatter.elastic.params import ElastBscParams
from ELDAmwl.backscatter.raman.params import RamanBscParams
from ELDAmwl.bases.base import Params
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.component.interface import IDataStorage
from ELDAmwl.component.interface import IParams
from ELDAmwl.depol.params import VLDRParams
from ELDAmwl.elda_mwl.get_basic_products import GetBasicProducts
from ELDAmwl.elda_mwl.get_derived_products import GetDerivedProducts
from ELDAmwl.elda_mwl.get_lidar_constants import GetLidarConstants
from ELDAmwl.elda_mwl.compile_mwl_product import GetProductMatrix
from ELDAmwl.elda_mwl.do_quality_control import QualityControl
from ELDAmwl.errors.exceptions import ProductNotUnique, ELDAmwlException
from ELDAmwl.extinction.params import ExtinctionParams
from ELDAmwl.lidar_ratio.params import LidarRatioParams
from ELDAmwl.output.write_mwl_output import WriteMWLOutput
from ELDAmwl.prepare_signals import PrepareSignals
from ELDAmwl.products import GeneralProductParams
from ELDAmwl.products import SmoothParams
from ELDAmwl.signals import ElppData
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXIT_CODE_NONE
from ELDAmwl.utils.constants import EXIT_CODE_OK
from ELDAmwl.utils.constants import EXIT_CODE_SOME
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import HIGHRES
from ELDAmwl.utils.constants import LOWRES
from ELDAmwl.utils.constants import LR
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTION_STR
from ELDAmwl.utils.constants import VLDR
from zope import component

import numpy as np
import pandas as pd
import zope


PARAM_CLASSES = {RBSC: RamanBscParams,
                 EBSC: ElastBscParams,
                 EXT: ExtinctionParams,
                 LR: LidarRatioParams,
                 VLDR: VLDRParams}


@zope.interface.implementer(IParams)
class MeasurementParams(Params):
    """General parameters and settings of the measurement
    """
    def __init__(self):
        super(MeasurementParams, self).__init__()
        self.sub_params = ['measurement_params', 'smooth_params']
        self.smooth_params = None
        self.measurement_params = None

    def load_from_db(self, meas_id):
        """ reads the parameters of a measurement from db

        Args:
            meas_id: measurement id

        Returns:

        """
        self.measurement_params = Params()
        self.measurement_params.meas_id = meas_id
        self.measurement_params.system_id = self.db_func.read_system_id(self.meas_id)
        self.measurement_params.mwl_product_id = self.db_func.read_mwl_product_id(self.system_id)  # noqa E501

        # product_list provides a link between product id and
        # the parameter object of the product
        self.measurement_params.product_list = Dict()

        # the product_table provides a table-like overview of
        # all individual products. It shall be used for search operations
        # (e.g. for all extinction products or all basic products or..)
        # the search operations are realized by filtering the DataFrame.
        # they return the corresponding product_ids.
        # Using the link between product id and parameter object from
        # the product_list, the search operations
        # will return lists of product parameter objects.
        self.measurement_params.product_table = pd.DataFrame.from_dict(
            {'id': [],
             'wl': [],
             'type': [],
             'basic': [],
             'derived': [],
             'failed': [],
             RESOLUTION_STR[HIGHRES]: [],
             RESOLUTION_STR[LOWRES]: [],
             'elpp_file': []})\
            .astype({'id': 'str',
                     'wl': 'float',
                     'type': 'int',
                     'basic': 'bool',
                     'derived': 'bool',
                     'failed': 'bool',
                     RESOLUTION_STR[HIGHRES]: 'bool',
                     RESOLUTION_STR[LOWRES]: 'bool',
                     'elpp_file': 'str'})

        self.smooth_params = SmoothParams.from_db(self.measurement_params.mwl_product_id)

    def wavelengths(self, res=None, prod_types=None):
        """unique sorted list of wavelengths of all products with resolution = res
        Args:
            res (optional): ['lowres', 'highres']
        Returns:
            list of float: unique, sorted list of wavelengths of all products with resolution = res
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]

        if res is not None:
            prod_df = prod_df[prod_df[RESOLUTION_STR[res]] == True]
        if prod_types is not None:
            if (len(prod_types) == 1) or isinstance(prod_types, int):
                prod_df = prod_df[prod_df['type'] == prod_types]
            elif len(prod_types) > 1:
                type_df = prod_df[prod_df['type'] == prod_types[0]]
                for pt in prod_types[1:]:
                    type_df = pd.concat([type_df, prod_df[prod_df['type'] == pt]])
                prod_df = type_df
            else:
                self.logger.error('empty list of product types')

        all_wls = prod_df.wl.to_numpy()

        unique_wls = np.unique(all_wls)
        return unique_wls.tolist()

    def prod_types(self, res=None):
        """unique sorted list of all product types with resolution = res

        Args:
            res (optional): ['lowres', 'highres']
        Returns:
            list of float: unique, sorted list of all product types with resolution = res
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]

        if res is not None:
            all_ptypes = prod_df['type'][prod_df[RESOLUTION_STR[res]] == True].to_numpy()   # noqa E712
        else:
            all_ptypes = prod_df.type.to_numpy()

        unique_ptypes = np.unique(all_ptypes)
        return unique_ptypes.tolist()

    def basic_products(self):
        """list of parameters of all basic products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all basic products
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df.basic]
        return self.filtered_list(ids)

    def failed_products(self):
        """list of parameters of all products which could not be derived

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all products which could not be derived
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed']]
        ids = prod_df['id']
        return self.filtered_list(ids)

    def all_products_of_res(self, res):
        """list of parameters of all products with resolution res

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all products with resolution res
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df[RESOLUTION_STR[res]]]
        return self.filtered_list(ids)

    def all_basic_products_of_wl(self, wl):
        """list of parameters of all basic products with wavelength wl

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all basic products with wavelength wl
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][(prod_df.wl == wl) & (prod_df.basic)]
        return self.filtered_list(ids)

    def extinction_products(self):
        """list of parameters of all extinction products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all extinction products
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df.type == EXT]
        return self.filtered_list(ids)

    def raman_bsc_products(self):
        """list of parameters of all Raman backscatter products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all Raman backscatter products
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df.type == RBSC]
        return self.filtered_list(ids)

    def elast_bsc_products(self):
        """list of parameters of all elastic backscatter products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all elastic backscatter products
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df.type == EBSC]
        return self.filtered_list(ids)

    def vldr_products(self):
        """list of parameters of all vldr products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all vldr products
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df.type == VLDR]
        return self.filtered_list(ids)

    def all_bsc_products(self):
        """list of parameters of all backscatter products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all backscatter products
        """
        return self.raman_bsc_products() + self.elast_bsc_products()

    def lidar_ratio_products(self):
        """list of parameters of all lidar_ratio products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all lidar ratio products
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][prod_df.type == LR]
        return self.filtered_list(ids)

    def filtered_list(self, filtered_ids):
        """ converts a filtered subset of the product_table
        into list of product parameter instances`

        Args:
            filtered_ids: filtered subset of the product_table (pd.DataFrame)

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters corresponding to the filtered_ids

        """
        if len(filtered_ids) > 0:
            result = []
            for idx in filtered_ids:
                result.append(self.measurement_params.product_list[idx])
            return result
        else:
            return []

    def count_scheduled_products(self):
        """counts the number of scheduled products.

        Each wavelength and resolution is counted as an extra product.

        Returns: (integer): number of products

        """
        prod_df = self.measurement_params.product_table
        result = prod_df[prod_df['lowres']].id.count() \
                 + prod_df[prod_df['highres']].id.count()
        return result

    def read_product_list(self):
        """Reads the parameter of all products of this measurement from database.

        General information on the product (id, product type, wavelength,
        is it a basic product,
        to be calculated with high / low resolution, etc.) are
        stored in the product_table (pandas.DataFrame).
        This table is used for search
        and filter operations.
        The parameters (:class:`ELDAmwl.products.ProductParams`)
        itself are stored in
        product_list (dict) from where
        they can be assessed by their product_id_str (str).
        """

        # read basic products first (with info on used channels, elpp files etc.)
        p_query = self.db_func.get_basic_products_query(
            self.mwl_product_id,
            self.measurement_params.meas_id)
        for q in p_query:
            general_params = GeneralProductParams.from_extended_query(q)
            prod_type = general_params.product_type
            if prod_type in PARAM_CLASSES:
                prod_params = PARAM_CLASSES[prod_type]()
                prod_params.from_db(general_params)
                prod_params.assign_to_product_list(self.measurement_params)
            else:
                self.logger.error('product type {} not yet implemented'.format(prod_type))

        # next, read derived products
        p_query = self.db_func.get_derived_products_query(self.mwl_product_id)
        if p_query is not None:
            for q in p_query:
                general_params = GeneralProductParams.from_short_query(q)
                prod_type = general_params.product_type
                if prod_type in PARAM_CLASSES:
                    prod_params = PARAM_CLASSES[prod_type]()
                    prod_params.from_db(general_params)
                    prod_params.assign_to_product_list(self.measurement_params)
                else:
                    self.logger.error('product type {} not yet implemented'.format(prod_type))


    def prod_params(self, prod_type, wl):
        """ returns a list with params of all products of type prod_type and wavelength wl
         """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][(prod_df.wl == wl) & (prod_df.type == prod_type)]

        if ids.size > 0:
            result = []
            for idx in ids:
                result.append(self.measurement_params.product_list[idx])
            return result
        else:
            return None

    def prod_param(self, prod_type, wl):
        """ returns exactly one param of the one product of type prod_type and wavelength wl
         """
        lst = self.prod_params(prod_type, wl)

        if lst is None:
            return None
        elif len(lst) == 1:
            return lst[0]
        else:
            raise ProductNotUnique(prod_type, wl)

    def prod_id(self, prod_type, wl):
        """finds the id of a given product type and wavelength

        Args:
            prod_type: int
            wl: float

        Returns:
            id (str): of the product with wavelength wl and type product_type
            None: if no product exists for wl and product_type
        """
        prod_df = self.measurement_params.product_table
        prod_df = prod_df[prod_df['failed'] == False]
        ids = prod_df['id'][(prod_df.wl == wl) & (prod_df.type == prod_type)]

        if ids.size == 1:
            return ids.values[0]
        elif ids.size >= 1:
            self.logger.warning('more than one product id for wavelength {} and produc type {}'.format(wl, prod_type))
            return None
        else:
            return None


def register_params(params=None):
    if params is None:
        params = MeasurementParams()
    component.provideUtility(params, IParams)


class RunELDAmwl(BaseOperation):
    """
    This is the global ELDAmwl operation class
    """

    def __init__(self, meas_id):
        super(RunELDAmwl, self).__init__()

        scc_version_id = self.db_func.get_scc_version_id()
        self.data_storage.set_scc_version_id(scc_version_id)
        self.params.load_from_db(meas_id)

    def read_tasks(self):
        """read from db which products shall be calculated

        """
        self.logger.info('read tasks from db')
        self.params.read_product_list()
        pc = self.params.count_scheduled_products()
        self.data_storage.set_number_of_scheduled_products(pc)

        self.logger.debug('{0} products are scheduled.'.format(pc))

        # todo: check whether the products have at
        #  least one resolution with which they shall be derived
        #  (calc_with_lr or calc_with_hr)

    def read_elpp_data(self):
        """read pre-processed signals from ELPP files

        """
        self.logger.info('read ELPP files')
        for p_param in self.params.basic_products():
            ElppData().read_nc_file(p_param)

    def prepare_signals(self):
        """prepare signal data for optical retrievals

        """
        self.logger.info('prepare signals')
        PrepareSignals()(products=self.params.basic_products()).run()

    def get_basic_products(self):
        """calculate basic products

        """
        self.logger.info('calc basic products ')
        GetBasicProducts()(product_params=self.params).run()

    def get_derived_products(self):
        """calculate derived products

        """
        self.logger.info('calc derived products ')
        GetDerivedProducts()(product_params=self.params).run()

    def get_lidar_constants(self):
        """calculate lidar constants

        """
        self.logger.info('calc lidar constants ')
        GetLidarConstants()(product_params=self.params).run()

    def get_product_matrix(self):
        """combine all products in common matrixes

        """
        self.logger.info('bring all products and cloud mask on common grid (altitude, time, wavelength) ')
        GetProductMatrix()(product_params=self.params).run()

    def quality_control(self):
        """synergystic quality control of all products

        """
        self.logger.info('synergistic quality control of all products ')
        QualityControl()(product_params=self.params).run()

    def get_return_value(self):
        """determines the return code

        Returns: 0 in case that all scheduled products have been derived,
        1 in case only some of them are derived,
        2 if no products were derived

        """
        self.logger.debug('determine return code')
        num_products = self.data_storage.number_of_derived_products()

        if num_products == self.data_storage.number_of_scheduled_products():
            self.logger.info('all scheduled products have been calculated')
            return EXIT_CODE_OK
        elif num_products > 0:
            self.logger.warning('only some of the scheduled products have been calculated')
            return EXIT_CODE_SOME
        else:
            self.logger.error('none of the scheduled products have been calculated')
            return EXIT_CODE_NONE


    def write_single_output(self):
        """write products in single nc files (old style)  - not yet implemented

        """
        self.logger.info('write products into NetCDF files ')
#        self.data.basic_product_common_smooth('377', LOWRES).save_to_netcdf()
#        for p_param in self.params.basic_products():
#            self.data.basic_product_common_smooth(p_param.prod_id_str, 'lowres').save_to_netcdf()

    def write_mwl_output(self):
        """write mwl output in single nc file

        """
        self.logger.info('write all products into one NetCDF file ')
        WriteMWLOutput()(product_params=self.params).run()

    @property
    def data(self):
        """link to global data storage
        :returns: a dict with all global data
        """
        return component.queryUtility(IDataStorage)
