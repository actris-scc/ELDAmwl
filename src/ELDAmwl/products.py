# -*- coding: utf-8 -*-
"""base classes for products"""

from addict import Dict
from ELDAmwl.base import Params
from ELDAmwl.constants import COMBINE_DEPOL_USE_CASES
from ELDAmwl.constants import EBSC
from ELDAmwl.constants import RBSC
from ELDAmwl.database.db_functions import get_general_params_query
from ELDAmwl.log import logger
from ELDAmwl.signals import Signals

import numpy as np


class Products(Signals):

    def save_to_netcdf(self):
        pass


class ProductParams(Params):

    def __init__(self):
        self.sub_params = ['general_params']
        self.general_params = None

    @property
    def prod_id_str(self):
        return str(self.general_params.prod_id)

    def assign_to_product_list(self, measurement_params):
        gen_params = self.general_params
        params_list = measurement_params.product_list
        params_table = measurement_params.product_table

        if self.prod_id_str not in params_list:
            params_list[self.prod_id_str] = self
            params_table.loc[len(params_table.index)] = \
                {'id': self.prod_id_str,
                 'wl': np.nan,
                 'type': gen_params.product_type,
                 'basic': gen_params.is_basic_product,
                 'derived': gen_params.is_derived_product,
                 'hres': gen_params.calc_with_hr,
                 'lres': gen_params.calc_with_lr,
                 'elpp_file': gen_params.elpp_file}
        else:
            df = params_table[(params_table.id == self.prod_id_str)]

            hres = df.hres[0] or gen_params.calc_with_hr
            lres = df.lres[0] or gen_params.calc_with_lr

            params_table.loc[params_table.id == self.prod_id_str, 'hres'] = hres  # noqa E501
            params_table.loc[params_table.id == self.prod_id_str, 'lres'] = lres  # noqa E501

    def is_bsc_from_depol_components(self):
        if self.general_params.product_type in [RBSC, EBSC]:
            if self.general_params.usecase in COMBINE_DEPOL_USE_CASES[self.general_params.product_type]:  # noqa E501
                return True
            else:
                return False
        else:
            return False

    def add_signal_role(self, signal):
        pass


class GeneralProductParams(Params):
    """
    general parameters for product retrievals
    """

    def __init__(self):
        # product id
        self.prod_id = None
        self.product_type = None
        self.usecase = None

        self.is_basic_product = False
        self.is_derived_product = False

        self.calc_with_hr = False
        self.calc_with_lr = False

        self.error_method = None
        self.detection_limit = None
        self.error_threshold = Dict({'low': None,
                                     'high': None})

        self.valid_alt_range = Dict({'min_height': None,
                                     'max_height': None})

        self.elpp_file = ''

        self.signals = []

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.prod_id = query.Products.ID
        result.product_type = query.Products._prod_type_ID
        result.usecase = query.Products._usecase_ID

        result.is_basic_product = query.ProductTypes.is_basic_product == 1
        result.is_derived_product = not result.is_basic_product

        result.error_threshold.low = query.ErrorThresholdsLow.value
        result.error_threshold.high = query.ErrorThresholdsHigh.value
        result.detection_limit = query.ProductOptions.detection_limit

        result.valid_alt_range.min_height = query.ProductOptions.min_height
        result.valid_alt_range.max_height = query.ProductOptions.max_height

        # the MWLproducProduct and PreparedSignalFile tables
        # are not available if query is
        # related to a simple (not mwl) product. There is no way to test
        # whether the table is inside the query collection -> just try
        try:
            result.calc_with_hr = bool(query.MWLproductProduct.create_with_hr)
            result.calc_with_lr = bool(query.MWLproductProduct.create_with_lr)
            result.elpp_file = query.PreparedSignalFile.filename
        except AttributeError:
            pass

        return result

    @classmethod
    def from_db(cls, general_params):
        if not isinstance(general_params, ProductParams):
            logger.error('')
            return None

        result = general_params.deepcopy()

        return result

    @classmethod
    def from_id(cls, prod_id):
        query = get_general_params_query(prod_id)
        result = cls.from_query(query)
        return result
