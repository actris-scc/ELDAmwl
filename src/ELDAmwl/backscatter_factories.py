# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from addict import Dict
from ELDAmwl.base import Params
from ELDAmwl.constants import RBSC
from ELDAmwl.database.db_functions import get_bsc_cal_params_query
from ELDAmwl.exceptions import BscCalParamsNotEqual
from ELDAmwl.exceptions import CalRangeHigherThanValid
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.log import logger
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry
from ELDAmwl.signals import Signals
from scipy.stats import sem

import numpy as np
import xarray as xr


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

        result.cal_range_search_method = \
            query.BscCalibrOption._calRangeSearchMethod_ID
        result.window_width = \
            float(query.BscCalibrOption.WindowWidth)
        result.cal_value = \
            float(query.BscCalibrOption.calValue)
        result.cal_interval['min_height'] = \
            float(query.BscCalibrOption.LowestHeight)
        result.cal_interval['max_height'] = \
            float(query.BscCalibrOption.TopHeight)

        return result

    def equal(self, other):
        result = True
        if (self.cal_interval.min_height != other.cal_interval.min_height) or \
                (self.cal_interval.max_height !=
                 other.cal_interval.max_height) or \
                (self.window_width != other.window_width) or \
                (self.cal_value != other.cal_value) or \
                (self.cal_range_search_method !=
                 other.cal_range_search_method):
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
            logger.error('the height interval for searching '
                         'the calibration window is '
                         'higher than the vertical range '
                         'for product calculation')
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
            signal (:class:`Signals`): time series of signal profiles
            p_params (:class:`BackscatterParams`):
                        calculation params of the backscatter product
            calibr_window (tuple):
                        first and last height of the calibration window [m]
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)
        cls.calibr_window = calibr_window

        return result


class BackscatterFactory(BaseOperationFactory):
    """
    derives a single instance of :class:`Backscatters`.
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
    derives a single instance of :class:`Backscatters`.
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
        bsc_params (list of :class:`BackscatterParams`): \
                list of params of all backscatter products
    """
    name = 'FindCommonBscCalibrWindow'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_params' in kwargs
        res = super(FindCommonBscCalibrWindow, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        return FindBscCalibrWindowAsInELDA.__name__


class FindBscCalibrWindowAsInELDA(BaseOperation):
    """find bsc calibration windows as in ELDA

    * for all bsc products and time slices independently
    * the calibration window is the minimum interval for which \
      the relative standard error of the mean is smaller than the \
      error threshold for altitudes above 2km.
    * use signal ratio in case of Raman bsc, otherwise elastic signal only
    * the results are xr.DataArrays (with variable \
      'backscatter_calibration_range') which are assigned to the individual
      BackscatterParams.calibr_window
    """

    name = 'FindBscCalibrWindowAsInELDA'

    data_storage = None
    bsc_params = None

    def run(self):
        """

        Returns: None (results are assigned to individual BackscatterParams)

        """
        self.data_storage = self.kwargs['data_storage']
        self.bsc_params = self.kwargs['bsc_params']

        # check whether all calibration params are equal
        for bp in self.bsc_params[1:]:
            if not self.bsc_params[0].calibration_params.equal(
                    bp.calibration_params):
                logger.error('calibration params of products {0} and {1} '
                             'are not equal.'.format(
                                self.bsc_params[0].prod_id,
                                bp.prod_id))
                raise BscCalParamsNotEqual

        for bp in self.bsc_params:
            el_sig = self.data_storage.prepared_signal(bp.prod_id_str,
                                                       bp.total_sig_id)
            error_threshold = bp.general_params.error_threshold.high
            w_width = (bp.calibration_params.window_width //
                       el_sig.raw_heightres).astype(int)
            ww0 = w_width[0, 0]

            if bp.general_params.product_type == RBSC:
                r_sig = self.data_storage.prepared_signal(
                    bp.prod_id_str, bp.raman_sig_id)
                sigratio = Signals.as_sig_ratio(el_sig, r_sig)
                ds = sigratio.data_in_vertical_range(
                    bp.calibration_params.cal_interval)
            else:
                ds = el_sig.data_in_vertical_range(
                    bp.calibration_params.cal_interval)

            # calculate rolling means, std errs of mean, and rel sem
            # if all window_width are equal, get means and sems at once
            if np.all(w_width == ww0):
                means = ds.data.rolling(level=ww0).reduce(np.mean)
                sems = ds.data.rolling(level=ww0).reduce(sem)

            # else do it for each time slice separately
            else:
                m_list = []
                s_list = []
                for t in range(ds.dims.time):
                    m_list.append(ds.data[t].rolling(level=w_width[t, 0]).
                                  reduce(np.mean))
                    s_list.append(ds.data[t].rolling(level=w_width[t, 0]).
                                  reduce(sem))

                means = xr.concat(m_list, 'time')
                sems = xr.concat(s_list, 'time')

            rel_sem = sems / means

            # find all means with rel_sem < error threshold:
            # rel_sem.where(rel_sem.data < error_threshold)
            #           => rel_sem values and nans
            # rel_sem.where(rel_sem.data < error_threshold) / rel_sem
            #           => ones and nans
            # valid_means = means and nans
            valid_means = (rel_sem.where(rel_sem.data < error_threshold) /
                           rel_sem * means)

            # find pos of minima, pos is the beginning of rolling window
            min_pos = np.argmin(valid_means, axis=1)
            max_pos = (min_pos[:] + w_width[:, 0])

            da = xr.DataArray(np.zeros((ds.dims['time'], ds.dims['nv'])),
                              coords=[ds.time, ds.nv],
                              dims=['time', 'nv'])
            da.name = 'backscatter_calibration_range'
            da.attrs = {'long_name': 'height range where '
                                     'calibration was calculated',
                        'units': 'm'}
            da[:, 0] = el_sig.height[:, min_pos[:]].values
            da[:, 1] = el_sig.height[:, max_pos[:]].values

            bp.calibr_window = da

        return None


registry.register_class(FindCommonBscCalibrWindow,
                        FindBscCalibrWindowAsInELDA.__name__,
                        FindBscCalibrWindowAsInELDA)

# these are virtual classes, therefore, they need no registration
# registry.register_class(BackscatterFactory,
#                         BackscatterFactoryDefault.__name__,
#                         BackscatterFactoryDefault)
