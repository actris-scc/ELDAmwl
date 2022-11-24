# -*- coding: utf-8 -*-
"""Classes for lidar constant calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import UseCaseNotImplemented, NegBscForLidarconst
from ELDAmwl.lidar_constant.product import LidarConstants
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import ANGSTROEM_DEFAULT
from ELDAmwl.utils.constants import ASSUMED_LR_DEFAULT
from ELDAmwl.utils.constants import ASSUMED_LR_ERROR_DEFAULT
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import LOWEST_HEIGHT_RANGE
from ELDAmwl.utils.constants import LR
from ELDAmwl.utils.constants import OVL_FACTOR
from ELDAmwl.utils.constants import OVL_FACTOR_ERR
from ELDAmwl.utils.constants import RAMAN
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTIONS
from ELDAmwl.utils.numerical import integral_profile
from numpy import sqrt
from numpy import square as sqr

import numpy as np


class LidarConstantFactory(BaseOperationFactory):
    """
    """

    name = 'LidarConstantFactory'

    def __call__(self, **kwargs):
        assert 'wavelength' in kwargs
        assert 'mwl_product_params' in kwargs
        res = super(LidarConstantFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'LidarConstantFactoryDefault' .
        """
        return LidarConstantFactoryDefault.__name__


class LidarConstantFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`LidarConstants` from all products of the same wavelength.
    Params:
        wl (float): wavelength for which the lidar constant shall be derived
        mwl_product_params (MeasurementParams): parameter of the mwl product
    """

    name = 'LidarConstantFactoryDefault'

    mwl_product_params = None
    wl = None
    used_resolution = None
    bsc_param = None
    bsc = None
    signals = None
    lidar_constants = None
    calibr_height = None
    assumed_angstroem = None
    assumed_lr = None
    assumed_lr_err = None
    lc_params = None

    def init(self):
        self.lidar_constants = Dict()
        self.calibr_height = np.nan
        self.assumed_angstroem = ANGSTROEM_DEFAULT
        self.assumed_lr = np.nan
        self.assumed_lr_err = np.nan
        self.wl = self.kwargs['wavelength']
        self.mwl_product_params = self.kwargs['mwl_product_params']

    def prepare(self):
        """collect input values from measurement or assumed values

        calculation of lidar constant requires the following information
            * which backscatter product is the one with this wavelength?
            * which signals are related to this backscatter product?
            * lidar ratio below lowest bin of backscatter profile
            * angstroem exponent below lowest bin of backscatter profile
            * the height of full overlap is the height for calculation the lidar constant
        """
        self.init()

        # which backscatter product is attributed to the wavelength ? -> self.bsc_param
        self.find_bsc_product()

        # which signals are used for the retrieval of this backscatter ? -> self.signals
        self.find_signals()

        # find the best value for the angstroem assumption -> assumed_angstroem
        self.find_angstroem()

        # find calibration height and resolution -> self.calibr_height
        #                                       -> self.used_resolution
        self.find_calibration_height_and_res()

        # find the best value for lidar ratio assumption -> self.assumed_lr
        #                                                  -> self.assumed_lr_err
        self.find_lidar_ratio()

        # import the backscatter profiles from data storage
        self.bsc = self.data_storage.product_common_smooth(self.bsc_param.prod_id_str,
                                                           self.used_resolution)

        # create empty lidar constants (with all meta data) for each involved signals
        for sig in self.signals.keys():
            self.lidar_constants[sig] = LidarConstants.init(self.bsc, self.signals[sig])
            self.lidar_constants[sig].calibr_height = self.calibr_height

    def find_signals(self):
        """ Which signals were used for the retrieval of the backscatter?

        Lidar constants are derived for those channels.
        The signals are collected in self.signals which is an addict.dict with the following keys:
            * 'total' (always)
            * 'refl' and 'transm' (in case the backscatter was calculated from a
               combination of reflected and transmitted signal)
            * 'raman' (in case of Raman backscatter)
        """
        self.signals = Dict({
            'total': self.data_storage.prepared_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.total_sig_id_str)})

        if self.bsc_param.is_bsc_from_depol_components():
            self.signals['refl'] = self.data_storage.prepared_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.refl_sig_id_str)
            self.signals['transm'] = self.data_storage.prepared_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.transm_sig_id_str)

        if self.bsc_param.bsc_method == RAMAN:
            self.signals['raman'] = self.data_storage.prepared_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.raman_sig_id_str)

    def find_angstroem(self):
        """ find best assumption for angstroem exponent

        If an extinction product is defined for this wavelength,
        the angstroem assumption of this product is used.
        Otherwise, a default value (defined in `.constants`) is used.
        """
        ext_param = self.mwl_product_params.prod_param(EXT, self.wl)
        if ext_param is not None:
            self.assumed_angstroem = ext_param.angstroem

    def find_bsc_product(self):
        """ find the backscatter product at this wavelength
        """
        self.bsc_param = self.mwl_product_params.prod_param(RBSC, self.wl)
        if self.bsc_param is None:
            self.bsc_param = self.mwl_product_params.prod_param(EBSC, self.wl)

        if self.bsc_param is None:
            self.logger.warning('cannot calculate lidar constant without backscatter product')

    def find_calibration_height_and_res(self):
        """ find calibration height

        The height of calibration is the height of full overlap.
        If the backscatter profile starts at larger height, use the lowest height of the backscatter profile instead.
        If the backscatter profile is calculated with several resolutions,
        the resolution with the lowest calibration height is used for further retrievals.
        """

        ovl_height = np.nan
        if not self.bsc_param.includes_product_merging():
            for sig in self.signals.values():
                for channel_id in sig.channel_id.values:
                    ovl_height = np.nanmax([ovl_height, self.db_func.read_full_overlap(int(channel_id))])
        else:
            self.logger.error('lidar constant from merged product not yet implemented')

        for res in RESOLUTIONS:
            if self.bsc_param.calc_with_res(res):
                profile = self.data_storage.product_common_smooth(self.bsc_param.prod_id_str, res)

                # start with overlap height
                calibr_height = ovl_height
                for t in range(profile.ds.dims['time']):
                    # use the maximum of all time_slices
                    calibr_idx = profile.first_valid_bin(t)
                    calibr_height = np.nanmax([calibr_height, profile.height[t, calibr_idx]])

                # use the minimum of all resolutions, initial value of self.calibr_height is nan
                self.calibr_height = np.nanmin([self.calibr_height, calibr_height])

                # if this resolution has minimum calibration height -> use this resolution
                if self.calibr_height == calibr_height:
                    self.used_resolution = res

    def find_lidar_ratio(self):
        """ find best assumption for lidar ratio

        the assumed lidar ratio below the calibration height is derived from the following options (prioritized)

        a) if a lidar ratio profile is available at this wavelength -> use the average of lowest profile part

        b) if an elastic backscatter profile is available -> use the average of assumed lr in lowest profile part

        c) use default value (defined in `.constants`)

        """
        # try option a)
        mean_lr, mean_lr_err = self.calc_mean_lr(LR, 'data', 'err')
        if (not np.isnan(mean_lr)) and (not np.isnan(mean_lr_err)):
            self.assumed_lr = mean_lr
            self.assumed_lr_err = mean_lr_err

        else:
            # try option b)
            mean_lr, mean_lr_err = self.calc_mean_lr(
                EBSC,
                'assumed_particle_lidar_ratio',
                'assumed_particle_lidar_ratio_error')
            if (not np.isnan(mean_lr)) and (not np.isnan(mean_lr_err)):
                self.assumed_lr = mean_lr
                self.assumed_lr_err = mean_lr_err

            else:
                # option c)
                self.assumed_lr = ASSUMED_LR_DEFAULT
                self.assumed_lr_err = ASSUMED_LR_ERROR_DEFAULT

    def calc_mean_lr(self, data_type, var_name, error_var_name):
        """calculates the mean lidar ratio in the height range (defined in `.constants`) above calibr_height

        If the data are provided with several resolutions, the result with the smallest error is returned.
        The returned lr error is the maximum of
        the averaged error variable (which represents the calculation uncertainty) and
        the standard deviation (which represents the atmospheric variability)

        Args:
            data_type: from which type of profile. can be LR or EBSC
            var_name(str): name of the variable in the DataSet ('data' or 'assumed_lidar_ratio')
            error_var_name(str): name of the error_variable in the DataSet ('data' or 'assumed_lidar_ratio')
        Returns:
            average lidar ratio, lidar ratio error. nan values are ignored

        """
        avrg_height_bottom = self.calibr_height
        avrg_height_top = self.calibr_height + LOWEST_HEIGHT_RANGE

        # get product parameters of requested data type and wavelength
        prod_param = self.mwl_product_params.prod_param(data_type, self.wl)

        result_avrg = np.nan
        result_err = np.nan

        if prod_param is not None:
            for res in RESOLUTIONS:
                if prod_param.calc_with_res(res):
                    # get the product profile with resolution res
                    profile = self.data_storage.product_common_smooth(prod_param.prod_id_str, res)

                    # get the data points (data and error) within the requested height range
                    avrg_data = profile.ds[var_name].where(
                        (profile.height >= avrg_height_bottom) & (profile.height <= avrg_height_top), drop=True)
                    avrg_error_data = profile.ds[error_var_name].where(
                        (profile.height >= avrg_height_bottom) & (profile.height <= avrg_height_top), drop=True)

                    # calculate average of data, average of error, stddev of data
                    avrg = np.nanmean(avrg_data)
                    avrg_err = np.nanmean(avrg_error_data)
                    stddev = np.nanstd(avrg_data)

                    # the uncertainty of the mean is the maximum of the stddev (atmospheric variability)
                    # and average error (calculation uncertainty)
                    err = np.nanmax([avrg_err, stddev])

                    # the average with smallest error is final result
                    if np.nanmin([result_err, err]) == err:
                        result_avrg = avrg
                        result_err = err

        return result_avrg, result_err

    def calc_lc_total(self):
        calc_routine = CalcLidarConstant()(
            bsc=self.bsc,
            signal=self.signals.total,
            lc_params=self.lc_params,
            empty_lc=self.lidar_constants.total,
        )

        self.lidar_constants.total = calc_routine.run()

    def calc_lc_raman(self):
        raman_calc_routine = CalcRamanLidarConstant()(
            signal=self.signals.raman,
            lc_params=self.lc_params,
            elast_lc=self.lidar_constants.total,
            empty_lc=self.lidar_constants.raman,
        )

        self.lidar_constants.raman = raman_calc_routine.run()

    def calc_lc_depol(self):
        depol_calc_routine = SplitDepolLidarConstant()(
            refl_signal=self.signals.refl,
            transm_signal=self.signals.transm,
            lc_params=self.lc_params,
            total_lc=self.lidar_constants.total,
            empty_lc_refl=self.lidar_constants.refl,
            empty_lc_transm=self.lidar_constants.transm,
        )

        self.lidar_constants.refl, self.lidar_constants.transm = \
            depol_calc_routine.run().values()

    def write_lc_to_db(self):
        for lc in self.lidar_constants.values():
            lc.write_to_database()

    def run(self):
        self.prepare()

        # create Dict with all params which are needed for the calculation
        self.lc_params = Dict({
            'angstroem': self.assumed_angstroem,
            'lidar_ratio': self.assumed_lr,
            'lidar_ratio_err': self.assumed_lr_err,
            'calibr_height': self.calibr_height,
        })

        self.calc_lc_total()

        if 'raman' in self.signals:
            self.calc_lc_raman()

        if self.bsc_param.is_bsc_from_depol_components():
            self.calc_lc_depol()

        self.write_lc_to_db()

        return self.lidar_constants


class CalcLidarConstant(BaseOperationFactory):
    """
    creates a calculator for the calculation of a lidar constant

    Keyword Args:
        bsc (`.Backscatters`): profiles of particle backscatter coefficient
        signal(`.Signals`): :math:`P_{\lambda_0}(t,z)`: elastically backscattered signal  # noqa W605
                           (total signal or combined from depolarization components).
                           The signal must be prepared by `.PrepareBscSignals` before.
                           It can be taken from the global data storage with `.DataStorage.prepared_signal()`.
        empty_lc (`.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        lc_params (addict.Dict): dictionary with mandatory keys

                * 'lidar_ratio' and 'lidar_ratio_err' (used for estimation of atmospheric transmission below calibr_height)

                * 'calibr_height' (height of full overlap of the signal)

    Returns:
            Returns an instance of `.BaseOperation` which calculates the
            lidar constant. In this case,
            it will always return an instance of `.CalcLidarConstantDefault`.
            The keyword parameters are passed on to the created instance.

    """

    name = 'CalcLidarConstant'

    def __call__(self, **kwargs):
        assert 'bsc' in kwargs
        assert 'signal' in kwargs
        assert 'lc_params' in kwargs
        assert 'empty_lc' in kwargs

        res = super(CalcLidarConstant, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcLidarConstantDefault' .
        """
        return 'CalcLidarConstantDefault'


class CalcLidarConstantDefault(BaseOperation):
    """
    Calculates the lidar constant of an elastic signal from a backscatter profile.

    The result is a copy of empty_lc, but its dataset is filled with the calculated values.
    Input signal and bsc are not modified.

    Keyword Args:
        ~: the same as for `.CalcLidarConst`

    """

    name = 'CalcLidarConstantDefault'

    bsc = None
    result = None
    signal = None
    lc_params = None

    def __init__(self, **kwargs):
        super(CalcLidarConstantDefault, self).__init__(**kwargs)
        self.signal = deepcopy(kwargs['signal'])
        self.bsc = deepcopy(kwargs['bsc'])
        self.lc_params = kwargs['lc_params']
        self.result = kwargs['empty_lc']

    def run(self):
        r"""run the lidar constant calculation.

        * The height at which the lidar constant is calculated is :math:`z_c` = self.lc_params.calibr_height
        * | If not yet done so, the signal data are corrected for molecular transmission
            (see `.Signals.correct_for_mol_transmission()`) .

        .. math::
            \widetilde{P_{\lambda_0}}(t,z)
                &= C_{\lambda_0}(t)\:
                   \beta_{\lambda_0}(t,z) \:
                   T_0^{par}(t,z)\\
        * The volume backscatter profile at calibration height is

        .. math::
            \beta_{\lambda_0}(t,z_c) &= \beta_{\lambda_0}^{par}(t,z_c) +
                      \beta_{\lambda_0}^{mol}(t,z_c)\\
        * 2-way atmospheric transmission due to scattering at particles below :math:`z_c` is

        .. math::
            T_0^{par}(t,z_c) &=
                    T_{\lambda_{up}}^{par}(t,z_c) \:
                    T_{\lambda_{down}}^{par}(t,z_c)\\
                                       &= \exp
                                       \bigl( -2 \: \tau_{\lambda_0}^{par}(t,z_c)
                                       \bigr) \\
            \Delta T_0^{par}(t,z_c) &= 2 \: T_0^{par}(t,z_c) \:
                                                    \Delta \tau_{\lambda_0}^{par}(t,z_c)\\

        * The optical depth and its uncertainty are

        .. math::
            \tau_{\lambda_0}^{par}(t,z_c)
                &= S^{par} \: \int_0^{z_c}\beta_{\lambda_0}^{par}(t,\zeta) d\zeta\\
            \Delta \tau_{\lambda_0}^{par}(t,z_c)
                &= \tau_{\lambda_0}^{par}(t,z_c) \:
                    \sqrt{\Biggl( \frac{\Delta S^{par}}
                                       {S^{par}}
                          \Biggr)^2 +
                          \Biggl( \frac{\Delta \int_0^{z_c}\beta_{\lambda_0}^{par}(t,\zeta) d\zeta}
                                       {\int_0^{z_c}\beta_{\lambda_0}^{par}(t,\zeta) d\zeta}
                          \Biggr)^2 +
                    }\\

        with :math:`S^{par}` and :math:`\Delta S^{par}` = self.lc_params.lidar_ratio and self.lc_params.lidar_ratio_err.

        The integral is calculated with `.ELDAmwl.utils.numerical.integral_profile` which includes an extrapolation
        of the data to the ground and an estimation of the uncertainty.

        * finally, the lidar constant and its uncertainty is derived as

        .. math::
            C_0(t) &= \frac{\widetilde{P_{\lambda_0}}(t,z_c)}
                                    {\beta_{\lambda_0}(t,z_c) \:
                                    T_{\lambda_0}^{par}(t,z_c)}\\
            \Delta C_0(t) &= C_{\lambda_0}(t) \:
                                        \sqrt{\Biggl( \frac
                                            {\Delta \widetilde{P_{\lambda_0}}(t,z_c)}
                                            {\widetilde{P_{\lambda_0}}(t,z_c)}
                                            \Biggr)^2 +
                                            \Biggl( \frac
                                            {\Delta \beta_{\lambda_0}(t,z_c)}
                                            {\beta_{\lambda_0}(t,z_c)}
                                            \Biggr)^2 +
                                            \Biggl( \frac
                                            {\Delta T_{\lambda_0}^{par}(t,z_c)}
                                            {T_{\lambda_0}^{par}(t,z_c)}
                                            \Biggr)^2
                                            }\\


        Returns:
            `.LidarConstants`: :math:`C_0(t)`: time series of lidar constants of the elastic total signal

        """

        # bin numbers of calibration height in backscatter profile
        bsc_calibr_bins = self.bsc.height_to_levels(self.lc_params.calibr_height).values

        # bin numbers of calibration height in signal profile
        sig_calibr_bins = self.signal.height_to_levels(self.lc_params.calibr_height).values

        # backscatter and signal profiles must have the same altitude axis
        # if not -> exception
        if np.any(bsc_calibr_bins != sig_calibr_bins):
            raise (UseCaseNotImplemented('different height axis in signal and backscatter profile',
                                         'lidar constant calculation',
                                         '?'))

        if not self.signal.corrected_for_mol_transmission:
            self.signal.correct_for_mol_transmission()

        # calculation of calibration constant (has to be done for each time slice)
        for t in range(self.bsc.num_times):
            # value of the molecular backscatter at calibration height
            mol_bsc = self.signal.ds.mol_backscatter[t, sig_calibr_bins[t]].values

            # value of the signal at calibration height
            sig = self.signal.data[t, sig_calibr_bins[t]].values
            sig_err = self.signal.err[t, sig_calibr_bins[t]].values

            # backscatter profile data (might have values below calibration height)
            part_bsc = self.bsc.data[t].values
            part_bsc_err = self.bsc.err[t].values

            if self.bsc.is_negative[t, bsc_calibr_bins[t]]:
                self.logger.error('cannot calculate lidar constant from negative backscatter profile')
                raise NegBscForLidarconst(self.bsc.params.prod_id_str)

            # volume bsc
            vol_bsc = (part_bsc + mol_bsc)[bsc_calibr_bins[t]]
            vol_bsc_err = vol_bsc * (part_bsc_err / part_bsc)[bsc_calibr_bins[t]]

            # calculate atmospheric transmission below calibration height
            # 1) integrated backscatter with lower and upper error bound
            int_bsc = integral_profile(part_bsc,
                                       range_axis=self.bsc.range[t].values,
                                       extrapolate_ovl_factor=OVL_FACTOR,
                                       first_bin=None,
                                       last_bin=None)[bsc_calibr_bins[t]]

            int_bsc_min = integral_profile(part_bsc - part_bsc_err,
                                           range_axis=self.bsc.range[t].values,
                                           extrapolate_ovl_factor=(OVL_FACTOR - OVL_FACTOR_ERR),
                                           first_bin=None,
                                           last_bin=None)[bsc_calibr_bins[t]]

            int_bsc_max = integral_profile(part_bsc + part_bsc_err,
                                           range_axis=self.bsc.range[t].values,
                                           extrapolate_ovl_factor=(OVL_FACTOR + OVL_FACTOR_ERR),
                                           first_bin=None,
                                           last_bin=None)[bsc_calibr_bins[t]]

            int_bsc_err = abs(int_bsc_max - int_bsc_min) / 2

            # 2) aod = integrated backscatter * assumed lidar ratio
            lr = self.lc_params.lidar_ratio
            lr_err = self.lc_params.lidar_ratio_err
            aod = int_bsc * lr
            aod_err = aod * sqrt(sqr(lr_err / lr) + sqr(int_bsc_err / int_bsc))

            # 3) transmission at calibration height = exp(-2 aod)
            # transm_err = sqrt(sqr(-2*transm * aod_err)) = 2 * transm * aod_err
            transm = np.exp(-2 * aod)
            transm_err = 2 * transm * aod_err

            # calculate lidar constant lc
            # lc = signal / ((mol bsc + part bsc) * total transmission)
            lc = sig / vol_bsc / transm
            lc_err = lc * sqrt(sqr(sig_err / sig)
                               + sqr(vol_bsc_err / vol_bsc)
                               + sqr(transm_err / transm))

            self.result.ds.data_vars['lidar_constant'][t] = lc
            self.result.ds.data_vars['lidar_constant_err'][t] = lc_err
            self.result.ds.data_vars['particle_transmission'][t] = transm
            self.result.ds.data_vars['particle_transmission_err'][t] = transm_err

        return self.result


class CalcRamanLidarConstant(BaseOperationFactory):
    """
    creates a calculator for a lidar constant of a Raman signal

    Keyword Args:
        signal(`.Signals`): :math:`P_{\lambda_R}(t,z)`: Raman signal  # noqa W605
                           The signal must be prepared by `.PrepareBscSignals` before.
                           It can be taken from the global data storage with `.DataStorage.prepared_signal()`.
        empty_lc (`.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        elast_lc (`.LidarConstants`): \
                the lidar constant of the elastic signal
        lc_params (addict.Dict): dictionary with mandatory keys

                * 'angstroem' (used for estimation of atmospheric transmission below calibr_height)

                * 'calibr_height' (height of full overlap of the signal)

    Returns:
            Returns an instance of `.BaseOperation` which calculates the
            lidar constant of the Raman signal. In this case,
            it will always return an instance of `.CalcRamanLidarConstantDefault`.
            The keyword parameters are passed on to the created instance.

    """

    name = 'CalcRamanLidarConstant'

    def __call__(self, **kwargs):
        assert 'signal' in kwargs
        assert 'elast_lc' in kwargs
        assert 'lc_params' in kwargs
        assert 'empty_lc' in kwargs

        res = super(CalcRamanLidarConstant, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcRamanLidarConstantDefault' .
        """
        return 'CalcRamanLidarConstantDefault'


class CalcRamanLidarConstantDefault(BaseOperation):
    """
    Calculates the lidar constant of a Raman signal from the Raman signal and
    the lidar constant of the elastic signal.

    The result is a copy of empty_lc, but its dataset is filled with the calculated values.
    Input signal, elast_lc, and lc_params are not modified.

    Keyword Args:
        ~: the same as for `.CalcRamanLidarConst`

    """

    name = 'CalcRamanLidarConstantDefault'

    signal = None
    lc_params = None
    elast_lc = None
    result = None

    def __init__(self, **kwargs):
        super(CalcRamanLidarConstantDefault, self).__init__(**kwargs)
        self.signal = deepcopy(kwargs['signal'])
        self.lc_params = kwargs['lc_params']
        self.elast_lc = deepcopy(kwargs['elast_lc'])
        self.result = kwargs['empty_lc']

    def run(self):
        r"""run the lidar constant calculation.

        Here, the reference for this calibration is the Rayleigh backscatter profile, not the Raman backscatter profile.
        If the lidar constant is derived in this way,
        the finally calibrated Raman signal corresponds to the attenuated Rayleigh backscatter
        profile and is more useful for further applications than the attenuated Raman backscatter would be.

        * The height at which the lidar constant is calculated is :math:`z_c` = self.lc_params.calibr_height

        .. math::
            \widetilde{P_{\lambda_R}}(t,z)
                &= C_R(t)\:
                   \beta_{\lambda_R}^{mol}(t,z) \:
                   T_R^{par}(t,z)\\

        * :math:`\beta_{\lambda_R}^{mol}(t,z)` is the Rayleigh backscatter coefficient.

        * | :math:`T_0^{par}(t,z_c)` is the 2-way atmospheric transmission at
            emission wavelength due to scattering at particles below
            :math:`z_c`. It is included in the data of keyword argument elast_lc
        * The Ångström exponent :math:`\ae` is included in the keyword parameter lc_params
        * The 2-way atmospheric transmission of the Raman signal and its uncertainty are

        .. math::
            T_R^{par}(t,z_c)
                &= T_{\lambda_0}^{par}(t,z) \: T_{\lambda_R}^{par}(t,z)\\
                &= \bigl( T_0\bigr) ^{f_{\lambda}} \\
            \Delta T_R^{par}(t,z_c)
                &= f_{\lambda} \: T_R^{par}(t,z_c) \:
                    \frac{\Delta T_0^{par}(t,z_c)}
                         {T_0^{par}(t,z_c)} \\

        * The wavelength factor :math:`f_{\lambda}` is

        .. math::
            f_{\lambda} &=
                \frac{1 + \Bigl( \frac{\lambda_0}{\lambda_R} \Bigr ) ^{\ae}}
                     {2}\\

        * finally, the lidar constant and its uncertainty is derived as

        .. math::
            C_R(t) &= \frac{\widetilde{P_{\lambda_R}}(t,z_c)}
                                    {\beta_{\lambda_R}(t,z_c) \:
                                    T_R^{par}(t,z_c)}\\
            \Delta C_R(t) &= C_R(t) \:
                                        \sqrt{\Biggl( \frac
                                            {\Delta \widetilde{P_{\lambda_R}}(t,z_c)}
                                            {\widetilde{P_{\lambda_R}}(t,z_c)}
                                            \Biggr)^2 +
                                            \Biggl( \frac
                                            {\Delta T_R^{par}(t,z_c)}
                                            {T_R^{par}(t,z_c)}
                                            \Biggr)^2
                                            }\\


        Returns:
            `.LidarConstants`: :math:`C_R(t)`: time series of lidar constants of the Raman signal

        """

        # bin numbers of calibration height in signal profile
        sig_calibr_bins = self.signal.height_to_levels(self.lc_params.calibr_height).values

        raman_wl = float(self.signal.detection_wavelength)
        elast_wl = float(self.signal.emission_wavelength)

        # transmission at Raman wavelength at calibration height is calculated
        # from transmission at elastic wavelength (which is included in corresponding
        # LidarConstants instance
        wl_dep = (1 + np.power(elast_wl / raman_wl, self.lc_params.angstroem)) / 2
        elast_transm = self.elast_lc.ds.particle_transmission
        elast_transm_err = self.elast_lc.ds.particle_transmission_err
        transm = np.power(elast_transm, wl_dep)
        transm_err = transm * elast_transm_err / elast_transm * wl_dep

        self.result.ds.data_vars['particle_transmission'].values = transm
        self.result.ds.data_vars['particle_transmission_err'].values = transm_err

        for t in range(self.signal.ds.dims['time']):
            sig = self.signal.data[t, sig_calibr_bins[t]]
            sig_err = self.signal.err[t, sig_calibr_bins[t]]

            # value of the molecular backscatter at calibration height
            rayl_bsc = self.signal.ds.mol_backscatter[t, sig_calibr_bins[t]]

            lc = (sig / rayl_bsc / transm[t])
            lc_err = lc * sqrt(sqr(sig_err / sig)
                               + sqr(transm_err[t] / transm[t]))
            self.result.ds.data_vars['lidar_constant'][t] = lc
            self.result.ds.data_vars['lidar_constant_err'][t] = lc_err

        return self.result


class SplitDepolLidarConstant(BaseOperationFactory):
    """
    creates a calculator for the lidar constant of the reflected and transmitted signals

    Keyword Args:
        refl_signal(`.Signals`): :math:`P_r(t,z)`: reflected signal
                           The signal must be prepared by `.PrepareBscSignals` before.
                           It can be taken from the global data storage with `.DataStorage.prepared_signal()`.
        transm_signal(`.Signals`): :math:`P_t(t,z)`: transmitted signal
                           The signal must be prepared by `.PrepareBscSignals` before.
                           It can be taken from the global data storage with `.DataStorage.prepared_signal()`.
        empty_lc_refl (`.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        empty_lc_transm (`.LidarConstants`): :math:`C_0(t)`\
                instance of LidarConstants which has all meta data but data are empty arrays
        total_lc (`.LidarConstants`): \
                the lidar constant of the combined (total) elastic signal
        lc_params (addict.Dict): dictionary with mandatory keys

                * 'calibr_height' (height of full overlap of the signals)

    Returns:
            Returns an instance of `.BaseOperation` which calculates the
            lidar constant of the transmitted and reflected signals. In this case,
            it will always return an instance of `.SplitDepolLidarConstantDefault`.
            The keyword parameters are passed on to the created instance.

    """

    name = 'SplitDepolLidarConstant'

    def __call__(self, **kwargs):
        assert 'refl_signal' in kwargs
        assert 'transm_signal' in kwargs
        assert 'total_lc' in kwargs
        assert 'lc_params' in kwargs
        assert 'empty_lc_refl' in kwargs
        assert 'empty_lc_transm' in kwargs

        res = super(SplitDepolLidarConstant, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'SplitDepolLidarConstantDefault' .
        """
        return 'SplitDepolLidarConstantDefault'


class SplitDepolLidarConstantDefault(BaseOperation):
    """
    Calculates the lidar constant of a transmitted and reflected signal from the
    both signals and the lidar constant of the combined elastic (total) signal.

    The result is a copy of empty_lc, but its dataset is filled with the calculated values.
    Input data refl_signal, transm_signal, total_lc, and lc_params are not modified.

    Keyword Args:
        ~: the same as for `.CalcRamanLidarConst`

    """

    name = 'SplitDepolLidarConstantDefault'

    bsc = None
    result = None
    refl_signal = None
    transm_signal = None
    lc_params = None
    total_lc = None

    def __init__(self, **kwargs):
        super(SplitDepolLidarConstantDefault, self).__init__(**kwargs)
        self.refl_signal = deepcopy(kwargs['refl_signal'])
        self.transm_signal = deepcopy(kwargs['transm_signal'])
        self.lc_params = kwargs['lc_params']
        self.total_lc = deepcopy(kwargs['total_lc'])
        self.result = Dict({'refl': kwargs['empty_lc_refl'],
                            'transm': kwargs['empty_lc_transm'],
                            })

    def run(self):
        r"""run the lidar constant calculation

        * The height at which the lidar constant is calculated is :math:`z_c` = self.lc_params.calibr_height
        * | If not yet done so, the data of both signals are corrected for molecular transmission
            (see `.Signals.correct_for_mol_transmission()`).

        .. math::
            \widetilde{P_r}(t,z)
                &= C_r(t) \:
                    \beta_r(t,z) \: T_r^{par}(t,z) \\
            \widetilde{P_t}(t,z)
                &= C_t(t)\:
                   \beta_t(t,z) \: T_t^{par}(t,z)\\

        * The signal ratio is

        .. math::
            R(t,z) &= \frac{\widetilde{P_r}(t,z)}{\widetilde{P_t}(t,z)}\\

        * The factor :math:`f` is

        .. math::
            f &= \frac{\eta^*}{K} \: H_r\\
            \text{with } \eta^* &= \text{gain factor} \\
                            K &= \text{gain factor correction, and}\\
                            H_r, H_t &= H\text{parameters of }\widetilde{P_r} \text{ and } \widetilde{P_t}\\
            \Delta f &= f \: \sqrt{\Biggl(\frac{ \Delta \eta^* }{\eta^*}\Biggr) ^2 +
                                   \Biggl(\frac{ \Delta K }{K}\Biggr) ^2 +
                                   \Biggl(\frac{ \Delta H_r }{H_r}\Biggr) ^2}\\

        * The lidar constants are calculated with

        .. math::
            d_r &= \frac{f}{R(t,z_c)} - H_t \\
            C_r(t) &= \frac{C_0(t)}
                           {d_r}\\
            \Delta C_r(t) &= \sqrt{\Biggl( \frac{\Delta C_0(t) \: d_r}{C_0(t)} \Biggr)^2 +
                                   \Biggl( \Delta H_t \Biggr)^2 +
                                   \Biggl( \frac{\Delta f}{R(t,z_c)} \Biggr)^2 +
                                   \Biggl( \frac{\Delta R(t,z_c) \: f}{R^2(t,z_c)} \Biggr)^2
                                   } \\

            d_t &= f - H_t \: R(t,z_c) \\
            C_t(t) &= \frac{C_0(t)}
                           {d_t}\\
            \Delta C_t(t) &= \sqrt{\Biggl( \frac{\Delta C_0(t) \: d_t}{C_0(t)}\Biggr)^2 +
                                   \Biggl( \Delta f \Biggr)^2 +
                                   \Biggl( \Delta H_t \: R(t,z_c) \Biggr) ^2 +
                                   \Biggl( \Delta R(t,z_c) \: R(t,z_c) \Biggr) ^2
                                   } \\

        * | The lidar constants :math:`C_t` and :math:`C_r` are defined in a way, that the average
            of both calibrated signals is equal to the calibrated total signal, see `.signals.from_depol_components`.

        .. math::
            \frac{1}{2}\Biggl (\frac{\widetilde{P_r}}{C_r}  +
                               \frac{\widetilde{P_t}}{C_t}
                       \Biggr)
                &= \frac{f \: \widetilde{P_t} - H_T \: \widetilde{P_r}}{C_0}
                = \frac{\widetilde{P_0}}{C_0}\\

        Returns:
            addict.Dict with the keys 'refl' and 'transm' which contain
            the time series of corresponding lidar constants (`.LidarConstants`)

        """
        # bin numbers of calibration height in signal profile
        sig_calibr_bins = self.refl_signal.height_to_levels(self.lc_params.calibr_height).values

        if not self.transm_signal.corrected_for_mol_transmission:
            self.transm_signal.correct_for_mol_transmission()
        if not self.refl_signal.corrected_for_mol_transmission:
            self.transm_signal.correct_for_mol_transmission()

        sigratio = Signals.as_sig_ratio(self.refl_signal, self.transm_signal)
        h_refl = float(self.refl_signal.h.value)
        h_refl_err = float(self.refl_signal.h.stat_error)
        if np.isnan(h_refl_err):
            h_refl_err = 0

        h_transm = float(self.transm_signal.h.value)
        h_transm_err = float(self.transm_signal.h.stat_error)
        if np.isnan(h_transm_err):
            h_transm_err = 0

        gain_factor_correction = float(self.refl_signal.pol_calibr.gain_factor_correction.value)
        gain_factor_correction_err = float(self.refl_signal.pol_calibr.gain_factor_correction.stat_error)  # noqa E501
        if np.isnan(gain_factor_correction_err):
            gain_factor_correction_err = 0

        gain_factor = float(self.refl_signal.pol_calibr.gain_factor.value)
        gain_factor_err = float(self.refl_signal.pol_calibr.gain_factor_correction.stat_error)
        if np.isnan(gain_factor_err):
            gain_factor_err = 0

        factor = gain_factor / gain_factor_correction * h_refl
        if h_refl != 0.0:
            factor_err = factor * sqrt(sqr(gain_factor_err / gain_factor)
                                       + sqr(gain_factor_correction_err / gain_factor_correction)
                                       + sqr(h_refl_err / h_refl))
        else:
            factor_err = factor * sqrt(sqr(gain_factor_err / gain_factor)
                                       + sqr(gain_factor_correction_err / gain_factor_correction))

        for t in range(sigratio.ds.dims['time']):
            c_total = float(self.total_lc.ds.lidar_constant[t])
            c_total_err = float(self.total_lc.ds.lidar_constant_err[t])

            ratio = float(sigratio.data[t, sig_calibr_bins[t]])
            ratio_err = float(sigratio.err[t][sig_calibr_bins[t]])

            # dr = denominator of lc_refl equations
            dr = (factor / ratio - h_transm)
            lc_refl = c_total / dr
            lc_refl_err = lc_refl / dr * np.sqrt(sqr(c_total_err / c_total * dr)
                                                 + sqr(h_transm_err)
                                                 + sqr(factor_err / ratio)
                                                 + sqr(ratio_err * factor / sqr(ratio)))

            # dt = denominator of lc_transm equations
            dt = factor - h_transm * ratio
            lc_transm = c_total / dt
            lc_transm_err = lc_transm / dt * sqrt(sqr(c_total_err / c_total * dt)
                                                  + sqr(factor_err)
                                                  + sqr(h_transm_err * ratio)
                                                  + sqr(ratio_err * h_transm))

            self.result.refl.ds.data_vars['lidar_constant'][t] = float(lc_refl)
            self.result.transm.ds.data_vars['lidar_constant'][t] = float(lc_transm)
            self.result.refl.ds.data_vars['lidar_constant_err'][t] = float(lc_refl_err)
            self.result.transm.ds.data_vars['lidar_constant_err'][t] = float(lc_transm_err)

        return self.result


registry.register_class(SplitDepolLidarConstant,
                        SplitDepolLidarConstantDefault.__name__,
                        SplitDepolLidarConstantDefault)

registry.register_class(CalcRamanLidarConstant,
                        CalcRamanLidarConstantDefault.__name__,
                        CalcRamanLidarConstantDefault)

registry.register_class(CalcLidarConstant,
                        CalcLidarConstantDefault.__name__,
                        CalcLidarConstantDefault)

registry.register_class(LidarConstantFactory,
                        LidarConstantFactoryDefault.__name__,
                        LidarConstantFactoryDefault)
