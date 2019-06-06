import os

import pandas as pd
import numpy as np
import xarray as xr
from attrdict import AttrDict

from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.base import Params
from ELDAmwl.constants import EXT, RBSC
from ELDAmwl.database.db_functions import read_system_id, get_products_query, read_mwl_product_id
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.products import ProductParams
from ELDAmwl.registry import registry
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.signals import Signals
from ELDAmwl.log import logger

try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg

PARAM_CLASSES = {RBSC: BackscatterParams,
                 EXT: ExtinctionParams}

class MeasurementParams(Params):
    """
    Those are general parameters of the measurement
    """
    def __init__(self, measurement_id):
        self.sub_params = ['measurement_params']
        self.measurement_params = Params()

        self.measurement_params.meas_id = measurement_id
        self.measurement_params.system_id = read_system_id(self.meas_id)
        self.measurement_params.mwl_product_id = read_mwl_product_id(self.system_id)
        self.measurement_params.products = AttrDict({'params':AttrDict({}),
                                                     'header': pd.DataFrame.from_dict({'id': [],
                                                                                       'wl': [],
                                                                                       'type': [],
                                                                                       'basic': [],
                                                                                       'derived': [],
                                                                                       'hres': [],
                                                                                       'lres': []}).
                                                                    astype({'id': 'int',
                                                                                       'wl':'float',
                                                                                       'type':'int',
                                                                                       'basic':'bool',
                                                                                       'derived':'bool',
                                                                                       'hres':'bool',
                                                                                       'lres':'bool'})
                                                     })

    def read_product_list(self):
        p_query = get_products_query(self.mwl_product_id, self.meas_id)
        for q in p_query:
            params = ProductParams.from_query(q)
            prod_type = params.product_type
            prod_params = PARAM_CLASSES[prod_type].from_db(params)

            self.assign_to_product_list(prod_params)

    def assign_to_product_list(self, params):
        if not params.prod_id in self.measurement_params.products.params:
            self.measurement_params.products.params[params.prod_id] = params
            self.measurement_params.products.header = \
                self.measurement_params.products.header.append({'id': params.prod_id,
                                                            'wl': np.nan,
                                                            'type': params.product_type,
                                                            'basic': params.is_basic_product,
                                                            'derived': params.is_derived_product,
                                                            'hres': params.calc_with_hr,
                                                            'lres': params.calc_with_lr},
                                                               ignore_index=True)
        else:
            logger.notice('prod_id %s already exists' % (params.prod_id))


    @property
    def prod_params(self, prod_type, wl):
        prod_df = self.measurement_params.products.header
        ids = prod_df['id'][(prod_df.wl == wl) & (prod_df.type == prod_type)]

        return self.measurement_params.products.params[ids]



class RunELDAmwl(BaseOperation):
    """
    This is the global ELDAmwl operation class
    """
    _data = None

    def __init__(self, measurement_id):
        self._params = MeasurementParams(measurement_id)
        _data = AttrDict()

    def read_tasks(self):
        self.params.read_product_list()
        p = self.params.prod_params(EXT, 355)

    def read_signals(self):
        self._data['raw_signals'] = AttrDict()
        for p in self.params.products:
            p.signal_ids = []
            nc_ds = xr.open_dataset(os.path.join(cfg.SIGNAL_PATH, p.ELPP_filename))
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
