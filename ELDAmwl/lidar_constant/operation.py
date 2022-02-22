# -*- coding: utf-8 -*-
"""Classes for lidar constant calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
import zope
import numpy as np

from ELDAmwl.utils.constants import RESOLUTIONS, EXT, RBSC, EBSC, ANGSTROEM_DEFAULT, ASSUMED_LR_DEFAULT, \
    ASSUMED_LR_ERROR_DEFAULT, FIXED, LR, LOWEST_HEIGHT_RANGE, RAMAN
from ELDAmwl.utils.numerical import integral_profile


class LidarConstantFactory(BaseOperationFactory):
    """
    """

    name = 'LidarConstantFactory'

    def __call__(self, **kwargs):
        assert 'wl' in kwargs
        assert 'product_params' in kwargs
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
    """

    name = 'LidarConstantFactoryDefault'

    measurement_product_params = None
    wl = None
    used_resolution = None
    bsc_param = None
    bsc = None
    signals = None
    calibr_height = np.nan
    assumed_angstroem = ANGSTROEM_DEFAULT
    assumed_lr = np.nan
    assumed_lr_err = np.nan

    def prepare(self):
        """
        calculation of lidar constant requires the following assumptions
            * lidar ratio below lowest bin of backscatter profile
            * angstroem exponent below lowest bin of backscatter profile
        """
        self.wl = self.kwargs['wl']
        self.measurement_product_params = self.kwargs['product_params']

        self.find_bsc_product()
        self.find_signals()
        self.find_angstroem()
        self.find_calibration_height_and_res()
        self.bsc = self.data_storage.product_common_smooth(self.bsc_param.prod_id_str,
                                                           self.used_resolution),
        self.find_lidar_ratio()

    def find_signals(self):
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
        ext_param = self.measurement_product_params.prod_param(EXT, self.wl)
        if ext_param is not None:
            self.assumed_angstroem = ext_param.angstroem

    def find_bsc_product(self):
        """
        find the backscatter product at this wavelength
        """
        self.bsc_param = self.measurement_product_params.prod_param(RBSC, self.wl)
        if self.bsc_param is None:
            self.bsc_param = self.measurement_product_params.prod_param(EBSC, self.wl)

        if self.bsc_param is None:
            self.logger.warning('cannot calculate lidar constant without backscatter product')

    def find_calibration_height_and_res(self):
        """
        the height of calibration is the lowest point of the backscatter profile at this wavelength
        """

        # find the lowest height of the backscatter profile. test all resolutions

        # self.db_func.read_full_overlap(int(self.bsc_param.total_sig_id[0]))
        # todo: in case of Raman backscatter -> use full overlap height
        for res in RESOLUTIONS:
            if self.bsc_param.calc_with_res(res):
                profile = self.data_storage.product_common_smooth(self.bsc_param.prod_id_str, res)
                calibr_height = np.nan
                for t in range(profile.ds.dims['time']):
                    # use the maximum of all time_slices
                    calibr_idx = profile.first_valid_bin(t)
                    calibr_height = np.nanmax([calibr_height, profile.height[t, calibr_idx]])

                # use the minimum of all resolutions
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
            mean_lr, mean_lr_err = self.calc_mean_lr(EBSC, 'assumed_lidar_ratio', 'assumed_lidar_ratio_error')
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
        prod_param = self.measurement_product_params.prod_param(data_type, self.wl)

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
            signals=self.signals,
            lc_params=lc_params)

        lc = calc_routine.run()



class CalcLidarConstant(BaseOperationFactory):
    """
    creates a Class for the calculation of a lidar constant

    Returns an instance of BaseOperation which calculates the lidar constant.
    In this case, it will be always an instance of CalcLidarConstantDefault().

    Keyword Args:
        bsc (:class:`ELDAmwl.backscatter.raman.product.Backscatters`): particle backscatter profiles
        empty_lr (:class:`ELDAmwl.lidar_ratio.product.LidarRatios`): \
                instance of LidarRatios which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    name = 'CalcLidarConstant'

    def __call__(self, **kwargs):
        assert 'bsc' in kwargs
        assert 'signals' in kwargs
        assert 'lc_params' in kwargs

        res = super(CalcLidarConstant, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcLidarRatioDefault' .
        """
        return 'CalcLidarConstantDefault'


class CalcLidarConstantDefault(BaseOperation):
    """
    Calculates lidar constant from backscatter profile.

    The result is a copy of empty_lc, but its dataset is filled with the calculated values

    Keyword Args:
        bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter profiles
        empty_lc (:class:`ELDAmwl.l`): \
                instance of LidarConstants which has all meta data but data are empty arrays

    Returns:
        time series if lidar constants (:class:`ELDAmwl.`)

    """

    name = 'CalcLidarConstantDefault'

    bsc = None
    result = None
    signals = None
    lc_params = None

    def __init__(self, **kwargs):
        super(CalcLidarConstantDefault, self).__init__(**kwargs)
        self.signals = kwargs['signals']
        self.bsc = kwargs['bsc']
        self.lc_params = kwargs['lc_params']

    def run(self):
        """
        run the lidar constant calculation

        The the optional keyword args  'bsc' allow to feed new input data into
        an existing instance of CalcLidarRatioDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Keyword Args:
            bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): Raman backscatter profiles, default=None

        Returns:
            time series if lidar constants (:class:`ELDAmwl.`)

        """

        # self.result.ds['data'] = ext.data / bsc.data
        # self.result.ds['err'] = self.result.data * np.sqrt(
        #     np.power(ext.err / ext.err, 2) + np.power(bsc.err / bsc.err, 2))
        # self.result.ds['qf'] = ext.qf | bsc.qf

        self.signals['total'].ds.mol_backscatter
        self.signals['total'].data
        self.bsc[0].data

        self.bsc[0].height_to_levels(self.kwargs['lc_params'].calibr_height)
        self.signals['total'].ds.mol_backscatter[:, self.signals['total'].height_to_levels(733)]

        transm = integral_profile(self.bsc[0].data,
                     range_axis=None,
                     extrapolate_ovl_factor=None,
                     first_bin=None,
                     last_bin=None)



        return self.result


registry.register_class(CalcLidarConstant,
                        CalcLidarConstantDefault.__name__,
                        CalcLidarConstantDefault)

registry.register_class(LidarConstantFactory,
                        LidarConstantFactoryDefault.__name__,
                        LidarConstantFactoryDefault)
