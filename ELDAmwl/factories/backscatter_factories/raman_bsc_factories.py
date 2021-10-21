# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.bases.factory import BaseOperation, BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.interface import IRamBscOp
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoValidDataPointsForCalibration
from ELDAmwl.factories.backscatter_factories.backscatter_factories import BackscatterFactoryDefault, BackscatterFactory
from ELDAmwl.factories.backscatter_factories.backscatter_factories import BackscatterParams
from ELDAmwl.factories.backscatter_factories.backscatter_factories import Backscatters
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import MC, NC_FILL_STR
from ELDAmwl.utils.constants import RAMAN
from ELDAmwl.utils.constants import RAYL_LR

import numpy as np
import xarray as xr
import zope


class RamanBscParams(BackscatterParams):

    def __init__(self):
        super(RamanBscParams, self).__init__()
        self.raman_sig_id = None

        self.raman_bsc_algorithm = None
        self.bsc_method = RAMAN

    def from_db(self, general_params):
        super(RamanBscParams, self).from_db(general_params)

        rbp = self.db_func.read_raman_bsc_params(general_params.prod_id)
        self.raman_bsc_algorithm = rbp['ram_bsc_method']
        self.get_error_params(rbp)
        self.smooth_params.smooth_method = rbp['smooth_method']

    def add_signal_role(self, signal):
        super(RamanBscParams, self).add_signal_role(signal)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(RamanBscParams, self).to_meta_ds_dict(dct)
        dct.data_vars.evaluation_algorithm = MWLFileVarsFromDB().ram_bsc_algorithm_var(self.raman_bsc_algorithm)


class RamanBackscatters(Backscatters):

    @classmethod
    def init(cls, sigratio, p_params, calibr_window=None):
        """calculates RamanBackscatters from a signal ratio.

        The signals were previously prepared by PrepareBscSignals .

        Args:
            sigratio (:class:`Signals`): time series
                                        of signal ratio profiles
            p_params (:class:`RamanBackscatterParams`):
                                    calculation params
                                    of the backscatter product
            calibr_window (xarray.DataArray): variable
                                    'backscatter_calibration_range'
                                    (time, nv: 2)
        """

        result = super(RamanBackscatters, cls).init(sigratio,
                                                    p_params,
                                                    calibr_window)
        # todo ina: check documentation calibr_window is tupe or dataarray?

        result.calibr_window = calibr_window

        # cal_first_lev = sigratio.heights_to_levels(
        #     calibr_window[:, 0])
        # cal_last_lev = sigratio.heights_to_levels(
        #     calibr_window[:, 1])
        #
        # error_params = Dict({'err_threshold':
        #                     p_params.quality_params.error_threshold,
        #                      })
        #
        # calibr_value = DataPoint.from_data(
        #     p_params.calibration_params.cal_value, 0, 0)
        # cal_params = Dict({'cal_first_lev': cal_first_lev.values,
        #                    'cal_last_lev': cal_last_lev.values,
        #                    'calibr_value': calibr_value})
        #
        # calc_routine = CalcRamanBscProfile()(prod_id=p_params.prod_id_str)
        #
        # result.ds = calc_routine.run(sigratio=sigratio.ds,
        #                              error_params=error_params,
        #                              calibration=cal_params)
        return result


class RamanBackscatterFactoryDefault(BackscatterFactoryDefault):
    """
    derives a single instance of :class:`RamanBackscatters`.
    """

    name = 'RamanBackscatterFactoryDefault'

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

        bsc_retrieval_routine = GetRamanBackscatter()(
            bsc_params=self.param,
            calc_routine=CalcRamanBscProfile()(prod_id=self.prod_id),
            calibr_window=self.calibr_window,
            signal_ratio=self.sig_ratio,
            empty_bsc=self.empty_bsc
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
class GetRamanBackscatterDefault(BaseOperation):
    """
    Calculates particle backscatter coefficient from Raman signal.
    """

    name = 'GetRamanBackscatterDefault'

    bsc_params = None
    sigratio = None
    calibr_window = None
    calc_routine = None
    result = None

    def __init__(self, **kwargs):
        super(GetRamanBackscatterDefault, self).__init__(**kwargs)
        self.sigratio = self.kwargs['signal_ratio']
        self.calibr_window = self.kwargs['calibr_window']
        self.calc_routine = self.kwargs['calc_routine']
        self.bsc_params = self.kwargs['bsc_params']
        self.result = deepcopy(self.kwargs['empty_bsc'])

    def run(self, data=None):
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


class CalcRamanBscProfileViaBR(BaseOperation):
    """calculates Raman backscatter profile via BR"""

    name = 'CalcRamanBscProfileViaBR'
    sigratio = None
    error_params = None
    calibration = None

    def run(self, **kwargs):
        """calculates Raman bsc profile from elast and Raman signals
        and calibration window

            Keyword Args:
                sigratio (xarray.DataSet):
                    already smoothed signal ratio with \
                    variables 'data', 'error', 'qf',
                    'binres', 'mol_extinction'
                error_params (addict.Dict):
                    with keys 'lowrange' and 'highrange' =
                        maximum allowable relative statistical error
                calibration (addict.Dict):
                    with keys 'cal_first_lev',
                    'cal_last_lev', and 'calibr_value'
        """
        assert 'sigratio' in kwargs
        assert 'error_params' in kwargs
        assert 'calibration' in kwargs

        sigratio = kwargs['sigratio']
        calibration = kwargs['calibration']
        error_params = kwargs['error_params']
        rayl_bsc = sigratio.mol_extinction / RAYL_LR
        # todo: make BaseOperation for RAYL_LR

        # 1) calculate calibration factor

        times = sigratio.dims['time']
        calibr_factor = np.ones(times) * np.nan
        calibr_factor_err = np.ones(times) * np.nan
        sqr_rel_calibr_err = np.ones(times) * np.nan

        for t in range(times):
            df = sigratio.data.isel({'level':
                                    range(calibration['cal_first_lev'][t],
                                          calibration['cal_last_lev'][t]),
                                     'time': t})\
                .to_dataframe()
            mean = df.data.mean()
            sem = df.data.sem()
            rel_sem = sem / mean

            if rel_sem > error_params.err_threshold.highrange:
                raise NoValidDataPointsForCalibration

            else:
                calibr_factor[t] = calibration.calibr_value.value / mean
                calibr_factor_err[t] = calibr_factor[t] * \
                    np.sqrt(np.square(rel_sem) + np.square(calibration.calibr_value.rel_error))
                sqr_rel_calibr_err[t] = np.square(calibr_factor_err[t] / calibr_factor[t])

        cf = xr.DataArray(calibr_factor,
                          dims=['time'],
                          coords=[sigratio.time])
        sqr_cf_err = xr.DataArray(sqr_rel_calibr_err,
                                  dims=['time'],
                                  coords=[sigratio.time])

        # 2) calculate backscatter ratio
        # todo ina: test whether this copy makes sense and is necessary
        # bsc = deepcopy(sigratio)
        bsc = xr.Dataset()
        bsc['data'] = sigratio.data * cf
        bsc['err'] = bsc.data * np.sqrt(np.square(sigratio.err / sigratio.data) + sqr_cf_err)

        # 3) calculate backscatter coefficient
        bsc['data'] = (bsc.data - 1.) * rayl_bsc
        bsc['err'] = abs(bsc.err * rayl_bsc)

        bsc['qf'] = sigratio.qf
        bsc['binres'] = sigratio.binres

        return bsc


# class CalcRamanBscProfileAsAnsmann(BaseOperation):
#     """calculates Raman backscatter profile like in ansmann et al 1992"""
#
#     name = 'CalcRamanBscProfileAsAnsmann'
#
#     def run(self, **kwargs):
#         raise UseCaseNotImplemented('CalcRamanBscProfileAsAnsmann',
#                                     'Raman Backscatter',
#                                     'viaBR (id = 1)')
#

class CalcRamanBscProfile(BaseOperationFactory):
    """calculates Raman bsc profile from elast
    and Raman signals and calibration window

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
        return self.db_func.read_raman_bsc_algorithm(self.prod_id)

    pass


registry.register_class(CalcRamanBscProfile,
                        CalcRamanBscProfileViaBR.__name__,
                        CalcRamanBscProfileViaBR)


class RamanBackscatterFactory(BackscatterFactory):
    """

    """

    name = 'RamanBackscatterFactory'

    def get_classname_from_db(self):
        return RamanBackscatterFactoryDefault.__name__


registry.register_class(RamanBackscatterFactory,
                        RamanBackscatterFactoryDefault.__name__,
                        RamanBackscatterFactoryDefault)


class GetRamanBackscatter(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
    backscatter coefficient from a  Raman and elastic signal. In this case, it
    will be always an instance of GetRamanBackscatterDefault().
    """

    name = 'GetRamanBackscatter'

    def __call__(self, **kwargs):
        assert 'bsc_params' in kwargs
        assert 'calibr_window' in kwargs
        assert 'calc_routine' in kwargs
        assert 'signal_ratio' in kwargs
        assert 'empty_bsc' in kwargs

        res = super(GetRamanBackscatter, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'GetRamanBackscatterDefault' .
        """
        return 'GetRamanBackscatterDefault'


registry.register_class(GetRamanBackscatter,
                        GetRamanBackscatterDefault.__name__,
                        GetRamanBackscatterDefault)
