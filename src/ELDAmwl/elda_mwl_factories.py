# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from attrdict import AttrDict
from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.base import Params
from ELDAmwl.constants import EXT
from ELDAmwl.constants import LR
from ELDAmwl.constants import RBSC
from ELDAmwl.database.db_functions import get_products_query
from ELDAmwl.database.db_functions import read_mwl_product_id
from ELDAmwl.database.db_functions import read_system_id
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.factory import BaseOperation
from ELDAmwl.lidar_ratio_factories import LidarRatioParams
from ELDAmwl.log import logger
from ELDAmwl.products import GeneralProductParams
from ELDAmwl.signals import Signals

import numpy as np
import os
import pandas as pd
import xarray as xr


try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg

PARAM_CLASSES = {RBSC: BackscatterParams,
                 EXT: ExtinctionParams,
                 LR: LidarRatioParams}


class MeasurementParams(Params):
    """
    Those are general parameters of the measurement
    """
    def __init__(self, measurement_id):
        super(MeasurementParams, self).__init__()
        self.sub_params = ['measurement_params']
        self.measurement_params = Params()

        self.measurement_params.meas_id = measurement_id
        self.measurement_params.system_id = read_system_id(self.meas_id)
        self.measurement_params.mwl_product_id = read_mwl_product_id(self.system_id)  # noqa E501
        self.measurement_params.products = \
            AttrDict({'params': AttrDict({}),
                      'header': pd.DataFrame.from_dict({'id': [],
                                                        'wl': [],
                                                        'type': [],
                                                        'basic': [],
                                                        'derived': [],
                                                        'hres': [],
                                                        'lres': []}).
                      astype({'id': 'int',
                              'wl': 'float',
                              'type': 'int',
                              'basic': 'bool',
                              'derived': 'bool',
                              'hres': 'bool',
                              'lres': 'bool'}),
                      })

    def read_product_list(self):
        p_query = get_products_query(self.mwl_product_id, self.meas_id)
        for q in p_query:
            general_params = GeneralProductParams.from_query(q)
            prod_type = general_params.product_type
            prod_params = PARAM_CLASSES[prod_type].from_db(general_params)

            self.assign_to_product_list(prod_params)

    def assign_to_product_list(self, params):
        gen_params = params.general_params
        if gen_params.prod_id not in self.measurement_params.products.params:
            self.measurement_params.products.params[gen_params.prod_id] = params  # noqa E501
            self.measurement_params.products.header = \
                self.measurement_params.products.header.append({'id': gen_params.prod_id,  # noqa E501
                                                                'wl': np.nan,
                                                                'type': gen_params.product_type,  # noqa E501
                                                                'basic': gen_params.is_basic_product,  # noqa E501
                                                                'derived': gen_params.is_derived_product,  # noqa E501
                                                                'hres': gen_params.calc_with_hr,  # noqa E501
                                                                'lres': gen_params.calc_with_lr},  # noqa E501
                                                                ignore_index=True)  # noqa E501
        else:
            logger.notice('prod_id {0} already exists'.format(gen_params.prod_id))  # noqa E501

    def prod_params(self, prod_type, wl):
        prod_df = self.measurement_params.products.header
        ids = prod_df['id'][(prod_df.wl == wl) & (prod_df.type == prod_type)]

        if ids > 0:
            return self.measurement_params.products.params[ids]
        else:
            return None


class RunELDAmwl(BaseOperation):
    """
    This is the global ELDAmwl operation class
    """
    _data = None

    def __init__(self, measurement_id):
        super(RunELDAmwl, self).__init__()
        self._params = MeasurementParams(measurement_id)
        self._data = AttrDict()

    def read_tasks(self):
        self.params.read_product_list()
#        p = self.params.prod_params(EXT, 355)

    def read_signals(self):
        self._data['raw_signals'] = AttrDict()
        for p in self.params.products:
            p.signal_ids = []
            nc_ds = xr.open_dataset(os.path.join(cfg.SIGNAL_PATH,
                                                 p.ELPP_filename))
            for idx in range(nc_ds.dims['channel']):
                sig = Signals.from_nc_file(nc_ds, idx)
                channel_id = sig.channel_id.values[0]
                self.data.raw_signals[channel_id] = sig
                p.signal_ids.append(channel_id)

    @property
    def data(self):
        """
        Return the global data
        :returns: a dict with all global data
        """
        return self._data
