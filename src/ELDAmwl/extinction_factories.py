# -*- coding: utf-8 -*-
"""Classes for extinction calculation"""
from addict import Dict
from copy import deepcopy

from ELDAmwl.configs.config_default import RANGE_BOUNDARY
from ELDAmwl.constants import MC, BELOW_OVL, ABOVE_MAX_ALT
from ELDAmwl.constants import NC_FILL_STR
from ELDAmwl.database.db_functions import read_extinction_algorithm
from ELDAmwl.database.db_functions import read_extinction_params
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.log import logger
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry

import numpy as np
import xarray as xr


class ExtinctionParams(ProductParams):

    def __init__(self):
        super(ExtinctionParams, self).__init__()
        self.raman_sig_id = None
        self.ext_method = np.nan
        self.angstroem = np.nan
        self.correct_ovl = False
        self.ovl_filename = NC_FILL_STR

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params

        ep = read_extinction_params(general_params.prod_id)

        result.angstroem = ep['angstroem']
        result.correct_ovl = ep['overlap_correction']
        result.ovl_filename = ep['overlap_file']
        result.ext_method = ep['ext_method']
        result.general_params.error_method = ep['error_method']

        return result

    def add_signal_role(self, signal):
        super(ExtinctionParams, self)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str
        else:
            logger.debug('channel {0} is no Raman signal'.
                         format(signal.channel_id_str))

    @property
    def ang_exp_asDataArray(self):
        return xr.DataArray(self.angstroem,
                            name='angstroem_exponent',
                            attrs={'long_name': 'Angstroem exponent '
                                                'for the extinction '
                                                'retrieval'})
    @property
    def smooth_params(self):
        res = super(ExtinctionParams, self).smooth_params
        # todo: get bin resolutions from actual height resolution of the used algorithm
        res.max_binres_low = 39
        res.max_binres_high = 155
        res.max_bin_delta = 2
        return res


class Extinctions(Products):
    """
    time series of extinction profiles
    """
    @classmethod
    def from_signal(cls, signal, p_params):
        """calculates Extinctions from a Raman signal.

        The signal was previously prepared by PrepareExtSignals .

        Args:
            signal (Signals): time series of signal profiles
            p_params (ExtinctionParams)
        """
        result = super(Extinctions, cls).from_signal(signal, p_params)

        ext_params = Dict({'detection_wavelength': signal.detection_wavelength,
                           'emission_wavelength': signal.emission_wavelength,
                           'angstroem_exponent': p_params.ang_exp_asDataArray,
                           })

        num_times = signal.ds.dims['time']
        num_levels = signal.ds.dims['level']

        slope_routine = SignalSlope()(prod_id=p_params.prod_id_str)

        for t in range(num_times):
            for l in range(num_levels):
                window = int(signal.ds.binres[t, l])
                half_win = window // 2

                if l < half_win:
                    result.set_invalid_point(t, l, BELOW_OVL)

                elif l >= (num_levels-half_win):
                    result.set_invalid_point(t, l, ABOVE_MAX_ALT)

                else:
                    fb = l - half_win
                    lb = l + half_win
                    level_idx = xr.DataArray(range(fb, lb+1), dims=['level'])
                    window_data = signal.ds.isel(time=[t], level=level_idx)

                    sig_slope = slope_routine.run(signal=window_data)

                    result.ds['data'][t,l] = sig_slope.data
                    result.ds['err'][t,l] = sig_slope.err
                    result.ds['qf'][t,l] = sig_slope.qf
                    result.ds['binres'][t,l] = window


        result.ds = SlopeToExtinction()(slope=result.ds,
                                        ext_params=ext_params).run()

        return result


class SlopeToExtinction(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
    extinction coefficient from signal slope. In this case, it
    will be always an instance of SlopeToExtinctionDefault().
    """

    name = 'SlopeToExtinction'

    def __call__(self, **kwargs):
        assert 'slope' in kwargs
        assert 'ext_params' in kwargs
        res = super(SlopeToExtinction, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'SlopeToExtinctionDefault' .
        """
        return 'SlopeToExtinctionDefault'


class SlopeToExtinctionDefault(BaseOperation):
    """
    Calculates particle extinction coefficient from signal slope.
    """

    name = 'SlopeToExtinctionDefault'

    def run(self):
        """
        """
        slope = self.kwargs['slope']
        ext_params = self.kwargs['ext_params']

        det_wl = ext_params.detection_wavelength
        em_wl = ext_params.emission_wavelength
        ang_exp = ext_params.angstroem_exponent

        wl_factor = 1. / (1. + pow((em_wl/det_wl), ang_exp))

        result = deepcopy(slope)
        result['data'] = -1. * slope.data * wl_factor
        result['err'] = slope.err * wl_factor

        return result


class ExtinctionAutosmooth(BaseOperationFactory):
    """
    Args:
        signal: xarray.Dataset with variables
         * data
         * err
         * qf
         and coordinates time and altitude
        smooth_params: Dict with keys:
         * error_threshold_low
         * error_threshold_high
         * detection_limit
         each of them is xarray.DataArray
    """
    name = 'ExtinctionAutosmooth'

    def __call__(self, **kwargs):
        assert 'signal' in kwargs
        assert 'smooth_params' in kwargs
        res = super(ExtinctionAutosmooth, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'ExtinctionAutosmoothDefault' .
        """
        return ExtinctionAutosmoothDefault.__name__


class ExtinctionAutosmoothDefault(BaseOperation):
    """
    derives optimum vertical resolution of the extinction retrieval.
    """

    name = 'ExtinctionAutosmoothDefault'

    signal = None
    smooth_params = None

    def max_smooth(self):
        smooth_res = self.signal['binres']

        mbr_low = self.smooth_params.max_binres_low
        mbr_high = self.smooth_params.max_binres_high
        mb_delta = self.smooth_params.max_bin_delta

        times = self.signal.dims['time']
        levels = self.signal.dims['level']

        for t in range(times):
            low_bins = np.where(self.signal.altitude[t] < RANGE_BOUNDARY)

            # use mbr_low for bins below RANGE_BOUNDARY
            smooth_res[t, low_bins[0]] = mbr_low

            # continuously increase bin resolution (transition zone)
            b_inc = low_bins[0][-1] + 1
            while (b_inc < levels -1) and \
                    (smooth_res[t][b_inc-1] < mbr_high):
                # (b_inc < levels -1 ) => not yet end of profile
                # smooth_res[t][b_inc-1] < mbr_high => not yet binres of high altitudes

                smooth_res[t][b_inc] = smooth_res[t][b_inc-1] + mb_delta
                b_inc += 1

            # use mbr_high for bins above transition zone
            smooth_res[t][b_inc : ] = mbr_high

        return smooth_res

    def run(self):
        self.signal = deepcopy(self.kwargs['signal'])
        self.smooth_params = self.kwargs['smooth_params']

        self.max_smooth()


        return self.signal.binres


class ExtinctionFactory(BaseOperationFactory):
    """

    """

    name = 'ExtinctionFactory'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'ext_param' in kwargs
        assert 'autosmooth' in kwargs
        res = super(ExtinctionFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'ExtinctionFactoryDefault' .
        """
        return ExtinctionFactoryDefault.__name__


class ExtinctionFactoryDefault(BaseOperation):
    """
    derives particle extinction coefficient.
    """

    name = 'ExtinctionFactoryDefault'

    data_storage = None

    def get_product(self):
        self.data_storage = self.kwargs['data_storage']
        self.param = self.kwargs['ext_param']

        if not self.param.includes_product_merging():
            raman_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.raman_sig_id)

            if self.kwargs['autosmooth']:
                smooth_res = ExtinctionAutosmooth()(
                    signal=raman_sig.ds,
                    smooth_params=self.param.smooth_params,
                ).run()

            smoothed_sig = deepcopy(raman_sig)
            smoothed_sig.ds['binres'] = smooth_res
            result = Extinctions.from_signal(smoothed_sig, self.param)
        else:
            # result = Extinctions.from_merged_signals()
            pass

        if self.param.error_method == MC:
            pass

        return result


class SignalSlope(BaseOperationFactory):
    """
    Calculates signal slope.
    """

    name = 'SignalSlope'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']

        res = super(SignalSlope, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        return read_extinction_algorithm(self.prod_id)


class LinFit(BaseOperation):
    """

    """
    name = 'LinFit'

    data = None

    def run(self, **kwargs):
        assert 'signal' in kwargs
        self.data = kwargs['signal']
        # data have dimensions (time, level), but the length
        # of the time dimension is always 1. Therefore, use always
        # the time slice with index 0

        sig = np.array(self.data.data)[0]
        range_axis = np.array(self.data.altitude * np.cos(np.deg2rad(self.data.laser_pointing_angle)))[0]
        qf = np.array(self.data.qf)[0]

        if self.kwargs['weight']:
            weight = np.array(1/self.data.err)[0]
        else:
            weight = None

        fit = np.polyfit(range_axis, sig, 1, w=weight, cov='unscaled')
        # np.polyfit(x, y, deg, w=weight)
        # weight: For gaussian uncertainties, use 1/sigma.
        # These settings (w= 1/err, cov='unscaled')correspond
        # to the equations from numerical
        # recipes which are implemented in the old ELDA
        #
        # fit[0]: Polynomial coefficients, highest power first
        # fit[1]: The covariance matrix of the polynomial
        #           coefficient estimates. The diagonal of this
        #           matrix are the variance estimates for
        #           each coefficient

        result = Dict({'data': fit[0][0],
                       'err': np.sqrt(fit[1])[0,0],
                       'qf': np.bitwise_or.reduce(qf),
                       })

        return result



class WeightedLinearFit(BaseOperation):
    """

    """
    name = 'WeightedLinearFit'

    def __init__(self, **kwargs):
        super(WeightedLinearFit, self).__init__(**kwargs)
        self.fit = LinFit(weight=True)

    def run(self, **kwargs):
        assert 'signal' in kwargs

        return self.fit.run(signal=kwargs['signal'])


class NonWeightedLinearFit(BaseOperation):
    """

    """
    name = 'NonWeightedLinearFit'

    def __init__(self, **kwargs):
        super(NonWeightedLinearFit, self).__init__(**kwargs)
        self.fit = LinFit(weight=False)

    def run(self, **kwargs):
        assert 'signal' in kwargs
        return self.fit.run(signal=kwargs['signal'])


registry.register_class(SignalSlope,
                        NonWeightedLinearFit.__name__,
                        NonWeightedLinearFit)

registry.register_class(SignalSlope,
                        WeightedLinearFit.__name__,
                        WeightedLinearFit)

registry.register_class(ExtinctionFactory,
                        ExtinctionFactoryDefault.__name__,
                        ExtinctionFactoryDefault)

registry.register_class(ExtinctionAutosmooth,
                        ExtinctionAutosmoothDefault.__name__,
                        ExtinctionAutosmoothDefault)

registry.register_class(SlopeToExtinction,
                        SlopeToExtinctionDefault.__name__,
                        SlopeToExtinctionDefault)
