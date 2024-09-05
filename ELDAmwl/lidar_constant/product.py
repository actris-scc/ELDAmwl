from datetime import datetime
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from ELDAmwl.utils.constants import ELDA_MWL_VERSION
from ELDAmwl.utils.numerical import np_datetime64_to_datetime
from zope import component

import numpy as np
import xarray as xr


class LidarConstantData(object):
    """
    time series of lidar constants
    """

    ds = None
    product_id = None
    measurement_id = None
    system_id = None
    channel_id = None
    wavelength = None
    calibr_height = None
    is_from_combined_signal = None

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

        result.is_from_combined_signal = sig.is_from_depol_components
        result.measurement_id = meas_params.meas_id
        result.system_id = meas_params.system_id
        result.product_id = bsc.params.prod_id
        if sig.channel_id.size == 1:
            result.channel_id = int(sig.channel_id.values)
        else:
            result.channel_id = sig.channel_id.values
        result.wavelength = float(sig.detection_wavelength.values)

        result.ds = xr.Dataset(data_vars=dict(
            time=bsc.ds.time,
            time_bounds=bsc.ds.time_bounds,
            lidar_constant=xr.DataArray(
                np.ones((bsc.ds.dims['time'])) * np.nan,
                dims=['time']),
            lidar_constant_err=xr.DataArray(
                np.ones((bsc.ds.dims['time'])) * np.nan,
                dims=['time']),
            particle_transmission=xr.DataArray(
                np.ones((bsc.ds.dims['time'])) * np.nan,
                dims=['time']),
            particle_transmission_err=xr.DataArray(
                np.ones((bsc.ds.dims['time'])) * np.nan,
                dims=['time']),
        ))
        result.ds.load()
        return result

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    def write_to_database(self):
        db_func = component.queryUtility(IDBFunc)
        if self.is_from_combined_signal:
            return

        # find valid time slices
        valid_ts = np.where(~self.ds.lidar_constant.isnull())[0]

        channel_id = self.channel_id

        # for t in range(self.ds.dims['time']):
        for t in valid_ts:
            db_func.write_lidar_constant_in_db(self.measurement_id,
                                               self.product_id,
                                               int(channel_id),
                                               self.system_id,
                                               self.wavelength,
                                               'unknown ELDAmwl file',
                                               ELDA_MWL_VERSION,
                                               datetime.now(),
                                               np_datetime64_to_datetime(self.ds.time_bounds[t, 0].values),
                                               np_datetime64_to_datetime(self.ds.time_bounds[t, 1].values),
                                               float(self.ds.lidar_constant[t]),
                                               None,  # systematic error
                                               float(self.ds.lidar_constant_err[t]),
                                               float(self.calibr_height), float(self.calibr_height))
        # todo: find correct filename here
