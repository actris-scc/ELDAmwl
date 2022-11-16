# -*- coding: utf-8 -*-
"""Classes for lidar constant calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.lidar_constant.product import LidarConstants
from ELDAmwl.signals import Signals
import zope
import numpy as np
import xarray as xr
from numpy import square as sqr
from numpy import sqrt


from ELDAmwl.utils.constants import RESOLUTIONS, EXT, RBSC, EBSC, ANGSTROEM_DEFAULT, ASSUMED_LR_DEFAULT, \
    ASSUMED_LR_ERROR_DEFAULT, FIXED, LR, LOWEST_HEIGHT_RANGE, RAMAN, OVL_FACTOR_ERR, OVL_FACTOR
from ELDAmwl.utils.numerical import integral_profile


class LidarConstantFactory(BaseOperationFactory):
    """
    """

    name = 'LidarConstantFactory'

    def __call__(self, **kwargs):
        assert 'wl' in kwargs
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
    lidar_constants = Dict()
    calibr_height = np.nan
    assumed_angstroem = ANGSTROEM_DEFAULT
    assumed_lr = np.nan
    assumed_lr_err = np.nan

    def prepare(self):
        """collect input values from measurement or assumed values

        calculation of lidar constant requires the following informations
            * which backscatter product is the one with this wavelength?
            * which signals are related to this backscatter product?
            * lidar ratio below lowest bin of backscatter profile
            * angstroem exponent below lowest bin of backscatter profile
            * the height of full overlap is the height for calculation the lidar constant
        """
        self.wl = self.kwargs['wl']
        self.mwl_product_params = self.kwargs['mwl_product_params']

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
        for key, value in self.signals.items():
            self.lidar_constants[key] = LidarConstants.init(self.bsc, value)
            self.lidar_constants[key].calibr_height = self.calibr_height

    def find_signals(self):
        """
        Which signals were used for the retrieval of the backscatter?
        Lidar constants are derived for those channels.
        The signals are collected in self.signals which is an addict.dict with the following keys:
            * 'total' (always)
            * 'refl' and 'transm' (in case the backscatter was calculated from a
               combination of reflected and transmitted signal)
            * 'raman' (in case of Raman backscatter)
        """
        self.signals = Dict({
            'total': self.data_storage.elpp_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.total_sig_id_str)})

        if self.bsc_param.is_bsc_from_depol_components():
            self.signals['refl'] = self.data_storage.elpp_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.refl_sig_id_str)
            self.signals['transm'] = self.data_storage.elpp_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.transm_sig_id_str)

        if self.bsc_param.bsc_method == RAMAN:
            self.signals['raman'] = self.data_storage.elpp_signal(
                self.bsc_param.prod_id_str,
                self.bsc_param.raman_sig_id_str)

    def find_angstroem(self):
        """
        If an extinction product is defined for this wavelength,
        the angstroem assumption of this product is used.
        Otherwise, a default value (defined in ELDAmwl.utils.constants) is used.
        """
        ext_param = self.mwl_product_params.prod_param(EXT, self.wl)
        if ext_param is not None:
            self.assumed_angstroem = ext_param.angstroem

    def find_bsc_product(self):
        """
        find the backscatter product at this wavelength
        """
        self.bsc_param = self.mwl_product_params.prod_param(RBSC, self.wl)
        if self.bsc_param is None:
            self.bsc_param = self.mwl_product_params.prod_param(EBSC, self.wl)

        if self.bsc_param is None:
            self.logger.warning('cannot calculate lidar constant without backscatter product')

    def find_calibration_height_and_res(self):
        """
        The height of calibration is the height of full overlap.
        If the backscatter profile starts at larger height, use the lowest height of the backscatter profile instead.
        If the backscatter profile is calculated with several resolutions,
        the resolution with the lowest calibration height is used for further retrievals.
        """

        ovl_height = np.nan
        if not self.bsc_param.includes_product_merging():
            for sig in self.signals.values():
                ovl_height = np.nanmax([np.nan, self.db_func.read_full_overlap(int(sig.channel_id))])
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
        """
        the assumed lidar ratio below the calibration height is derived from the following options (prioritized)

        a) if a lidar ratio profile is available at this wavelength -> use the average of lowest profile part

        b) if an elastic backscatter profile is available -> use the average of assumed lr in lowest profile part

        c) use default value (defined in ELDAmwl.utils.constants)

        """
        # try option a)
        mean_lr, mean_lr_err = self.calc_mean_lr(LR, 'data', 'err')
        if (not np.isnan(mean_lr)) and (not np.isnan(mean_lr_err)):
            self.assumed_lr = mean_lr
            self.assumed_lr_err = mean_lr_err

        else:
            # try option b)
            mean_lr, mean_lr_err = self.calc_mean_lr(EBSC, 'assumed_particle_lidar_ratio', 'assumed_particle_lidar_ratio_error')
            if (not np.isnan(mean_lr)) and (not np.isnan(mean_lr_err)):
                self.assumed_lr = mean_lr
                self.assumed_lr_err = mean_lr_err

            else:
                # option c)
                self.assumed_lr = ASSUMED_LR_DEFAULT
                self.assumed_lr_err = ASSUMED_LR_ERROR_DEFAULT

    def calc_mean_lr(self, data_type, var_name, error_var_name):
        """calculates the mean lidar ratio in the height range (defined in ELDAmwl.utils.constants) above calibr_height

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
                    avrg_data = profile.ds[var_name].where((profile.height >= avrg_height_bottom) &
                                                   (profile.height <= avrg_height_top), drop=True)
                    avrg_error_data = profile.ds[error_var_name].where((profile.height >= avrg_height_bottom) &
                                                   (profile.height <= avrg_height_top), drop=True)

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

    def run(self):
        self.prepare()

        # create Dict with all params which are needed for the calculation
        lc_params = Dict({
            'angstroem': self.assumed_angstroem,
            'lidar_ratio': self.assumed_lr,
            'lidar_ratio_err': self.assumed_lr_err,
            'calibr_height': self.calibr_height,
        })

        calc_routine = CalcLidarConstant()(
            bsc=self.bsc,
            signal=self.signals.total,
            lc_params=lc_params,
            empty_lc=self.lidar_constants.total
        )

        self.lidar_constants.total = calc_routine.run()

        if 'raman' in self.signals:
            calc_routine = CalcRamanLidarConstant()(
                signal=self.signals.raman,
                lc_params=lc_params,
                elast_lc=self.lidar_constants.total,
                empty_lc=self.lidar_constants.raman
            )

            self.lidar_constants.raman = calc_routine.run()

        self.lidar_constants.total.write_to_database()
        self.lidar_constants.raman.write_to_database()

        return self.lidar_constants


class CalcLidarConstant(BaseOperationFactory):
    """
    creates a Class for the calculation of a lidar constant

    Returns an instance of BaseOperation which calculates the lidar constant.
    In this case, it will be always an instance of CalcLidarConstantDefault().

    Keyword Args:
        bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter profiles
        signal(:class:`ELDAmwl.signals.Signals`): total signal
        empty_lc (:class:`ELDAmwl.lidar_constant.product.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        lc_params (Dict): dictionary with mandatory keys ('angstroem', 'lidar_ratio', 'lidar_ratio_err', 'calibr_height')

    Returns:
        time series if lidar constants (:class:`ELDAmwl.lidar_constant.product.LidarConstants`)

    """

    name = 'CalcLidarConstant'

    def __call__(self, **kwargs):
        assert 'bsc' in kwargs
        assert 'signal' in kwargs
        assert 'lc_params' in kwargs

        res = super(CalcLidarConstant, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcLidarConstantDefault' .
        """
        return 'CalcLidarConstantDefault'


class CalcLidarConstantDefault(BaseOperation):
    """
    Calculates lidar constant from backscatter profile.

    The result is a copy of empty_lc, but its dataset is filled with the calculated values

    Keyword Args:
        bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter profiles
        signal(:class:`ELDAmwl.signals.Signals`): total signal
        empty_lc (:class:`ELDAmwl.lidar_constant.product.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        lc_params (Dict): dictionary with mandatory keys ('angstroem', 'lidar_ratio', 'lidar_ratio_err', 'calibr_height')

    Returns:
        time series if lidar constants (:class:`ELDAmwl.lidar_constant.product.LidarConstants`)
    """

    name = 'CalcLidarConstantDefault'

    bsc = None
    result = None
    signal = None
    lc_params = None
    result = None

    def __init__(self, **kwargs):
        super(CalcLidarConstantDefault, self).__init__(**kwargs)
        self.signal = deepcopy(kwargs['signal'])
        self.bsc = kwargs['bsc']
        self.lc_params = kwargs['lc_params']
        self.result = kwargs['empty_lc']

    def run(self):
        """
        run the lidar constant calculation

        Returns:
            time series if lidar constants (:class:`ELDAmwl.lidar_constant.product.LidarConstants`)

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

        self.signal.normalize_by_shots()
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

            # volume bsc
            vol_bsc = (part_bsc + mol_bsc)[bsc_calibr_bins[t]]
            vol_bsc_err = vol_bsc * (part_bsc_err/part_bsc)[bsc_calibr_bins[t]]

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
            aod_err = aod * sqrt(sqr(lr_err/lr) + sqr(int_bsc_err/int_bsc))

            # 3) transmission at calibration height = exp(-2 aod)
            # transm_err = sqrt(sqr(-2*transm * aod_err)) = 2 * transm * aod_err
            transm = np.exp(-2 * aod)
            transm_err = 2 * transm * aod_err

            # calculate lidar constant lc
            # lc = signal / ((mol bsc + part bsc) * total transmission)
            lc = sig / vol_bsc / transm
            lc_err = lc * sqrt(sqr(sig_err / sig) +
                               sqr(vol_bsc_err / vol_bsc) +
                               sqr(transm_err / transm))

            self.result.ds.data_vars['lidar_constant'][t] = lc
            self.result.ds.data_vars['lidar_constant_err'][t] = lc_err
            self.result.ds.data_vars['particle_transmission'][t] = transm
            self.result.ds.data_vars['particle_transmission_err'][t] = transm_err

        return self.result


class CalcRamanLidarConstant(BaseOperationFactory):
    """
    creates a Class for the calculation of a lidar constant of a Raman signal

    Returns an instance of BaseOperation which calculates the lidar constant.
    In this case, it will be always an instance of CalcLidarConstantDefault().

    Keyword Args:
        signal(:class:`ELDAmwl.signals.Signals`): total signal
        empty_lc (:class:`ELDAmwl.lidar_constant.product.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        elast_lc(:class:`ELDAmwl.lidar_constant.product.LidarConstants`): \
                lidar constant of the elastic signal
        lc_params (Dict): dictionary with mandatory keys ('angstroem', 'lidar_ratio', 'lidar_ratio_err', 'calibr_height')

    Returns:
        time series if lidar constants (:class:`ELDAmwl.lidar_constant.product.LidarConstants`)

    """

    name = 'CalcRamanLidarConstant'

    def __call__(self, **kwargs):
        assert 'signal' in kwargs
        assert 'elast_lc' in kwargs
        assert 'lc_params' in kwargs

        res = super(CalcRamanLidarConstant, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcRamanLidarConstantDefault' .
        """
        return 'CalcRamanLidarConstantDefault'


class CalcRamanLidarConstantDefault(BaseOperation):
    """Calculates lidar constant of a Raman signal.

    the lidar constant is retrieved from the Raman signal
    and the lidar constant of the elastic signal.
    The result is a copy of empty_lc, but its dataset is filled with the calculated values

    Keyword Args:
        signal(:class:`ELDAmwl.signals.Signals`): Raman signal
        empty_lc(:class:`ELDAmwl.lidar_constant.product.LidarConstants`): \
                instance of LidarConstants which has all meta data but data are empty arrays
        elast_lc(:class:`ELDAmwl.lidar_constant.product.LidarConstants`): \
                lidar constant of the elastic signal
        lc_params (Dict): dictionary with mandatory keys ('angstroem', 'lidar_ratio', 'lidar_ratio_err', 'calibr_height')

    Returns:
        time series if lidar constants (:class:`ELDAmwl.lidar_constant.product.LidarConstants`)
    """

    name = 'CalcRamanLidarConstantDefault'

    bsc = None
    result = None
    signal = None
    lc_params = None
    elast_lc = None
    result = None

    def __init__(self, **kwargs):
        super(CalcRamanLidarConstantDefault, self).__init__(**kwargs)
        self.signal = deepcopy(kwargs['signal'])
        self.lc_params = kwargs['lc_params']
        self.elast_lc = kwargs['elast_lc']
        self.result = kwargs['empty_lc']

    def run(self):
        """
        run the lidar constant calculation

        Returns:
            time series if lidar constants (:class:`ELDAmwl.lidar_constant.product.LidarConstants`)

        """

        # bin numbers of calibration height in signal profile
        sig_calibr_bins = self.signal.height_to_levels(self.lc_params.calibr_height).values

        self.signal.correct_for_mol_transmission()

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

        self.result.ds.data_vars['particle_transmission'] = transm
        self.result.ds.data_vars['particle_transmission_err'] = transm_err

        sig = self.signal.data
        sig_err = self.signal.err

        # value of the molecular backscatter at calibration height
        rayl_bsc = self.signal.ds.mol_backscatter

        lc = (sig / rayl_bsc / transm)[:, sig_calibr_bins]
        lc_err = lc * sqrt(sqr(sig_err / sig) +
                           sqr(transm_err / transm))

        for t in range(self.signal.ds.dims['time']):
            self.result.ds.data_vars['lidar_constant'][t] = lc[t, sig_calibr_bins[t]]
            self.result.ds.data_vars['lidar_constant_err'][t] = lc_err[t, sig_calibr_bins[t]]

        return self.result


class SplitDepolLidarConstant(BaseOperationFactory):
    pass


registry.register_class(CalcRamanLidarConstant,
                        CalcRamanLidarConstantDefault.__name__,
                        CalcRamanLidarConstantDefault)

registry.register_class(CalcLidarConstant,
                        CalcLidarConstantDefault.__name__,
                        CalcLidarConstantDefault)

registry.register_class(LidarConstantFactory,
                        LidarConstantFactoryDefault.__name__,
                        LidarConstantFactoryDefault)
