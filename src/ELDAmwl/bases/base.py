# -*- coding: utf-8 -*-
"""Base classes of the Operator and the Operator factory

.. moduleauthor:: Volker Jaenisch <volker.jaenisch@inqbus.de>

"""
import xarray as xr
from zope import component

from ELDAmwl.component.interface import ILogger, IDBFunc


class Params(object):
    """
    Base Params
    """

    def __init__(self):
        self.sub_params = []
        self.db_func = component.queryUtility(IDBFunc)
        self.logger = component.queryUtility(ILogger)

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            sp = None
            for sp_name in object.__getattribute__(self, 'sub_params'):
                sp = object.__getattribute__(self, sp_name)
                try:
                    return object.__getattribute__(sp, item)
                except AttributeError:
                    continue

            if sp is not None:
                class_name = object.__getattribute__(sp, '__class__').__name__
            else:
                class_name = object.__getattribute__(self, '__class__').__name__
            msg = 'class {} has no attribute {}'.format(class_name, item)
            raise AttributeError(msg)


class DataPoint(object):
    """a single data point
    """

    def __init__(self):
        self.data = xr.Dataset()

    @classmethod
    def from_data(cls, value, stat_err, sys_err):
        result = cls()

        dummy = xr.Dataset()
        result.data = dummy.assign({'value': value,
                                    'statistical_error': stat_err,
                                    'systematic_error': sys_err,
                                    })
        result.data.load()
        return result

    @classmethod
    def from_nc_file(cls, nc_ds, variable_name, idx_in_file):

        stat_err_name = variable_name + '_statistical_error'
        sys_err_name = variable_name + '_systematic_error'

        value = nc_ds.data_vars[variable_name][idx_in_file]
        stat_err = nc_ds.data_vars[stat_err_name][idx_in_file]
        sys_err = nc_ds.data_vars[sys_err_name][idx_in_file]

        result = cls.from_data(value, stat_err, sys_err)

        return result

    @property
    def rel_error(self):
        return self.stat_error / self.value

    @property
    def value(self):
        return float(self.data.value)

    @property
    def stat_error(self):
        return float(self.data.statistical_error)

    @property
    def sys_error(self):
        return float(self.data.systematic_error_error)


class ELDABase:

    def __init__(self):
        self.logger = component.queryUtility(ILogger)
