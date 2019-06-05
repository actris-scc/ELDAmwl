import os
import xarray as xr
from attrdict import AttrDict

from ELDAmwl.base import Params
from ELDAmwl.constants import EXT
from ELDAmwl.database.db_functions import read_system_id, get_products_query, read_mwl_product_id
from ELDAmwl.extinction_factories import ExtinctionParams
from ELDAmwl.products import ProductParams
from ELDAmwl.registry import registry
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.signals import Signals

try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg

PARAM_CLASSES = {EXT: ExtinctionParams}

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
        self.measurement_params.products = AttrDict({'basic':AttrDict({}),
                                                     'derived': AttrDict({})})

    def read_product_list(self):
        p_query = get_products_query(self.mwl_product_id, self.meas_id)
        for q in p_query:
            params = ProductParams.from_query(q)
            prod_type = params.product_type
            prod_params = PARAM_CLASSES[prod_type].from_db(params)

            if params.is_basic_product:
                if not prod_type in self.products.basic:
                    self.products.basic[prod_params] = []
            self.products.basic.prod_type.append(prod_params)



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
