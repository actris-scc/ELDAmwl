# -*- coding: utf-8 -*-
"""Classes for extinction calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IExtOp
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.factories.extinction_factories.ext_slope_calculations import SignalSlope
from ELDAmwl.factories.extinction_factories.ext_vertical_resolution import ExtEffBinRes
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.utils.constants import ABOVE_MAX_ALT
from ELDAmwl.utils.constants import BELOW_OVL
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_STR
from ELDAmwl.utils.constants import RANGE_BOUNDARY

import numpy as np
import xarray as xr
import zope


class ExtinctionParams(ProductParams):

    def __init__(self):
        super(ExtinctionParams, self).__init__()
        self.raman_sig_id = None
        self.ext_method = np.nan
        self.angstroem = np.nan
        self.correct_ovl = False
        self.ovl_filename = NC_FILL_STR

    def from_db(self, general_params):
        super(ExtinctionParams, self).from_db(general_params)

        ep = self.db_func.read_extinction_params(general_params.prod_id)

        self.angstroem = ep['angstroem']
        self.correct_ovl = ep['overlap_correction']
        self.ovl_filename = ep['overlap_file']
        self.ext_method = ep['ext_method']

        self.get_error_params(ep)

    def add_signal_role(self, signal):
        super(ExtinctionParams, self)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str
        else:
            self.logger.debug('channel {0} is no Raman signal'.format(signal.channel_id_str))

    @property
    def ang_exp_asDataArray(self):
        return xr.DataArray(self.angstroem,
                            name='assumed_angstroem_exponent',
                            attrs={'long_name': 'assumed Angstroem exponent '
                                                'for the extinction '
                                                'retrieval',
                                   'units': '1'})

    @property
    def smooth_params_auto(self):
        res = super(ExtinctionParams, self).smooth_params_auto()
        # todo: get bin resolutions from actual height
        #  resolution of the used algorithm
        res.max_binres_low = 39
        res.max_binres_high = 155
        res.max_bin_delta = 2
        return res

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(ExtinctionParams, self).to_meta_ds_dict(dct)
        dct.data_vars.assumed_angstroem_exponent = self.ang_exp_asDataArray
        mwl_vars = MWLFileVarsFromDB()
        dct.data_vars.evaluation_algorithm = mwl_vars.ext_algorithm_var(self.ext_method)

        if self.correct_ovl:
            dct.attrs.overlap_correction_file = self.ovl_filename


class Extinctions(Products):
    """
    time series of extinction profiles
    """
    @classmethod
    def init(cls, signal, p_params, **kwargs):
        """creates an empty instance of Extinctions, meta data are copied from the Raman signal.

        The signal was previously prepared by PrepareExtSignals .

        Args:
            signal (Signals): time series of signal profiles
            p_params (ExtinctionParams)
        """
        result = super(Extinctions, cls).from_signal(signal, p_params, **kwargs)

        cls.calc_eff_bin_res_routine = ExtEffBinRes()(prod_id=p_params.prod_id_str)

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Extinctions, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)


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

        wl_factor = 1. / (1. + pow((em_wl / det_wl), ang_exp))

        slope['data'] = -1. * slope.data * wl_factor
        slope['err'] = slope.err * wl_factor

        return None


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

    # data_storage = None

    def get_product(self):
        self.param = self.kwargs['ext_param']
        prod_id = self.param.prod_id_str
        resolution = self.kwargs['resolution']

        if not self.param.includes_product_merging():
            # raman_sig is a deepcopy from data_storage
            raman_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.raman_sig_id)

            if self.kwargs['autosmooth']:
                smooth_res = ExtinctionAutosmooth()(
                    signal=raman_sig.ds,
                    smooth_params=self.param.smooth_params,
                ).run()

            else:
                smooth_res = self.data_storage.binres_common_smooth(prod_id, resolution)

            raman_sig.ds['binres'] = smooth_res

            empty_ext = Extinctions.init(raman_sig, self.param)

            calc_routine = CalcExtinction()(
                ext_params=self.param,
                slope_routine=SignalSlope()(prod_id=prod_id),
                slope_to_ext_routine=SlopeToExtinction(),
                raman_signal=raman_sig,
                empty_ext=empty_ext,
            )
            ext = calc_routine.run()

            if self.param.error_method == MC:
                adapter = zope.component.getAdapter(calc_routine, IMonteCarlo)
                ext.err[:] = adapter(self.param.mc_params)
            else:
                ext = ext

            del raman_sig
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

registry.register_class(SlopeToExtinction,
                        SlopeToExtinctionDefault.__name__,
                        SlopeToExtinctionDefault)

registry.register_class(CalcExtinction,
                        CalcExtinctionDefault.__name__,
                        CalcExtinctionDefault)