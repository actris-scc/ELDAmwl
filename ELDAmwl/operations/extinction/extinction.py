# -*- coding: utf-8 -*-
"""Classes for extinction calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IExtOp
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.operations.extinction.ext_calc_tools import SignalSlope
from ELDAmwl.operations.extinction.ext_calc_tools import SlopeToExtinction
from ELDAmwl.operations.extinction.product import Extinctions
from ELDAmwl.utils.constants import ABOVE_MAX_ALT, NC_FILL_INT
from ELDAmwl.utils.constants import BELOW_OVL
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_STR
from ELDAmwl.utils.constants import RANGE_BOUNDARY

import numpy as np
import zope


class CalcExtinction(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
    extinction coefficient from a  Raman signal. In this case, it
    will be always an instance of CalcExtinctionDefault().
    """

    name = 'CalcExtinction'

    def __call__(self, **kwargs):
        assert 'ext_params' in kwargs
        assert 'slope_routine' in kwargs
        assert 'slope_to_ext_routine' in kwargs
        assert 'raman_signal' in kwargs
        assert 'empty_ext' in kwargs

        res = super(CalcExtinction, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcExtinctionDefault' .
        """
        return 'CalcExtinctionDefault'


@zope.interface.implementer(IExtOp)
class CalcExtinctionDefault(BaseOperation):
    """
    Calculates particle extinction coefficient from Raman signal.
    """

    name = 'CalcExtinctionDefault'

    ext_params = None
    signal = None
    slope_routine = None
    slope_to_ext_routine = None
    result = None
    x_data = None
    y_data = None
    yerr_data = None
    qf_data = None

    def __init__(self, **kwargs):
        super(CalcExtinctionDefault, self).__init__(**kwargs)
        self.signal = self.kwargs['raman_signal']
        self.ext_params = self.kwargs['ext_params']
        self.slope_routine = self.kwargs['slope_routine']
        self.slope_to_ext_routine = self.kwargs['slope_to_ext_routine']
        self.result = deepcopy(self.kwargs['empty_ext'])

    def calc_slope(self, t, lev, window, half_win):
        fb = lev - half_win
        lb = lev + half_win
        window_data = Dict({'x_data': self.x_data[t, fb:lb + 1],
                            'y_data': self.y_data[t, fb:lb + 1],
                            'yerr_data': self.yerr_data[t, fb:lb + 1],
                            })

        sig_slope = self.slope_routine.run(signal=window_data)
        qf = np.bitwise_or.reduce(self.qf_data[t, fb:lb + 1])

        self.result.ds['data'][t, lev] = sig_slope.slope
        self.result.ds['err'][t, lev] = sig_slope.slope_err
        self.result.ds['qf'][t, lev] = qf
        self.result.ds['binres'][t, lev] = window

    def prepare_data(self, data):
        self.x_data = np.array(data.range)
        self.y_data = np.array(data.ds.data)
        self.yerr_data = np.array(data.ds.err)
        self.qf_data = np.array(data.ds.qf)

    def calc_single_profile(self, t, data):
        fvb = data.first_valid_bin(t)
        lvb = data.last_valid_bin(t)
        for lev in range(fvb, lvb):
            window = int(data.ds.binres[t, lev])
            half_win = window // 2

            if lev < (fvb + half_win):
                self.result.set_invalid_point(t, lev, BELOW_OVL)

            elif lev >= (lvb - half_win):
                self.result.set_invalid_point(t, lev, ABOVE_MAX_ALT)

            else:
                self.calc_slope(t, lev, window, half_win)

    def run(self, data=None):
        if data is None:
            data = self.signal

        self.prepare_data(data)

        for t in range(data.num_times):
            self.calc_single_profile(t, data)

        # extract relevant parameter for calculation of ext from signal slope
        # from ExtinctionParams into Dict
        param_dct = Dict({
            'detection_wavelength': data.detection_wavelength,
            'emission_wavelength': data.emission_wavelength,
            'angstroem_exponent': self.ext_params.ang_exp_asDataArray,
        })

        # SlopeToExtinction converts the slope into extinction coefficients
        self.slope_to_ext_routine(
            slope=self.result.ds,
            ext_params=param_dct).run()

        return self.result


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
            while (b_inc < levels - 1) and \
                    (smooth_res[t][b_inc - 1] < mbr_high):
                # (b_inc < levels -1 )
                #           => not yet end of profile
                # smooth_res[t][b_inc-1] < mbr_high
                #           => not yet binres of high altitudes

                smooth_res[t][b_inc] = smooth_res[t][b_inc - 1] + mb_delta
                b_inc += 1

            # use mbr_high for bins above transition zone
            smooth_res[t][b_inc:] = mbr_high

        return smooth_res

    def run(self):
        # todo ina: test whether this copy makes sense and is necessary
        self.signal = deepcopy(self.kwargs['signal'])
        self.smooth_params = self.kwargs['smooth_params']

        self.max_smooth()

        return self.signal.binres


class ExtinctionFactory(BaseOperationFactory):
    """
    optional argument resolution, can be LOWRES(=0) or HIGHRES(=1)
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
    param = None
    raman_sig = None
    smooth_res = None
    empty_ext = None
    prod_id = NC_FILL_STR
    resolution = NC_FILL_INT

    def get_smooth_res(self):
        if self.kwargs['autosmooth']:
            result = ExtinctionAutosmooth()(
                signal=self.raman_sig.ds,
                smooth_params=self.param.smooth_params,
            ).run()

        else:
            result = self.data_storage.binres_common_smooth(self.prod_id, self.resolution)

        self.smooth_res = result

    def prepare(self):
        self.param = self.kwargs['ext_param']
        self.prod_id = self.param.prod_id_str
        self.resolution = self.kwargs['resolution']

        # raman_sig is a deepcopy from data_storage
        self.raman_sig = self.data_storage.prepared_signal(
            self.param.prod_id_str,
            self.param.raman_sig_id)

        self.get_smooth_res()

        self.raman_sig.ds['binres'] = self.smooth_res

        self.empty_ext = Extinctions.init(self.raman_sig, self.param)

    def get_non_merge_product(self):

        calc_routine = CalcExtinction()(
            ext_params=self.param,
            slope_routine=SignalSlope()(prod_id=self.prod_id),
            slope_to_ext_routine=SlopeToExtinction(),
            raman_signal=self.raman_sig,
            empty_ext=self.empty_ext,
        )
        ext = calc_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(calc_routine, IMonteCarlo)
            ext.err[:] = adapter(self.param.mc_params)
        else:
            ext = ext

        del self.raman_sig
        return ext

    def get_product(self):
        self.prepare()

        if not self.param.includes_product_merging():
            ext = self.get_non_merge_product()
        else:
            # todo: result = Extinctions.from_merged_signals()
            ext = None
            pass

        return ext


registry.register_class(ExtinctionFactory,
                        ExtinctionFactoryDefault.__name__,
                        ExtinctionFactoryDefault)

registry.register_class(ExtinctionAutosmooth,
                        ExtinctionAutosmoothDefault.__name__,
                        ExtinctionAutosmoothDefault)

registry.register_class(CalcExtinction,
                        CalcExtinctionDefault.__name__,
                        CalcExtinctionDefault)
