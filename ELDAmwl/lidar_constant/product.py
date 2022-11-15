from addict import Dict
from ELDAmwl.component.interface import IDataStorage
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from zope import component
from datetime import datetime

import numpy as np
import xarray as xr

from ELDAmwl.utils.constants import ELDA_MWL_VERSION
from ELDAmwl.utils.numerical import np_datetime64_to_datetime


class LidarConstants(object):
    """
    time series of lidar constants
    """

    ds = xr.Dataset()
    product_id = None
    measurement_id = None
    system_id = None
    channel_id = None
    wavelength = None
    calibr_height = None

    @classmethod
    def init(cls, bsc, sig):
        """creates an empty instance of LidarConstants, meta data are copied from bsc and sig

        Args:
            bsc (Backscatters): time series of backscatter profiles
            sig (signals): time series of signals
        """
        result = cls()

        # global measurement params
        meas_params = component.queryUtility(IParams).measurement_params

        result.measurement_id = meas_params.meas_id
        result.system_id = meas_params.system_id
        result.product_id = bsc.params.prod_id
        result.channel_id = int(sig.channel_id.values)
        result.wavelength = float(sig.detection_wavelength.values)

        result.ds['time'] = bsc.ds.time
        result.ds['time_bounds'] = bsc.ds.time_bounds
        result.ds['lidar_constant'] = xr.DataArray(
            np.ones((bsc.ds.dims['time'])) * np.nan,
            dims=['time'])
        result.ds['lidar_constant_err'] = xr.DataArray(
            np.ones((bsc.ds.dims['time'])) * np.nan,
            dims=['time'])
        result.ds['particle_transmission'] = xr.DataArray(
            np.ones((bsc.ds.dims['time'])) * np.nan,
            dims=['time'])
        result.ds['particle_transmission_err'] = xr.DataArray(
            np.ones((bsc.ds.dims['time'])) * np.nan,
            dims=['time'])

        result.ds.load()
        return result

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    def write_to_database(self):
        db_func = component.queryUtility(IDBFunc)
        for t in range(self.ds.dims['time']):
            db_func.write_lidar_constant_in_db(self.measurement_id,
                                               self.product_id,
                                               self.channel_id,
                                               self.system_id,
                                               self.wavelength,
                                               'unknown ELDAmwl file',
                                               ELDA_MWL_VERSION,
                                               datetime.now(),
                                               np_datetime64_to_datetime(self.ds.time_bounds[t,0].values),
                                               np_datetime64_to_datetime(self.ds.time_bounds[t,1].values),
                                               float(self.ds.lidar_constant[t]),
                                               None,  # systematic error
                                               float(self.ds.lidar_constant_err[t]),
                                               float(self.calibr_height), float(self.calibr_height))
        # todo: find correct filename here
