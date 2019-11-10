# -*- coding: utf-8 -*-
"""Classes for lidar ratio calculation"""

from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.constants import ERROR_METHODS
from ELDAmwl.database.db_functions import read_lidar_ratio_params
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.products import ProductParams


class LidarRatioParams(ProductParams):

    def __init__(self):
        super(LidarRatioParams, self).__init__()
        self.sub_params += ['backscatter_params', 'extinction_params']
        self.bsc_prod_id = None
        self.ext_prod_id = None
        self.min_BscRatio_for_LR = None

        self.extinction_params = None
        self.backscatter_params = None

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params

        query = read_lidar_ratio_params(general_params.prod_id)
        result.bsc_prod_id = query._raman_backscatter_options_product_ID
        result.ext_prod_id = query._extinction_options_product_ID
        result.general_params.error_method = ERROR_METHODS[query._error_method_ID]  # noqa E501
        result.min_BscRatio_for_LR = query.min_BscRatio_for_LR

        bsc_general_params = result.from_id(result.bsc_prod_id)
        result.backscatter_params = BackscatterParams.from_db(bsc_general_params)  # noqa E501
        result.backscatter_params.general_params.calc_with_lr = True

        ext_general_params = result.from_id(result.ext_prod_id)
        result.extinction_params = ExtinctionParams.from_db(ext_general_params)
        result.extinction_params.general_params.calc_with_lr = True
        return result

    def assign_to_product_list(self, global_product_list):
        super(LidarRatioParams, self).assign_to_product_list(
            global_product_list,
        )
        self.backscatter_params.assign_to_product_list(global_product_list)
        self.extinction_params.assign_to_product_list(global_product_list)
