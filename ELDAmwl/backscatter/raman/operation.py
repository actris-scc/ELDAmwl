# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.backscatter.common.operation import BackscatterFactory
from ELDAmwl.backscatter.common.operation import BackscatterFactoryDefault
from ELDAmwl.backscatter.raman.product import RamanBackscatters
from ELDAmwl.backscatter.raman.tools.operation import CalcRamanBscProfile
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.interface import IRamBscOp
from ELDAmwl.component.registry import registry
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import MC

import zope


class RamanBackscatterFactoryDefault(BackscatterFactoryDefault):
    """
    derives a single instance of :class:`RamanBackscatters`.

    This factory class handles the different use cases.
    """

    _name = 'RamanBackscatterFactoryDefault'

    raman_sig = None
    sig_ratio = None

    def prepare(self):
        super(RamanBackscatterFactoryDefault, self).prepare()
        if not self.param.includes_product_merging():
            self.raman_sig = self.data_storage.prepared_signal(
                self.prod_id,
                self.param.raman_sig_id)

            self.sig_ratio = Signals.as_sig_ratio(self.elast_sig, self.raman_sig)

        self.empty_bsc = RamanBackscatters.init(
            self.sig_ratio, self.param, self.calibr_window)

    def get_non_merge_product(self):

        bsc_retrieval_routine = CalcRamanBackscatter()(
            bsc_params=self.param,
            calc_routine=CalcRamanBscProfile()(prod_id=self.prod_id),
            calibr_window=self.calibr_window,
            signal_ratio=self.sig_ratio,
            empty_bsc=self.empty_bsc,
        )
        bsc = bsc_retrieval_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(bsc_retrieval_routine, IMonteCarlo)
            bsc.err[:] = adapter(self.param.mc_params)
        else:
            bsc = bsc

        del self.sig_ratio
        del self.raman_sig

        return bsc


@zope.interface.implementer(IRamBscOp)
class CalcRamanBackscatterDefault(BaseOperation):
    """
    Calculates particle backscatter coefficient from Raman signal.

    The result is a copy of empty_bsc, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        bsc_params (:class:`ELDAmwl.backscatter.raman.params.RamanBscParams`): \
                retrieval parameter of the backscatter product
        calibr_window (xarray.DataArray): variable 'backscatter_calibration_range' (time: 2, nv: 2) \
                contains bottom and top height of calibration window for each time slice
        calc_routine (:class:`ELDAmwl.bases.factory.BaseOperation`): result of :class:`ELDAmwl.backscatter.raman.tools.operation.CalcRamanBscProfile`
        signal_ratio (:class:`ELDAmwl.signals.Signals`): signal ratio
        empty_bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): \
                instance of RamanBackscatters which has all meta data but profile data are empty arrays

    Returns:
        profiles of particle backscatter coefficients (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`)

    """

    _name = 'CalcRamanBackscatterDefault'

    bsc_params = None
    sigratio = None
    calibr_window = None
    calc_routine = None
    result = None

    def __init__(self, **kwargs):
        super(CalcRamanBackscatterDefault, self).__init__(**kwargs)
        self.sigratio = self.kwargs['signal_ratio']
        self.calibr_window = self.kwargs['calibr_window']
        self.calc_routine = self.kwargs['calc_routine']
        self.bsc_params = self.kwargs['bsc_params']
        self.result = deepcopy(self.kwargs['empty_bsc'])

    def run(self, data=None):
        """
        run the Raman backscatter calculation

        The the optional keyword arg 'data' allows to feed new signal ratios into
        an existing instance of CalcRamanBackscatterDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Keyword Args:
            data (:class:`ELDAmwl.signals.Signals`): signal ratios, default=None

        Returns:
            profiles of particle backscatter coefficients(:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`)

        """
        if data is None:
            data = self.sigratio

        cal_first_lev = data.heights_to_levels(
            self.calibr_window[:, 0])
        cal_last_lev = data.heights_to_levels(
            self.calibr_window[:, 1])

        # extract relevant parameter for calculation of raman backscatter
        # from BackscatterParams into Dict

        calibr_value = DataPoint.from_data(
            self.bsc_params.calibration_params.cal_value, 0, 0)
        cal_params = Dict({'cal_first_lev': cal_first_lev.values,
                           'cal_last_lev': cal_last_lev.values,
                           'calibr_value': calibr_value})

        error_params = Dict({'err_threshold':
                            self.bsc_params.quality_params.error_threshold,
                             })

        self.result.ds = self.calc_routine.run(
            sigratio=data.ds,
            error_params=error_params,
            calibration=cal_params)

        return self.result


class RamanBackscatterFactory(BackscatterFactory):
    """

    """

    _name = 'RamanBackscatterFactory'

    def get_classname_from_db(self):
        return RamanBackscatterFactoryDefault.__name__


class CalcRamanBackscatter(BaseOperationFactory):
    """
    creates a Class for the calculation of a Raman backscatter coefficient

    Returns an instance of BaseOperation which calculates the particle
    backscatter coefficient from a Raman and an elastic signal. In this case, it
    will be always an instance of CalcRamanBackscatterDefault.

    Keyword Args:
        bsc_params (:class:`ELDAmwl.backscatter.raman.params.RamanBscParams`): \
                retrieval parameter of the backscatter product
        calibr_window (xarray.DataArray): variable 'backscatter_calibration_range' (time: 2, nv: 2) \
                contains bottom and top height of calibration window for each time slice
        calc_routine (:class:`ELDAmwl.bases.factory.BaseOperation`): result of :class:`ELDAmwl.backscatter.raman.tools.operation.CalcRamanBscProfile`
        signal_ratio (:class:`ELDAmwl.signals.Signals`): signal ratio
        empty_bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): \
                instance of RamanBackscatters which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    _name = 'CalcRamanBackscatter'

    def __call__(self, **kwargs):
        assert 'bsc_params' in kwargs
        assert 'calibr_window' in kwargs
        assert 'calc_routine' in kwargs
        assert 'signal_ratio' in kwargs
        assert 'empty_bsc' in kwargs

        res = super(CalcRamanBackscatter, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcRamanBackscatterDefault' .
        """
        return 'CalcRamanBackscatterDefault'


registry.register_class(CalcRamanBackscatter,
                        CalcRamanBackscatterDefault.__name__,
                        CalcRamanBackscatterDefault)

registry.register_class(RamanBackscatterFactory,
                        RamanBackscatterFactoryDefault.__name__,
                        RamanBackscatterFactoryDefault)
