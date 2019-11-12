# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.base import Params
from ELDAmwl.constants import EXT
from ELDAmwl.constants import LR
from ELDAmwl.constants import RBSC
from ELDAmwl.data_storage import DataStorage
from ELDAmwl.database.db_functions import get_products_query, read_signal_filenames
from ELDAmwl.database.db_functions import read_mwl_product_id
from ELDAmwl.database.db_functions import read_system_id
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.factory import BaseOperation
from ELDAmwl.lidar_ratio_factories import LidarRatioParams
from ELDAmwl.products import GeneralProductParams
from ELDAmwl.signals import Signals
from ELDAmwl.log import logger

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
        self.measurement_params.product_list =  Dict()
        self.measurement_params.product_table = pd.DataFrame.from_dict({'id': [],
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
        prod_df = self.measurement_params.product_table
        ids = prod_df ['id'][prod_df.basic == True]
        if len(ids) > 0:
            result = []
            for idx in ids:
                result.append(self.measurement_params.product_list[idx])
            return result
        else:
            return None

    def read_product_list(self):
        p_query = get_products_query(self.mwl_product_id, self.measurement_params.meas_id)
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
        self.params.read_product_list()
        # todo: check params (e.g. whether all time and vert. resolutions are equal)

    def read_signals(self):
        for p_param in self.params.basic_products():

            # todo: check if scc version in query = current version

            nc_ds = xr.open_dataset(os.path.join(cfg.SIGNAL_PATH,
                                                 p_param.general_params.elpp_file))
            for idx in range(nc_ds.dims['channel']):
                sig = Signals.from_nc_file(nc_ds, idx)
                sig.register(self.data, p_param)

        # todo: calculate combined signals (from depol components)

    @property
    def data(self):
        """
        Return the global data
        :returns: a dict with all global data
        """
        return self._data
