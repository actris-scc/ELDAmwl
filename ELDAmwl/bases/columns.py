# -*- coding: utf-8 -*-
"""base class for columns"""
from ELDAmwl.component.interface import ILogger
from ELDAmwl.utils.constants import NC_FILL_BYTE, NEG_TEST_STD_FACTOR
from ELDAmwl.utils.constants import NC_FILL_INT
from zope import component

import numpy as np
import xarray as xr


class Columns(object):
    """
    base column class (2 dimensional: (time, level))
    """

    def __init__(self):
        self.ds = xr.Dataset(
            {'data': (['time', 'level'], np.empty((0, 0))),
             'err': (['time', 'level'], np.empty((0, 0))),  # statistical error
             'sys_err_neg': (['time', 'level'], np.empty((0, 0))),
             'sys_err_pos': (['time', 'level'], np.empty((0, 0))),
             'qf': (['time', 'level'], np.empty((0, 0), dtype=np.int8)),
             'binres': (['time', 'level'], np.empty((0, 0), dtype=np.int64)),
             'time_bounds': (['time', 'nv'],
                             np.empty((0, 0), dtype=np.datetime64)),
             },
            coords={'time': (['time'], np.empty((0,), dtype=np.datetime64)),
                    'level': (['level'], np.empty((0,), dtype=np.int64)),
                    'altitude': (['time', 'level'], np.empty((0, 0))),
                    })
        self.ds.load()
        self.station_altitude = None

        self.has_sys_err = False

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    def set_invalid_point(self, time, level, qf):
        self.ds['data'][time, level] = np.nan
        self.ds['err'][time, level] = np.nan
        # self.ds['sys_err_neg'][time, level] = np.nan
        # self.ds['sys_err_pos'][time, level] = np.nan
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
            data_var: data_var is the angle dependent variable

        Returns: xarray with time dependent data

        """

        dct = {
            'dims': ('time',),
            'coords': {
                'time': {
                    'dims': angle_var.coords['time'].dims,
                    'data': angle_var.coords['time'].data,
                },
            },
        }

        if 'level' in data_var.dims:
            dct['dims'] = ('time', 'level')
            dct['coords']['level'] = {
                'dims': data_var.coords['level'].dims,
                'data': data_var.coords['level'].data,
            }  # noqa E501

        dct['attrs'] = data_var.attrs
        dct['data'] = data_var[angle_var.values.astype(int)].values

        da = xr.DataArray.from_dict(dct)
        return da

    def _relative_error(self):
        return self.err[:] / self.data[:]

    def _is_negative(self):
        return (self.data[:] + NEG_TEST_STD_FACTOR * self.err[:]) < 0

    @property
    def data(self):
        return self.ds.data

    @property
    def err(self):
        return self.ds.err

    # @property
    # def sys_err_neg(self):
    #     if self.has_sys_err:
    #         return self.ds.sys_err_neg
    #     else:
    #         return None
    #
    # @property
    # def sys_err_pos(self):
    #     if self.has_sys_err:
    #         return self.ds.sys_err_pos
    #     else:
    #         return None
    #
    @property
    def rel_err(self):
        return self._relative_error()

    @property
    def is_negative(self):
        return self._is_negative()

    @property
    def qf(self):
        return self.ds.qf

    @property
    def binres(self):
        return self.ds.binres

    @property
    def altitude(self):
        """xarray.DataArray(dimensions=time,level):
                altitude axis in m a.s.l."""
        return self.ds.altitude

    @property
    def height(self):
        """xarray.DataArray(dimensions=time,level): height axis in m a.g."""
        if 'height' in self.ds.data_vars:
            return self.ds.height
        else:
            return self.altitude - self.station_altitude

    @property
    def num_times(self):
        return self.ds.dims['time']

    @property
    def num_levels(self):
        return self.ds.dims['level']

    def first_valid_bin(self, time):
        try:
            fvb = np.where(~np.isnan(self.data[time]) & ~np.isnan(self.err[time]))[0][0]
        except IndexError:
            fvb = None
        return fvb

    def last_valid_bin(self, time):
        try:
            lvb = np.where(~np.isnan(self.data[time]) & ~np.isnan(self.err[time]))[0][-1]
        except IndexError:
            lvb = None
        return lvb

#    def height_to_bin(self, a_height):
#        # todo: try also scipy bisect
#        closest_bin = (abs(self.height - a_height)).nanargmin(dim='level')
#        return closest_bin
