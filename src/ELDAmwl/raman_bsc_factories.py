# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""
from addict import Dict
from copy import deepcopy

from ELDAmwl.backscatter_factories import BackscatterParams, Backscatters, BackscatterFactory, BackscatterFactoryDefault
from ELDAmwl.base import DataPoint
from ELDAmwl.constants import RAYL_LR, NC_FILL_STR
from ELDAmwl.database.db_functions import read_raman_bsc_params, read_raman_bsc_algorithm
from ELDAmwl.exceptions import NoValidDataPointsForCalibration, UseCaseNotImplemented
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.signals import Signals
from ELDAmwl.registry import registry
from ELDAmwl.log import logger
import numpy as np
import xarray as xr


class RamanBscParams(BackscatterParams):

    def __init__(self):
        super(RamanBscParams, self).__init__()
        self.raman_sig_id = None

        self.raman_bsc_method = None

    @classmethod
    def from_db(cls, general_params):
        result = super(RamanBscParams, cls).from_db(general_params)
        rbp = read_raman_bsc_params(general_params.prod_id)
        result.raman_bsc_method = rbp['ram_bsc_method']
        return result

    def add_signal_role(self, signal):
        super(RamanBscParams, self).add_signal_role(signal)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str

class RamanBackscatters(Backscatters):

    @classmethod
    def from_sigratio(cls, sigratio, p_params, calibr_window):
        """calculates RamanBackscatters from a signal ratio.

        The signals were previously prepared by PrepareBscSignals .

        Args:
            sigratio (::class:`Signals`): time series of signal ratio profiles
            p_params (::class:`RamanBackscatterParams`): calculation params of the backscatter product
            calibr_window (xarray.DataArray): variable 'backscatter_calibration_range' (time, nv: 2)
        """
        result = super(RamanBackscatters, cls).from_signal(sigratio, p_params, calibr_window)

        if calibr_window ==None:
            calibr_window = p_params.calibr_window

        times = sigratio.ds.dims['time']
        cal_first_lev = sigratio.heights_to_levels(calibr_window[:,0].values)
        cal_last_lev = sigratio.heights_to_levels(calibr_window[:,1].values)

        error_params = Dict({'err_threshold': p_params.general_params.error_threshold,
                             })

        calibr_value = DataPoint.from_data(p_params.calibration_params.CalValue, 0, 0)
        cal_params = Dict({'cal_first_lev': cal_first_lev,
                           'cal_last_lev': cal_last_lev,
                           'calibr_value': calibr_value})

        calc_routine = CalcRamanBscProfile()(prod_id=p_params.prod_id_str)

        result.ds = calc_routine.run(sigratio=sigratio.ds,
                                         error_params=error_params,
                                         calibration=cal_params)
        return result


class RamanBackscatterFactory(BackscatterFactory):
    """

    """

    name = 'RamanBackscatterFactory'

    def get_classname_from_db(self):
        return RamanBackscatterFactoryDefault.__name__


class RamanBackscatterFactoryDefault(BackscatterFactoryDefault):
    """
    derives a single instance of ::class:`RamanBackscatters`.
    """

    name = 'RamanBackscatterFactoryDefault'

    raman_sig = None

    def get_product(self):

        super(RamanBackscatterFactoryDefault, self).get_product()

        if not self.param.includes_product_merging():
            self.raman_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.raman_sig_id)

            sig_ratio = Signals.as_sig_ratio(self.elast_sig, self.raman_sig)

            # todo
            # if self.kwargs['autosmooth']:
            #     smooth_res = ExtinctionAutosmooth()(
            #         signal=raman_sig.ds,
            #         smooth_params=self.param.smooth_params,
            #     ).run()

            smoothed_sigratio = deepcopy(sig_ratio)
            # smoothed_sigratio.ds['binres'] = smooth_res
            result = RamanBackscatters.from_sigratio(smoothed_sigratio, self.param, self.calibr_window)

        return result


class CalcRamanBscProfile(BaseOperationFactory):
    """calculates Raman bsc profile from elast and Raman signals and calibration window
        Keyword Args:
            prod_id (str): id of the product
    """

    name = 'CalcRamanBscProfile'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(CalcRamanBscProfile, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for Raman bsc calculation

        Returns: name of the class for the bsc calculation
        """
        return read_raman_bsc_algorithm(self.prod_id)

    pass


class CalcRamanBscProfileViaBR(BaseOperation):
    """calculates Raman backscatter profile via BR"""

    name = 'CalcRamanBscProfileViaBR'
    sigratio = None
    error_params = None
    calibration = None

    def run(self, **kwargs):
        """calculates Raman bsc profile from elast and Raman signals and calibration window
            Keyword Args:
                sigratio (xarray.DataSet): already smoothed signal ratio with \
                                        variables 'data', 'error', 'qf', 'binres', 'mol_extinction'
                error_params (addict.Dict): with keys 'low' and 'high' = maximum allowable relative statistical error
                calibration (addict.Dict): with keys 'cal_first_lev', 'cal_last_lev', and 'calibr_value'
        """
        assert 'sigratio' in kwargs
        assert 'error_params' in kwargs
        assert 'calibration' in kwargs

        sigratio = kwargs['sigratio']
        calibration = kwargs['calibration']
        error_params = kwargs['error_params']
        rayl_bsc = sigratio.mol_extinction / RAYL_LR  # todo: make BaseOperation for RAYL_LR

        # 1) calculate calibration factor

        times = sigratio.dims['time']
        calibr_factor = np.ones(times) * np.nan
        calibr_factor_err = np.ones(times) * np.nan
        sqr_rel_calibr_err = np.ones(times) * np.nan


        for t in range(times):
            df = sigratio.data.isel({'level': range(calibration['cal_first_lev'][t],
                                                    calibration['cal_last_lev'][t]),
                                     'time': t})\
                .to_dataframe()
            mean = df.data.mean()
            sem = df.data.sem()
            rel_sem = sem / mean

            if rel_sem > error_params.err_threshold.high:
                logger.err('error of calibration factor too large')
                raise NoValidDataPointsForCalibration
            else:
                calibr_factor[t] = calibration.calibr_value.value / mean
                calibr_factor_err[t] = calibr_factor[t] * np.sqrt(np.square(rel_sem) +
                                                            np.square(calibration.calibr_value.rel_error))
                sqr_rel_calibr_err[t] = np.square(calibr_factor_err[t] / calibr_factor[t])

        cf = xr.DataArray(calibr_factor, dims=['time'], coords=[sigratio.time])
        cf_err = xr.DataArray(calibr_factor_err, dims=['time'], coords=[sigratio.time])
        sqr_cf_err = xr.DataArray(sqr_rel_calibr_err, dims=['time'], coords=[sigratio.time])

        # 2) calculate backscatter ratio
        bsc = deepcopy(sigratio)
        bsc['data'] = sigratio.data * cf
        bsc['error'] = bsc.data * np.sqrt(np.square(sigratio.err/sigratio.data)
                                                          + sqr_cf_err)

        # 3) calculate backscatter coefficient
        bsc['data'] = (bsc.data - 1.) * rayl_bsc
        bsc['error'] = abs(bsc.error * rayl_bsc)

        return bsc


class CalcRamanBscProfileAsAnsmann(BaseOperation):
    """calculates Raman backscatter profile like in ansmann et al 1992"""

    name = 'CalcRamanBscProfileAsAnsmann'
    def run(self, **kwargs):
        logger.error('This Raman bsc method is not yet implemented. '
                     'Use viaBR (id = 1) instead.')
        raise UseCaseNotImplemented()



registry.register_class(CalcRamanBscProfile,
                        CalcRamanBscProfileViaBR.__name__,
                        CalcRamanBscProfileViaBR)

registry.register_class(CalcRamanBscProfile,
                        CalcRamanBscProfileAsAnsmann.__name__,
                        CalcRamanBscProfileAsAnsmann)

registry.register_class(RamanBackscatterFactory,
                        RamanBackscatterFactoryDefault.__name__,
                        RamanBackscatterFactoryDefault)
