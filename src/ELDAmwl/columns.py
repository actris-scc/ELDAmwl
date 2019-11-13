# -*- coding: utf-8 -*-
"""base class for columns"""

import xarray as xr


class Columns(object):
    """
    base column class (2 dimensional)
    """

    def __init__(self):
        self.ds = xr.Dataset()
        self.station_altitude = None

    def angle_to_time_dependent_var(self, angle_var, data_var):
        """
        converts xr variables from (time dependent) angle dimension to time dimension

        Args:
            angle_var: angle var is the time dependent laser_pointing_angle_of_profiles
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

    def relative_error(self):
        return self.err[:] / self.data[:]

    @property
    def data(self):
        return self.ds.data

    @property
    def err(self):
        return self.ds.err

    @property
    def rel_err(self):
        return self.relative_error()

    @property
    def cf(self):
        return self.ds.cf

    @property
    def altitude(self):
        return self.ds.altitude  # altitude axis in m a.s.l.

    @property
    def height(self):
        return self.altitude - self.station_altitude  # height axis in m a.g.
