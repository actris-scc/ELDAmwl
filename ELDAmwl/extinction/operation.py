# -*- coding: utf-8 -*-
"""Classes for extinction calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IExtOp
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.extinction.product import Extinctions
from ELDAmwl.extinction.tools.operation import ExtinctionAutosmooth
from ELDAmwl.extinction.tools.operation import SignalSlope
from ELDAmwl.extinction.tools.operation import SlopeToExtinction
from ELDAmwl.utils.constants import ABOVE_MAX_ALT
from ELDAmwl.utils.constants import BELOW_OVL
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import NC_FILL_STR

import numpy as np
import zope


class CalcExtinction(BaseOperationFactory):
    """
    creates a class for the calculation of an extinction coefficient

    Returns an instance of BaseOperation which calculates the particle
    extinction coefficient from a  Raman signal. In this case, it
    will be always an instance of CalcExtinctionDefault().

    Keyword Args:
        ext_params (:class:`ELDAmwl.extinction.params.ExtinctionParams`): \
                retrieval parameter of the extinction product
        slope_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
            _result of :class:`ELDAmwl.extinction.tools.operation.SignalSlope`
        slope_to_ext_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
            _result of :class:`ELDAmwl.extinction.tools.operation.SlopeToExtinction`
        raman_signal (:class:`ELDAmwl.signals.Signals`): Raman signal
        empty_ext (:class:`ELDAmwl.extinction.product.Extinctions`): \
                instance of Extinctions which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    _name = 'CalcExtinction'

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

    The _result is a copy of empty_ext, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        ext_params (:class:`ELDAmwl.extinction.params.ExtinctionParams`): \
                retrieval parameter of the extinction product
        slope_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
            _result of :class:`ELDAmwl.extinction.tools.operation.SignalSlope`
        slope_to_ext_routine (:class:`ELDAmwl.bases.factory.BaseOperation`):
            _result of :class:`ELDAmwl.extinction.tools.operation.SlopeToExtinction`
        raman_signal (:class:`ELDAmwl.signals.Signals`): Raman signal
        empty_ext (:class:`ELDAmwl.extinction.product.Extinctions`): \
                instance of Extinctions which has all meta data but profile data are empty arrays

    Returns:
        profiles of particle extinction coefficients(:class:`ELDAmwl.extinction.product.Extinctions`)
    """

    _name = 'CalcExtinctionDefault'

    ext_params = None
    signal = None
    slope_routine = None
    slope_to_ext_routine = None
    _result = None
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
        self._result = deepcopy(self.kwargs['empty_ext'])

    def calc_slope(self, t, lev, window, half_win):
        fb = lev - half_win
        lb = lev + half_win
        window_data = Dict({'x_data': self.x_data[t, fb:lb + 1],
                            'y_data': self.y_data[t, fb:lb + 1],
                            'yerr_data': self.yerr_data[t, fb:lb + 1],
                            })

        sig_slope = self.slope_routine.run(signal=window_data)
        qf = np.bitwise_or.reduce(self.qf_data[t, fb:lb + 1])

        self._result.ds['data'][t, lev] = sig_slope.slope
        self._result.ds['err'][t, lev] = sig_slope.slope_err
        self._result.ds['qf'][t, lev] = qf
        self._result.ds['binres'][t, lev] = window

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
                self._result.set_invalid_point(t, lev, BELOW_OVL)

            elif lev >= (lvb - half_win):
                self._result.set_invalid_point(t, lev, ABOVE_MAX_ALT)

            else:
                self.calc_slope(t, lev, window, half_win)

    def run(self, data=None):
        """
        run the extinction calculation

        The the optional keyword arg 'data' allows to feed new raman signals into
        an existing instance of CalcExtinctionDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Keyword Args:
            data (:class:`ELDAmwl.signals.Signals`): Raman signal, default=None

        Returns:
            profiles of particle extinction coefficients(:class:`ELDAmwl.extinction.product.Extinctions`)

        """
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
            slope=self._result.ds,
            ext_params=param_dct).run()

        return self._result


class ExtinctionFactory(BaseOperationFactory):
    """
    optional argument resolution, can be LOWRES(=0) or HIGHRES(=1)
    """

    _name = 'ExtinctionFactory'

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

    _name = 'ExtinctionFactoryDefault'
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
            # todo: _result = Extinctions.from_merged_signals()
            ext = None
            pass

        return ext


registry.register_class(ExtinctionFactory,
                        ExtinctionFactoryDefault.__name__,
                        ExtinctionFactoryDefault)

registry.register_class(CalcExtinction,
                        CalcExtinctionDefault.__name__,
                        CalcExtinctionDefault)
