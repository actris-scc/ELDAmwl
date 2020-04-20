# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from copy import deepcopy
from addict import Dict
from ELDAmwl.base import Params
from ELDAmwl.constants import MC
from ELDAmwl.database.db_functions import get_bsc_cal_params_query
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.log import logger
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry
import xarray as xr
import numpy as np

class BscCalibrationParams(Params):

    def __init__(self):
        super(BscCalibrationParams, self).__init__()
        self.CalRangeSearchMethod = None
        self.WindowWidth = None
        self.CalValue = None
        self.CalInterval = Dict({'from': None, 'to': None})

    @classmethod
    def from_db(cls, general_params):
        result = cls()

        query = get_bsc_cal_params_query(general_params.prod_id,
                                         general_params.product_type)

        result.CalRangeSearchMethod = query.BscCalibrOption._calRangeSearchMethod_ID  # noqa E501
        result.WindowWidth = query.BscCalibrOption.WindowWidth
        result.CalValue = query.BscCalibrOption.calValue
        result.CalInterval['from'] = query.BscCalibrOption.LowestHeight
        result.CalInterval['to'] = query.BscCalibrOption.TopHeight

        return result


class BackscatterParams(ProductParams):

    def __init__(self):
        super(BackscatterParams, self).__init__()
        self.sub_params += ['calibration_params']
        self.calibration_params = None
        self.total_sig_id = None
        self.transm_sig_id = None
        self.refl_sig_id = None
        self.cross_sig_id = None
        self.parallel_sig_id = None

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params
        result.calibration_params = BscCalibrationParams.from_db(general_params)  # noqa E501
        return result

    def add_signal_role(self, signal):
        super(BackscatterParams, self)
        if signal.is_elast_sig:
            if signal.is_total_sig:
                self.total_sig_id = signal.channel_id_str
            if signal.is_cross_sig:
                self.cross_sig_id = signal.channel_id_str
            if signal.is_parallel_sig:
                self.parallel_sig_id = signal.channel_id_str
            if signal.is_transm_sig:
                self.transm_sig_id = signal.channel_id_str
            if signal.is_refl_sig:
                self.refl_sig_id = signal.channel_id_str
        else:
            logger.debug('channel {0} is no elast signal'.
                         format(signal.channel_id_str))


class Backscatters(Products):
    """
    time series of backscatter profiles
    """

    calibr_window = None

    @classmethod
    def from_signal(cls, signal, p_params, calibr_window):
        """calculates Backscatters from an elastic signal.

        The signal was previously prepared by PrepareBscSignals .

        Args:
            signal (::class:`Signals`): time series of signal profiles
            p_params (::class:`BackscatterParams`): calculation params of the backscatter product
            calibr_window (tuple): first and last height of the calibration window [m]
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)
        cls.calibr_window = calibr_window

        return result


class BackscatterFactory(BaseOperationFactory):
    """
    derives a single instance of ::class:`Backscatters`.
    """

    name = 'BackscatterFactory'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_param' in kwargs
        assert 'autosmooth' in kwargs
        assert 'calibr_window' in kwargs
        res = super(BackscatterFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        pass


class BackscatterFactoryDefault(BaseOperation):
    """
    derives a single instance of ::class:`Backscatters`.
    """

    name = 'BackscatterFactoryDefault'

    data_storage = None
    elast_sig = None
    calibr_window = None

    def get_product(self):
        self.data_storage = self.kwargs['data_storage']
        self.param = self.kwargs['bsc_param']
        self.calibr_window = self.kwargs['calibr_window']

        if not self.param.includes_product_merging():
            self.elast_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.total_sig_id)


class FindCommonBscCalibrWindow(BaseOperationFactory):
    """ fins a common calibration window for all bsc products

    Keyword Args:
        data_storage
        bsc_params (list of ::class:`BackscatterParams`): \
                list of params of all backscatter products
    """
    name = 'FindCommonBscCalibrWindow'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_params' in kwargs
        res = super(FindCommonBscCalibrWindow, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        return FindCommonBscCalibrWindowDefault.__name__


class FindCommonBscCalibrWindowDefault(BaseOperation):

    name = 'FindCommonBscCalibrWindowDefault'

    data_storage = None
    bsc_params = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.bsc_params = self.kwargs['bsc_params']

        # todo: these are fake values => implement real algorithm

        sig = self.data_storage.prepared_signal(self.bsc_params[0].prod_id_str,
                                                self.bsc_params[0].total_sig_id).ds
        da = xr.DataArray(np.zeros((sig.dims['time'], sig.dims['nv'])),
                              coords= [sig.time, sig.nv],
                              dims=['time', 'nv'])
        da.name = 'backscatter_calibration_range'
        da.attrs = {'long_name': 'height range where calibration was calculated',
                                     'units': 'm'}
        da[:,0] = 11000.
        da[:,1] = 12000.

        return da


registry.register_class(FindCommonBscCalibrWindow,
                        FindCommonBscCalibrWindowDefault.__name__,
                        FindCommonBscCalibrWindowDefault)

# these are virtual classes, therefore, they need no registration
# registry.register_class(BackscatterFactory,
#                         BackscatterFactoryDefault.__name__,
#                         BackscatterFactoryDefault)

