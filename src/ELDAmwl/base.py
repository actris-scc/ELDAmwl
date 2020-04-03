# -*- coding: utf-8 -*-
"""Base classes of the Operator and the Operator factory

.. moduleauthor:: Volker Jaenisch <volker.jaenisch@inqbus.de>

"""
import xarray as xr

class Params(object):
    """
    Base Params
    """
    sub_params = None

    def __init__(self):
        self.sub_params = []

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            for sp_name in object.__getattribute__(self, 'sub_params'):
                sp = object.__getattribute__(self, sp_name)
                try:
                    return object.__getattribute__(sp, item)
                except AttributeError:
                    continue

            class_name = object.__getattribute__(sp, '__class__').__name__
            raise(AttributeError('class {0} has no attribute {1}'.format(class_name, item)))  # noqa E501


class DataPoint(object):
    """a single data point
    """

    def __init__(self):
        self.data = xr.Dataset()

    @classmethod
    def from_nc_file(cls, nc_ds, variable_name, idx_in_file):
        result = cls()

        stat_err_name = variable_name + '_statistical_error'
        sys_err_name = variable_name + '_systematic_error'

        value = nc_ds.data_vars[variable_name][idx_in_file]
        stat_err = nc_ds.data_vars[stat_err_name][idx_in_file]
        sys_err = nc_ds.data_vars[sys_err_name][idx_in_file]

        dummy = xr.Dataset()
        result.data = dummy.assign({'value': value,
                                    'statistical_error': stat_err,
                                    'systematic_error': sys_err,
                                    })
        return result
