from addict import Dict
from ELDAmwl.component.interface import IDataStorage
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from zope import component

import numpy as np
import xarray as xr


class LidarConstants(object):
    """
    time series of lidar constants
    """

    data = Dict()
    product_id = None
    measurement_id = None
    system_id = None

    @classmethod
    def init(cls, bsc):
        """creates an empty instance of LidarConstants, meta data are copied from bsc and
        retrieved from global data storage.

        Args:
            bsc (Backscatters): time series of backscatter profiles
        """
        result = cls()

        data_storage = component.queryUtility(IDataStorage)
        meas_params = component.queryUtility(IParams).measurement_params

        result.measurement_id = meas_params.meas_id
        result.system_id = meas_params.system_id
        result.product_id = bsc.params.prod_id
        prod_id_str = bsc.params.prod_id_str

        total_sig = data_storage.prepared_signal(prod_id_str,
                                                 bsc.params.total_sig_id_str)

        result.data['total_sig'] = xr.Dataset()
        result.data.total_sig['time'] = bsc.ds.time
        result.data.total_sig['time_bounds'] = bsc.ds.time_bounds
        result.data.total_sig['data'] = xr.DataArray(
            np.ones((bsc.ds.dims['time'])) * np.nan,
            dims=['time'])
        result.data.total_sig['err'] = result.data.total_sig.data
        result.data.total_sig.attrs['wavelength'] = float(total_sig.detection_wavelength.values)
        result.data.total_sig.attrs['channel_id'] = int(total_sig.channel_id.values)

        # if bsc.params.is_bsc_from_depol_components():

        result.data.total_sig.load()
        return result

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    def write_to_database(self):
        db_func = component.queryUtility(IDBFunc)
        db_func.write_lidar_constant_in_db()
