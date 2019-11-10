# -*- coding: utf-8 -*-
"""base classes for products"""

from attrdict import AttrDict
from ELDAmwl.base import Params
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

#    @classmethod
#    def from_db(cls, general_params):
#        pass

    def assign_to_product_list(self, product_list):
        gen_params = self.general_params
        header_list = product_list['header']
        params_list = product_list['params']
        if gen_params.prod_id not in params_list:
            params_list[gen_params.prod_id] = self
            hl = header_list.append(
                {'id': gen_params.prod_id,
                 'wl': np.nan,
                 'type': gen_params.product_type,
                 'basic': gen_params.is_basic_product,
                 'derived': gen_params.is_derived_product,
                 'hres': gen_params.calc_with_hr,
                 'lres': gen_params.calc_with_lr},
                ignore_index=True)
            product_list['header'] = hl
        else:
            hl = header_list[(header_list.id == gen_params.prod_id)]

            hres = hl.hres[0] or gen_params.calc_with_hr
            lres = hl.lres[0] or gen_params.calc_with_lr

            header_list.loc[header_list.id == 378, 'hres'] = hres
            header_list.loc[header_list.id == 378, 'lres'] = lres

            product_list['header'] = header_list


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
        self.error_threshold = AttrDict({'low': None,
                                         'high': None})

        self.valid_alt_range = AttrDict({'min_height': None,
                                         'max_height': None})

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

        # the MWLproducProduct table is not available if query is
        # related to a simple (not mwl) product. There is no way to test
        # whether the table is inside the query collection -> just try
        try:
            result.calc_with_hr = bool(query.MWLproductProduct.create_with_hr)
            result.calc_with_lr = bool(query.MWLproductProduct.create_with_lr)
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
