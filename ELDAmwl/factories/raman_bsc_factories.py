# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""
from addict import Dict
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoValidDataPointsForCalibration
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.factories.backscatter_factories import BackscatterFactory
from ELDAmwl.factories.backscatter_factories import BackscatterFactoryDefault
from ELDAmwl.factories.backscatter_factories import BackscatterParams
from ELDAmwl.factories.backscatter_factories import Backscatters
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import NC_FILL_STR
from ELDAmwl.utils.constants import RAMAN
from ELDAmwl.utils.constants import RAYL_LR

import numpy as np
import xarray as xr


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
    def from_sigratio(cls, sigratio, p_params, calibr_window=None):
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

        # if calibr_window is None:
        #    calibr_window = p_params.calibr_window

        result = super(RamanBackscatters, cls).from_signal(sigratio,
                                                           p_params,
                                                           calibr_window)

        result.calibr_window = calibr_window

        cal_first_lev = sigratio.heights_to_levels(
            calibr_window[:, 0])
        cal_last_lev = sigratio.heights_to_levels(
            calibr_window[:, 1])

        error_params = Dict({'err_threshold':
                            p_params.quality_params.error_threshold,
                             })

        calibr_value = DataPoint.from_data(
            p_params.calibration_params.cal_value, 0, 0)
        cal_params = Dict({'cal_first_lev': cal_first_lev.values,
                           'cal_last_lev': cal_last_lev.values,
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
    derives a single instance of :class:`RamanBackscatters`.
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

            bsc = RamanBackscatters.from_sigratio(
                sig_ratio, self.param, self.calibr_window)

            del sig_ratio

        else:
            bsc = None
            # todo
            # if self.kwargs['autosmooth']:
            # get auto smooht resolution
            #     smooth_res = RamBscAutosmooth()(
            #         signal=raman_sig.ds,
            #         smooth_params=self.param.smooth_params,
            #     ).run()
            #    self.data_storage.set_binres_auto_smooth(self.param.prod_id_str, smooth_res)

        result = bsc

        return result


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


class CalcRamanBscProfileAsAnsmann(BaseOperation):
    """calculates Raman backscatter profile like in ansmann et al 1992"""

    name = 'CalcRamanBscProfileAsAnsmann'

    def run(self, **kwargs):
        raise UseCaseNotImplemented('CalcRamanBscProfileAsAnsmann',
                                    'Raman Backscatter',
                                    'viaBR (id = 1)')


class SavGolayEffBinRes(BaseOperation):
    """calculates effective bin resolution for a given number of bins
    used for smoothing a profile with Savitzky-Golay method

    The calculation is done according to Mattis et al. 2016 with the equation
    eff_binres = round(used_bins_ELDA * 1.24 - 0.24)
    In this paper, used_bins_ELDA corresponds to the radius of the smooth window.
    Here, used_bins is the diameter of the smooth window:
    used_bins = used_bins_ELDA *2 +1
    =>  eff_binres = round(used_bins_ELDA * 1.24 - 0.24) = round(used_bins * 0.62 - 0.86)
"""

    name = 'SavGolayEffBinRes'

    def run(self, **kwargs):
        """
        starts the calculation

        Keyword Args:
            used_bins(integer): number of bins used for the calculation of Sav-Gol filter
                                (= diameter of the smoothing window)

        Returns:
            eff_binres(integer): resulting effective resolution in terms of vertical bins

        """
        assert 'used_bins' in kwargs

        used_bins = kwargs['used_bins']
        eff_binres = np.array(used_bins * 0.62 - 0.86)
        result = eff_binres.round().astype(int)

        return result


class SavGolayUsedBinRes(BaseOperation):
    """calculates the number of bins which have to be
    used for smoothing a profile with Savitzky-Golay method in order to achieve
    a given effective bin resolution

    The calculation is done according to Mattis et al. 2016 with the equation
    used_bins_ELDA = round((eff_binres + 0.24) / 1.24).
    In this paper, used_bins_ELDA corresponds to the radius of the smooth window.
    Here, used_bins is the diameter of the smooth window:
    used_bins = used_bins_ELDA *2 +1 = round((eb+0.86)/0.62)
    """

    name = 'SavGolayUsedBinRes'

    def run(self, **kwargs):
        """
        starts the calculation

        Keyword Args:
            eff_binres(integer): required effective vertical resolution in terms of bins

        Returns:
            used_bins(integer): number of bins (= diameter of the smooth window) to be used for
                                the calculation of the Sav-Gol filter in order to achieve the required effective
                                vertical bin resolution. must be an odd number.

        """
        assert 'eff_binres' in kwargs

        eff_binres = np.array(kwargs['eff_binres'])
        used_binres = (eff_binres + 0.86) / 0.62
        odd_binres = ((used_binres - 1) / 2).round() * 2 + 1

        # result = sg_used_binres(eff_binres.tolist())
        result = odd_binres.astype(int)

        return result


class RamBscEffBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of the effective bin resolution for a given number of bins
    used in the retrieval of ...

    Keyword Args:
            prod_id (str): id of the product
    """

    name = 'RamBscEffBinRes'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(RamBscEffBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_raman_bsc_effbin_algorithm(self.prod_id)


class RamBscUsedBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of how many bins have to be used ...

    Keyword Args:
    """

    name = 'RamBscUsedBinRes'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(RamBscUsedBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_raman_bsc_usedbin_algorithm(self.prod_id)


registry.register_class(RamBscUsedBinRes,
                        SavGolayUsedBinRes.__name__,
                        SavGolayUsedBinRes)

registry.register_class(RamBscEffBinRes,
                        SavGolayEffBinRes.__name__,
                        SavGolayEffBinRes)

registry.register_class(CalcRamanBscProfile,
                        CalcRamanBscProfileViaBR.__name__,
                        CalcRamanBscProfileViaBR)

registry.register_class(CalcRamanBscProfile,
                        CalcRamanBscProfileAsAnsmann.__name__,
                        CalcRamanBscProfileAsAnsmann)

registry.register_class(RamanBackscatterFactory,
                        RamanBackscatterFactoryDefault.__name__,
                        RamanBackscatterFactoryDefault)
