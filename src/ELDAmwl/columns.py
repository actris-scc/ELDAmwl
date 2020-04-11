# -*- coding: utf-8 -*-
"""base class for columns"""

import numpy as np
import xarray as xr

from ELDAmwl.constants import NC_FILL_INT, NC_FILL_BYTE


class Columns(object):
    """
    base column class (2 dimensional: (time, level))
    """

    def __init__(self):
        self.ds = xr.Dataset(
            {'data': (['time', 'level'], np.empty((0, 0))),
             'err': (['time', 'level'], np.empty((0, 0))),
             'qf': (['time', 'level'], np.empty((0, 0), dtype=np.int8)),
             'binres': (['time', 'level'], np.empty((0, 0), dtype=np.int)),
             'time_bounds': (['time', 'nv'],
                             np.empty((0, 0), dtype=np.datetime64)),
             },
            coords={'time': (['time'], np.empty((0), dtype=np.datetime64)),
                    'level': (['level'], np.empty((0), dtype=np.int64)),
                    'altitude': (['time', 'level'], np.empty((0, 0)))})
        self.station_altitude = None

    def set_invalid_point(self, time, level, qf):
        self.ds['data'][time, level] = np.nan
        self.ds['err'][time, level] = np.nan
        self.ds['binres'][time, level] = NC_FILL_INT
        if self.ds.qf[time, level] != NC_FILL_BYTE:
            self.ds['qf'][time, level] = self.ds.qf[time, level] | qf
        else:
            self.ds['qf'][time, level] = qf

    def angle_to_time_dependent_var(self, angle_var, data_var):
        """
        converts xr variables from (time dependent) angle dimension
        to time dimension

        Args:
            angle_var: angle var is the time dependent
            laser_pointing_angle_of_profiles
            data_var: data_var is the angle dependent variable

        Returns: xarray with time dependent data

        """

        dict = {}
        dict['dims'] = ('time',)
        dict['coords'] = {'time': {'dims': angle_var.coords['time'].dims,
                                   'data': angle_var.coords['time'].data}}

        if 'level' in data_var.dims:
            dict['dims'] = ('time', 'level')
            dict['coords']['level'] = {'dims': data_var.coords['level'].dims,  # noqa E501
                                       'data': data_var.coords['level'].data}  # noqa E501

        dict['attrs'] = data_var.attrs
        dict['data'] = data_var[angle_var.values.astype(int)].values

        da = xr.DataArray.from_dict(dict)
        return da

    def _relative_error(self):
        return self.err[:] / self.data[:]

    @property
    def data(self):
        return self.ds.data

    @property
    def err(self):
        return self.ds.err

    @property
    def rel_err(self):
        return self._relative_error()

    @property
    def qf(self):
        return self.ds.qf

    @property
    def altitude(self):
        """xarray.DataArray(dimensions=time,level):
                altitude axis in m a.s.l."""
        return self.ds.altitude

    @property
    def height(self):
        """xarray.DataArray(dimensions=time,level): height axis in m a.g."""
        return self.altitude - self.station_altitude
