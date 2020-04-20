# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from copy import deepcopy
from addict import Dict
from ELDAmwl.base import Params
from ELDAmwl.constants import MC, RBSC
from ELDAmwl.database.db_functions import get_bsc_cal_params_query
from ELDAmwl.exceptions import CalRangeHigherThanValid, BscCalParamsNotEqual
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.log import logger
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry
import xarray as xr
import numpy as np

from ELDAmwl.signals import Signals


class BscCalibrationParams(Params):

    def __init__(self):
        super(BscCalibrationParams, self).__init__()
        self.cal_range_search_method = None
        self.WindowWidth = None
        self.cal_value = None
        self.cal_interval = Dict({'min_height': None,
                                 'max_height': None})

    @classmethod
    def from_db(cls, general_params):
        result = cls()

        query = get_bsc_cal_params_query(general_params.prod_id,
                                         general_params.product_type)

        result.cal_range_search_method = query.BscCalibrOption._calRangeSearchMethod_ID  # noqa E501
        result.window_width = query.BscCalibrOption.WindowWidth
        result.cal_value = query.BscCalibrOption.calValue
        result.cal_interval['min_height'] = float(query.BscCalibrOption.LowestHeight)
        result.cal_interval['max_height'] = float(query.BscCalibrOption.TopHeight)

        return result

    def equal(self, other):
        result = True
        if (self.cal_interval.min_height != other.cal_interval.min_height) or \
            (self.cal_interval.max_height != other.cal_interval.max_height) or \
            (self.window_width != other.window_width) or \
            (self.cal_value != other.cal_value) or \
            (self.cal_range_search_method != other.cal_range_search_method):
            result = False

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
        if result.calibration_params.cal_interval.max_height > \
                result.general_params.valid_alt_range.max_height:
            logger.error('the height interval for searching the calibration window is '
                         'higher than the vertical range for product calculation')
            raise CalRangeHigherThanValid

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
        return FindCommonBscCalibrWindowAsInELDA.__name__


class FindCommonBscCalibrWindowAsInELDA(BaseOperation):

    name = 'FindCommonBscCalibrWindowAsInELDA'

    data_storage = None
    bsc_params = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.bsc_params = self.kwargs['bsc_params']

        # check whether all calibration params are equal
        for bp in self.bsc_params[1:]:
            if not self.bsc_params[0].calibration_params.equal(bp.calibration_params):
                logger.error('calibration params of products {0} and {1} '
                             'are not equal.'.format(self.bsc_params[0].prod_id, bp.prod_id))
                raise BscCalParamsNotEqual

        for bp in self.bsc_params:
            el_sig = self.data_storage.prepared_signal(bp.prod_id_str, bp.total_sig_id)

            if bp.general_params.product_type == RBSC:
                r_sig = self.data_storage.prepared_signal(bp.prod_id_str, bp.raman_sig_id)
                sigratio = Signals.as_sig_ratio(el_sig, r_sig)
                ds = sigratio.data_in_vertical_range(bp.calibration_params.cal_interval)
            else:
                ds = el_sig.data_in_vertical_range(bp.calibration_params.cal_interval)

            #df = ds.data.rolling(level=10).construct('window').to_dataframe(name= 'data')

            # calculate rolling means, stddevs, and rel stddevs
            means= ds.data.rolling(level=10).reduce(np.mean)
            std = ds.data.rolling(level=10).reduce(np.std)
            rel_std = std / means

            # find all means with rel_std < error threshold
            # rel_std.where(rel_std.data < 0.1) => std values and nans
            # rel_std.where(rel_std.data < 0.1) / rel_std => ones and nans
            # valid_means = means and nans
            valid_means = (rel_std.where(rel_std.data < 0.1) / rel_std * means)

            # find pos of minima, pos is the beginning of rolling window
            min_pos = np.argmin(valid_means, axis=1)


                # df = sigratio.data.isel({'level': range(calibration['cal_first_lev'][t],
                #                                         calibration['cal_last_lev'][t]),
                #                          'time': t}) \
                #     .to_dataframe()
                # mean = df.data.mean()
                # sem = df.data.sem()
                # rel_sem = sem / mean
                #
                # if rel_sem > error_params.err_threshold.high:

        # todo: these are fake values => implement real algorithm

        da = xr.DataArray(np.zeros((ds.dims['time'], ds.dims['nv'])),
                              coords=[ds.time, ds.nv],
                              dims=['time', 'nv'])
        da.name = 'backscatter_calibration_range'
        da.attrs = {'long_name': 'height range where calibration was calculated',
                                     'units': 'm'}
        da[:,0] = 11000.
        da[:,1] = 12000.

        return da


registry.register_class(FindCommonBscCalibrWindow,
                        FindCommonBscCalibrWindowAsInELDA.__name__,
                        FindCommonBscCalibrWindowAsInELDA)

# these are virtual classes, therefore, they need no registration
# registry.register_class(BackscatterFactory,
#                         BackscatterFactoryDefault.__name__,
#                         BackscatterFactoryDefault)

