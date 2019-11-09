# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""

from attrdict import AttrDict
from ELDAmwl.base import Params
from ELDAmwl.database.db_functions import get_bsc_cal_params_query
from ELDAmwl.products import ProductParams


class BscCalibrationParams(Params):

    def __init__(self):
        super(BscCalibrationParams, self).__init__()
        self.CalRangeSearchMethod = None
        self.WindowWidth = None
        self.CalValue = None
        self.CalInterval = AttrDict({'from': None, 'to': None})

    @classmethod
    def from_db(cls, general_params):
        result = cls()

        query = get_bsc_cal_params_query(general_params.prod_id,
                                         general_params.product_type)

        result.CalRangeSearchMethod = query.BscCalibrOption._calRangeSearchMethod_ID  # noqa E501
        result.WindowWidth = query.BscCalibrOption.WindowWidth
        result.CalValue = query.BscCalibrOption.calValue
        result.CalInterval['from'] = query.BscCalibrOption.LowestHeight
        result.CalInterval['to'] = query.BscCalibrOption.TopHeight

        return result


class BackscatterParams(ProductParams):

    def __init__(self):
        super(BackscatterParams, self).__init__()
        self.sub_params += ['calibration_params']
        self.calibration_params = None

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params
        result.calibration_params = BscCalibrationParams.from_db(general_params)  # noqa E501
        return result
