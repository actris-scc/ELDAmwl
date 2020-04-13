# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.base import Params
from ELDAmwl.constants import EXT, EBSC
from ELDAmwl.constants import LR
from ELDAmwl.constants import RBSC
from ELDAmwl.data_storage import DataStorage
from ELDAmwl.database.db_functions import get_products_query
from ELDAmwl.database.db_functions import read_mwl_product_id
from ELDAmwl.database.db_functions import read_system_id
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.factory import BaseOperation
from ELDAmwl.get_basic_products import GetBasicProducts
from ELDAmwl.lidar_ratio_factories import LidarRatioParams
from ELDAmwl.log import logger
from ELDAmwl.prepare_signals import PrepareSignals
from ELDAmwl.products import GeneralProductParams
from ELDAmwl.signals import ElppData

import pandas as pd


try:
    import ELDAmwl.configs.config as cfg  # noqa E401
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg  # noqa E401

PARAM_CLASSES = {RBSC: BackscatterParams,
                 EXT: ExtinctionParams,
                 LR: LidarRatioParams}


class MeasurementParams(Params):
    """General parameters and settings of the measurement
    """
    def __init__(self, measurement_id):
        super(MeasurementParams, self).__init__()
        self.sub_params = ['measurement_params']
        self.measurement_params = Params()

        self.measurement_params.meas_id = measurement_id
        self.measurement_params.system_id = read_system_id(self.meas_id)
        self.measurement_params.mwl_product_id = read_mwl_product_id(self.system_id)  # noqa E501

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
             'hres': [],
             'lres': [],
             'elpp_file': []})\
            .astype({'id': 'str',
                     'wl': 'float',
                     'type': 'int',
                     'basic': 'bool',
                     'derived': 'bool',
                     'hres': 'bool',
                     'lres': 'bool',
                     'elpp_file': 'str'})

    def basic_products(self):
        """list of parameters of all basic products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all basic products
        """
        prod_df = self.measurement_params.product_table
        ids = prod_df['id'][prod_df.basic]
        return self.filtered_list(ids)

    def extinction_products(self):
        """list of parameters of all extinction products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all extinction products
        """
        prod_df = self.measurement_params.product_table
        ids = prod_df['id'][prod_df.type == EXT]
        return self.filtered_list(ids)

    def raman_bsc_products(self):
        """list of parameters of all Raman backscatter products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all Raman backscatter products
        """
        prod_df = self.measurement_params.product_table
        ids = prod_df['id'][prod_df.type == RBSC]
        return self.filtered_list(ids)

    def elast_bsc_products(self):
        """list of parameters of all elastic backscatter products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all elastic backscatter products
        """
        prod_df = self.measurement_params.product_table
        ids = prod_df['id'][prod_df.type == EBSC]
        return self.filtered_list(ids)

    def all_bsc_products(self):
        """list of parameters of all backscatter products

        Returns:
            list of :class:`ELDAmwl.products.ProductParams`:
            list of parameters of all backscatter products
        """
        return self.raman_bsc_products() + self.elast_bsc_products()

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
            return None

    def read_product_list(self):
        """Reads the parameter of all products of this measurement from database.

        General information on the product (id, product type, wavelength,
        is it a basic product,
        to be calculated with high / low resolution, etc.) are
        stored in the product_table (pandas.DataFrame).
        This table is used for search
        and filter operations.
        The parameters (:class:`ELDAmwl.products.ProductParams`) itself are stored in
        product_list (dict) from where
        they can be assessed by their product_id_str (str).
        """
        p_query = get_products_query(
            self.mwl_product_id,
            self.measurement_params.meas_id)
        for q in p_query:
            general_params = GeneralProductParams.from_query(q)
            prod_type = general_params.product_type
            prod_params = PARAM_CLASSES[prod_type].from_db(general_params)

            prod_params.assign_to_product_list(self.measurement_params)

    def prod_params(self, prod_type, wl):
        prod_df = self.measurement_params.product_table
        ids = prod_df['id'][(prod_df.wl == wl) & (prod_df.type == prod_type)]

        if ids > 0:
            result = []
            for idx in ids:
                result.append(self.measurement_params.product_list[idx])
            return result
        else:
            return None


class RunELDAmwl(BaseOperation):
    """
    This is the global ELDAmwl operation class
    """

    def __init__(self, measurement_id):
        super(RunELDAmwl, self).__init__()
        # todo: read current scc version
        self._params = MeasurementParams(measurement_id)
        self._data = DataStorage()

    def read_tasks(self):
        logger.info('read tasks from db')
        self.params.read_product_list()
        # todo: check params (e.g. whether all
        #  time and vert. resolutions are equal)

    def read_elpp_data(self):
        logger.info('read ELPP files')
        for p_param in self.params.basic_products():
            elpp_data = ElppData()
            elpp_data.read_nc_file(self.data, p_param)

    def prepare_signals(self):
        logger.info('prepare signals')
        PrepareSignals()(
            data_storage=self.data,
            products=self.params.basic_products(),
            ).run()

    def get_basic_products(self):
        logger.info('calc basic products ')
        GetBasicProducts()(
            data_storage=self.data,
            product_params=self.params,
            ).run()

    @property
    def data(self):
        """
        Return the global data
        :returns: a dict with all global data
        """
        return self._data
