# -*- coding: utf-8 -*-
"""base class for columns"""
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.component.interface import ILogger
from ELDAmwl.depol.depol_calibration_data import DepolarizationCalibration
from ELDAmwl.utils.constants import NC_FILL_BYTE, NEG_TEST_STD_FACTOR, ALL_OK
from ELDAmwl.utils.constants import NC_FILL_INT
from zope import component

import numpy as np
import xarray as xr


class Columns(object):
    """
    base column class (2 dimensional: (time, level))
    """

    _has_sys_err : bool = None
    profile_qf : xr.DataArray = None

    def __init__(self):
        self.ds = xr.Dataset(
            data_vars=dict(
                data=(['time', 'level'], np.empty((0,0))),
                err=(['time', 'level'], np.empty((0,0))),
                sys_err_neg=(['time', 'level'], np.empty((0, 0))),
                sys_err_pos=(['time', 'level'], np.empty((0, 0))),
                qf=(['time', 'level'], np.empty((0, 0), dtype=np.int8)),
                binres=(['time', 'level'], np.empty((0, 0), dtype=np.int64)),
                time_bounds=(['time', 'nv'], np.empty((0, 0), dtype='datetime64[ns]')),
            ),
            coords=dict(
                time=(['time'], np.empty((0,))),
                level=(['level'], np.empty((0,))),
                altitude=(['time', 'level'], np.empty((0, 0))),
                ),
            )

        self.ds.load()
        self.station_altitude = None

        self._has_sys_err = False

    def copy(self, target=None):
        if target is None:
            new = Columns()
        else:
            new = target
        new.ds = self.ds.copy(deep=True)
        new.has_sys_err = self._has_sys_err
        new.profile_qf = self.profile_qf.copy(deep=True)
        return new

    def __eq__(self, other):
        self_vars = vars(self)
        other_vars = vars(other)

        for attr, self_val in self_vars.items():
            other_val = other_vars[attr]

            # handle specifically xarray.Dataset/DataArray
            if isinstance(self_val, (xr.Dataset, xr.DataArray)):
                if not self_val.equals(other_val):
                    return False
            elif isinstance(self_val, np.ndarray):
                if not (self_val == other_val).all():
                    return False
            elif isinstance(self_val, DataPoint):
                if self_val != other_val:
                    return False
            elif isinstance(self_val, DepolarizationCalibration):
                if self_val != other_val:
                    return False
            else:
                # compare as usual for other types
                if self_val != other_val:
                    return False

        return True

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    def set_invalid_profile(self, time):
        self.ds['data'][time,:] = np.nan
        self.ds['err'][time, :] = np.nan
        self.ds['binres'][time, :] = NC_FILL_INT

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
        return abs(self.err[:] / self.data[:])

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
    def has_sys_err(self):
        if self._has_sys_err:
            if 'sys_err_neg' in self.ds.keys():
                if (np.isnan(self.ds.sys_err_neg).all() or
                    np.isnan(self.ds.sys_err_pos).all()):
                    return False
                else:
                    return True
            else:
                return False
        else:
            return False

    @has_sys_err.setter
    def has_sys_err(self, value):
        self._has_sys_err = value

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
