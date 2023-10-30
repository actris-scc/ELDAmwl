# -*- coding: utf-8 -*-
"""base classes for products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.base import Params
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import IParams
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import CouldNotFindProductsResolution
from ELDAmwl.errors.exceptions import DetectionLimitZero
from ELDAmwl.errors.exceptions import DifferentProductsResolution
from ELDAmwl.errors.exceptions import DifferentProductTypeForAE
from ELDAmwl.errors.exceptions import DifferentWlForLR
from ELDAmwl.errors.exceptions import NotEnoughMCIterations
from ELDAmwl.errors.exceptions import NoMwlProductDefined
from ELDAmwl.errors.exceptions import SameWlForAE
from ELDAmwl.errors.exceptions import NotFoundInStorage
from ELDAmwl.errors.exceptions import SizeMismatch
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.signals import Signals
from ELDAmwl.storage.cached_functions import sg_coeffs
from ELDAmwl.storage.cached_functions import smooth_routine_from_db
from ELDAmwl.utils.constants import AE_TYPES
from ELDAmwl.utils.constants import ALL_OK, BELOW_MIN_BSCR
from ELDAmwl.utils.constants import CALC_WINDOW_OUTSIDE_PROFILE
from ELDAmwl.utils.constants import COMBINE_DEPOL_USE_CASES
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import FIXED
from ELDAmwl.utils.constants import HIGHRES
from ELDAmwl.utils.constants import LOWRES
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import MERGE_PRODUCT_USE_CASES
from ELDAmwl.utils.constants import NC_FILL_BYTE
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import NEG_DATA, P_NEG_DATA, P_ALL_OK, P_EMPTY
from ELDAmwl.utils.constants import PRODUCT_TYPE_NAME
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTION_STR, SINGLE_POINT
from ELDAmwl.utils.constants import P_TOO_LARGE_INTEGRAL, P_VALUE_OUTSIDE_VALID_RANGE
from ELDAmwl.utils.constants import UNCERTAINTY_TOO_LARGE, VALUE_OUTSIDE_VALID_RANGE
from ELDAmwl.utils.numerical import integral_profile
from zope import component

import ELDAmwl.utils.constants
import numpy as np
import xarray as xr


class Products(Signals):
    # p_params = None
    smooth_routine = None  # class to perform smoothing
    mwl_meta_id = None
    params = None  # params of this specific product (ProductParams)
    num_scan_angles = None
    resolution = None

    @classmethod
    def from_signal(cls, signal, p_params, **kw_args):
        """creates an instance of Products from general data of signal.

        data, err, qf, and binres have the same shape as signal,
        but are filled with nan.

        """
        result = cls()
        result.ds = deepcopy(signal.ds)
        result.ds['data'][:] = np.nan
        result.ds['err'][:] = np.nan
        result.ds['qf'][:] = ALL_OK
        result.ds['binres'][:] = NC_FILL_INT

        result.station_altitude = signal.station_altitude
        result.raw_heightres = signal.raw_heightres
        result.params = p_params

        # todo: copy other general parameter
        result.emission_wavelength = deepcopy(signal.emission_wavelength)
        result.num_scan_angles = signal.num_scan_angles
        result.ds['time_bounds'] = signal.ds['time_bounds']
        result.ds['mol_backscatter'] = signal.ds.mol_backscatter
        result.profile_qf = deepcopy(signal.profile_qf)

        result.mwl_meta_id = '{}_{}'.format(MWLFileStructure.NC_VAR_NAMES[p_params.general_params.product_type],
                                            round(float(result.emission_wavelength)))

        if result.params.smooth_method is not None:
            result.smooth_routine = SmoothRoutine()(method_id=result.params.smooth_method)

        return result

    @property
    def product_type(self):
        return self.params.product_type

    @property
    def product_id_str(self):
        return self.params.prod_id_str

    @property
    def is_derived_product(self):
        return self.params.general_params.is_derived_product

    def smooth(self, binres):
        """
        performs smoothing of the data
        Args:
            binres (xarray.DataArray) array with the bin resolution which shall be used for smoothing

        Returns:

        """
        self.logger.debug(f'smooth product {self.product_id_str}')
        if self.data.shape != binres.shape:
            raise SizeMismatch('bin resolution',
                               'product {}'.format(self.params.prod_id_str),
                               'smooth')
        num_times = self.ds.dims['time']
        num_levels = self.ds.dims['level']
        # first bin of the smooth window
        fb = binres.level - binres // 2
        # next bin after smooth window
        nb = binres.level + binres // 2 + 1

        # find valid time slices (those which have not only nan values)
        valid_ts = np.where(~self.data.isnull().all(dim='level'))[0]

        for t in valid_ts:
            # first and last smoothable bins
            fsb = np.where(fb[:, t] >= self.first_valid_bin(t))[0][0]
            # actually, this is not the last smoothable bin, but the one after that
            lsb = np.where(nb[:, t] > self.last_valid_bin(t))[0][0]
            # keep this notation in order to avoid lsb + 1 everywhere

            for lev in range(fsb, lsb):
                self.qf[t, lev] = np.bitwise_or.reduce(self.qf.values[t, int(fb[lev, t]):int(nb[lev, t])])
                # todo: smoothing of mol_extinction, mol_backscatter, transmission, cloudflag, sys_err etc
                smoothed = self.smooth_routine.run(window=int(binres[t, lev]),
                                                   data=self.data.values[t, int(fb[lev, t]):int(nb[lev, t])],
                                                   err=self.err.values[t, int(fb[lev, t]):int(nb[lev, t])])
                self.data[t, lev] = smoothed.data
                self.err[t, lev] = smoothed.err
                self.binres[t, lev] = binres[t, lev]

            for lev in range(fsb):
                self.set_invalid_point(t, lev, CALC_WINDOW_OUTSIDE_PROFILE)
            for lev in range(lsb, num_levels):
                self.set_invalid_point(t, lev, CALC_WINDOW_OUTSIDE_PROFILE)

    def screen_negative_data(self):
        good_points_before = self.ds.qf.where(self.ds.qf == ALL_OK).count(dim='level')

        self.flag_values_below_threshold(0, NEG_DATA)

        good_points_after = self.ds.qf.where(self.ds.qf == ALL_OK).count(dim='level')
        num_neg_points = good_points_before - good_points_after

        if self.product_type in self.cfg.MAX_ALLOWED_PERCENTAGE_OF_NEG_DATA:
            max_percentage = self.cfg.MAX_ALLOWED_PERCENTAGE_OF_NEG_DATA[self.product_type]
            bad_time_slices = np.where((num_neg_points / good_points_before) > max_percentage)
            self.profile_qf[bad_time_slices] = self.profile_qf[bad_time_slices] | P_NEG_DATA
        # todo: overwrite this method in angstroem exponents and skip (pass) the test

    def flag_values_below_threshold(self, threshold, qf_flag):
        # todo: how to handle systematic errors ?
        max_profile = self.data + self.cfg.NEG_VALUES_ERR_FACTOR * self.err
        bad_idxs = np.where(max_profile < threshold)
        self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | qf_flag

    def flag_values_above_threshold(self, threshold, qf_flag):
        # todo: how to handle systematic errors ?
        min_profile = self.data - self.cfg.NEG_VALUES_ERR_FACTOR * self.err
        bad_idxs = np.where(min_profile > threshold)
        self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | qf_flag

    def screen_valid_data_range(self):
        min_value = self.cfg.VALID_DATA_RANGE[self.product_type][0]
        max_value = self.cfg.VALID_DATA_RANGE[self.product_type][1]

        if min_value != self.cfg.INVALID:
            self.flag_values_below_threshold(min_value, VALUE_OUTSIDE_VALID_RANGE)
        if max_value != self.cfg.INVALID:
            self.flag_values_above_threshold(max_value, VALUE_OUTSIDE_VALID_RANGE)

        self.qc_profile_data_range()

    def screen_too_large_errors(self):
        bad_idxs = np.where((self.rel_err > self.cfg.MAX_ALLOWED_REL_ERROR[self.product_type]) &
                            (self.err > self.cfg.MAX_ALLOWED_ABS_ERROR[self.product_type]))

        self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | UNCERTAINTY_TOO_LARGE

    def screen_for_aerosol_free_layers(self):
        # can be done only for derived products, because the reference backscatter ratio at 532
        # is obtained as first step of derived products
        # todo: testing

        if 'min_BscRatio' in self.params.__dict__:
            min_bsc_ratio = self.params.min_BscRatio
        elif self.product_type in self.cfg.MIN_BSC_RATIO:
            min_bsc_ratio = self.cfg.MIN_BSC_RATIO[self.product_type]
        else:
            self.logger.warning('cannot perform screening for aerosol free layers '
                                'because no minimum bsc ratio was defined')
            return None

        try:
            bsc_ratio_profile = self.data_storage.bsc_ratio_532(self.resolution)
            bad_idxs = np.where((bsc_ratio_profile.data < min_bsc_ratio) & (bsc_ratio_profile.ds.qf == ALL_OK))
            self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | BELOW_MIN_BSCR
        except NotFoundInStorage:
            self.logger.error('screening for aerosol free layers '
                                  f'for {PRODUCT_TYPE_NAME[self.product_type]} failed '
                                  f'because no bsc ratio is available for {RESOLUTION_STR[self.resolution]} ')

    def screen_for_single_points(self):
        """ flag single data points which are not connected to other neighboring valid data points
        """
        # use dummy_data.rolling(level=3, min_periods=1, center=True).count() < 2
        # if level==3 and count == 2, the point has itself and 1 neighbor
        # if level==3 and count == 1, the point has itself or only 1 neighbor
        # if level ==5 and count >=3, the point has itself and 2 neighbors in the 5 bins window
        # strategy -> increase level iteratively

        # select only data which are ok
        dummy_data = self.data.where(self.ds.qf == ALL_OK)

        # the common vertical resolution in m
        vert_res_m = self.data_storage.common_vertical_resolution(self.resolution).data

        # if some values in vert_res_m are smaller than the minimum layer depth, replace them with min_layer_depth
        min_layer_depth = self.cfg.MIN_LAYER_DEPTH
        vert_res_m[np.where(vert_res_m < min_layer_depth)[0]] = min_layer_depth

        # common vertical resolution in bins
        vert_res_bins = self.heightres_to_bins(vert_res_m)

        # all bin resolutions which occur in this array
        all_bin_res = np.unique(vert_res_bins)

        # this list may contain also NC_FILL_INT -> remove it
        all_bin_res = all_bin_res[np.where(all_bin_res != NC_FILL_INT)]

        self.ds['heightres'] = self.data_storage.common_vertical_resolution(self.resolution)
        self.ds['heightres_bin'] = self.data_storage.common_vertical_resolution(self.resolution)
        self.ds['heightres_bin'].data = vert_res_bins
        self.ds['counts'] = self.data_storage.common_vertical_resolution(self.resolution)
        self.ds['counts'].data[:] = 0

        for br in all_bin_res:

            # data with all binres are taken into account when counting neighbors
            counts = dummy_data.rolling(level=br, min_periods=1, center=True).count()

            # comparison to number of required neighbors is done only for data points with vert_res_bins == br
            bad_idxs = np.where((self.ds.qf == ALL_OK) & (counts < (br/2)) & (vert_res_bins == br))
            self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | SINGLE_POINT

            br_idxs = np.where(vert_res_bins == br)
            self.ds['counts'][br_idxs] = counts[br_idxs]

    def qc_integral(self):
        # todo: use only data points with qf == ALL_OK
        max_integral = self.cfg.MAX_INTEGRAL[self.product_type]
        dummy_data = self.data.where(self.ds.qf == ALL_OK)
        dummy_heights = self.height.where(self.ds.qf == ALL_OK)

        for t in np.where(self.profile_qf == P_ALL_OK)[0]:
            int_profile = integral_profile(dummy_data[t].values,
                                           range_axis=dummy_heights[t].values)
                                           # dummy_data[t].values,
                                           # range_axis=dummy_heights[t].values,
                                           # extrapolate_ovl_factor=OVL_FACTOR,
                                           # first_bin=self.first_valid_bin(t),
                                           # last_bin=self.last_valid_bin(t))

            # the last valid point of the integral profile (if any)
            if int_profile is not None:
                integral = int_profile[np.where(~np.isnan(int_profile))][-1]
                if integral > max_integral:
                    self.profile_qf[t] = self.profile_qf[t] | P_TOO_LARGE_INTEGRAL
            else:
                self.logger.warning('cannot perform qc integral check because no valid data in profile')

    def qc_profile_data_range(self):
        if self.product_type in self.cfg.MAX_ALLOWED_PERCENTAGE_OF_OUT_OF_RANGE_DATA:
            max_percentage = self.cfg.MAX_ALLOWED_PERCENTAGE_OF_OUT_OF_RANGE_DATA[self.product_type]

            good_points = self.ds.qf.where(self.ds.qf == ALL_OK).count(dim='level')
            out_of_range_points = self.ds.qf.where(self.ds.qf == VALUE_OUTSIDE_VALID_RANGE).count(dim='level')
            all_points = out_of_range_points + good_points

            bad_time_slices = np.where((out_of_range_points / all_points) > max_percentage)
            self.profile_qf[bad_time_slices] = self.profile_qf[bad_time_slices] | P_VALUE_OUTSIDE_VALID_RANGE

    def retrieval_failed(self):
        if (self.profile_qf != P_ALL_OK).all():
            return True
        else:
            return False

    def is_out_of_range(self):
        if ((self.profile_qf & P_VALUE_OUTSIDE_VALID_RANGE) == P_VALUE_OUTSIDE_VALID_RANGE).all():
            return True
        else:
            return False

    def flag_empty_profiles(self):
        empty_profiles = self.data.isnull().all('level')
        self.profile_qf[empty_profiles] = self.profile_qf[empty_profiles] | P_EMPTY

    def quality_control(self):
        self.screen_too_large_errors()
        self.screen_negative_data()

        if self.is_derived_product:
            self.screen_for_aerosol_free_layers()

        if self.product_type in self.cfg.VALID_DATA_RANGE:
            self.screen_valid_data_range()

        self.screen_for_single_points()

        self.flag_empty_profiles()

        if self.product_type in self.cfg.MAX_INTEGRAL:
            self.qc_integral()

        invalid_time_slices = np.where(self.profile_qf != P_ALL_OK)
        for t in invalid_time_slices[0]:
            self.set_invalid_profile(t)

        # todo: here is not the correct place to make this test. the product could be valid with other resolution
        # if all time slices are labelled as corrupt profiles -> set the whole product retrieval as failed
        # if self.retrieval_failed():
        #     # measurement_params are all params of the measurement (MeasurementParams)
        #     measurement_params = component.queryUtility(IParams)
        #     self.params.mark_as_failed(measurement_params)

    def save_to_netcdf(self):
        pass

    def write_data_in_ds(self, ds):
        """
        insert product data into dataset

        find the indexes where the product coordinates fit into coordinates of
        the ds and write product data there
        Args:
            ds (xr.Dataset): empty dataset where to insert the product data

        Returns:

        """
        subset = ds.sel(wavelength=self.emission_wavelength)
        if self.num_scan_angles > 1:
            # altitude axes might be different, analyze all time slices separately
            # todo: not yet tested
            for t_idx in range(subset.dims['time']):
                idx = np.searchsorted(subset.altitude.values[t_idx], self.altitude.values[t_idx])
                subset.variables['values'][t_idx, idx] = self.data[t_idx, :]
        else:
            # analyze only first time slice, because altitude axes are all equal
            t_idx = 0
            idx = np.searchsorted(subset.altitude.values[t_idx], self.altitude.values[t_idx])
            subset.variables['data'][:, idx] = self.data[:, :]
            subset.variables['quality_flag'][:, idx] = self.ds.qf[:, :]
            subset.variables['absolute_statistical_uncertainty'][:, idx] = self.err[:, :]
            if self.has_sys_err:
                subset.variables['absolute_systematic_uncertainty_positive'][:, idx] = self.ds.sys_err_pos[:, :]
                subset.variables['absolute_systematic_uncertainty_negative'][:, idx] = self.ds.sys_err_neg[:, :]

    def to_meta_ds_dict(self, meta_data):
        dct = Dict({'attrs': Dict(), 'data_vars': Dict()})

        dct.data_vars.error_retrieval_method = MWLFileStructure() \
            .error_method_var(self.params.general_params.error_method)
        meta_data[self.mwl_meta_id] = dct


class ProductParams(Params):

    def __init__(self):
        super(ProductParams, self).__init__()
        self.sub_params = ['general_params', 'mc_params', 'smooth_params']
        self.general_params = None
        self.mc_params = None
        self.smooth_params = None
        self.quality_params = None

    def from_db(self, general_params):
        self.general_params = general_params
        if self.general_params.is_basic_product:
            self.smooth_params = SmoothParams.from_db(general_params.prod_id)
            self.quality_params = QualityParams.from_db(general_params.prod_id)

    def from_db_with_id(self, prod_id):
        general_params = GeneralProductParams.from_id(prod_id)
        self.from_db(general_params)

    def get_error_params(self, db_options):
        """reads error params

        Args:
            db_options (Dict): product params, read from SCC db with read_elast_bsc_params(),
                    read_extinction_params(), or read_raman_bsc_params

        """

        self.general_params.error_method = db_options['error_method']
        if self.error_method == MC:
            self.mc_params = MCParams.from_db(self.prod_id)

    def harmonize_resolution_settings(self, params):
        """applicable for derived products.
        make sure that basic profiles are calculated with the same resolution(s) as derived product

        Args:
            params: list of basic params (:class:`ELDAmwl.products.ProductParams`)
        """
        if self.general_params.calc_with_lr:
            for param in params:
                param.general_params.calc_with_lr = True
        if self.general_params.calc_with_hr:
            for param in params:
                param.general_params.calc_with_hr = True

    def ensure_same_wavelength(self, params):
        """applicable for derived products.
        make sure that basic profiles are calculated with the same wavelength as derived product

        Args:
            params: list of basic params (:class:`ELDAmwl.products.ProductParams`)
        """
        for param in params:
            if self.general_params.emission_wavelength != param.emission_wavelength:
                raise DifferentWlForLR(self.prod_id_str)

    def get_valid_alt_range(self, params):
        """applicable for derived products.
        determine the valid_alt_range as min/max of the limits of the basic profiles

        Args:
            params: list of basic params (:class:`ELDAmwl.products.ProductParams`)
        """
        min_heights = []
        max_heights = []

        for param in params:
            min_heights.append(param.general_params.valid_alt_range.min_height)
            max_heights.append(param.general_params.valid_alt_range.max_height)

        self.general_params.valid_alt_range.min_height = max(min_heights)
        self.general_params.valid_alt_range.max_height = min(max_heights)

    def ensure_different_wavelength(self, params):
        """applicable for derived products.
        make sure that basic profiles are calculated for different wavelengths

        Args:
        params: list of basic params (:class:`ELDAmwl.products.ProductParams`)
        """

        wl = []

        for param in params:
            wl.append(param.general_params.emission_wavelength)

        if min(wl) == max(wl):
            raise SameWlForAE(self.prod_id_str)
        # ToDo fix problem if only one of the products is there

    def ensure_same_product_type(self, params):
        """applicable for derived products.
        make sure that basic profiles are of the same type (all backscatters or all extinctions)

        Args:
        params: list of basic params (:class:`ELDAmwl.products.ProductParams`)
        """

        prod_type = []

        for param in params:
            prod_type.append(param.general_params.product_type)

        n_b = prod_type.count(RBSC) + prod_type.count(EBSC)
        n_e = prod_type.count(EXT)

        if (n_b > 0) and (n_e > 0) :
            raise DifferentProductTypeForAE(self.prod_id_str)
        else:
            if n_b > 0:
                self.angstroem_exponent_type = AE_TYPES[1]    # AE Backscatter related
            else:
                self.angstroem_exponent_type = AE_TYPES[0]    # AE Extinction related

    @property
    def prod_id_str(self):
        return str(self.general_params.prod_id)

    @property
    def error_method(self):
        return self.general_params.error_method

    @property
    def smooth_type(self):
        return self.smooth_params.smooth_type

    @property
    def smooth_method(self):
        return self.smooth_params.smooth_method

    @property
    def det_limit_asDataArray(self):
        units = MWLFileStructure.UNITS[self.general_params.product_type]
        return xr.DataArray(self.quality_params.detection_limit,
                            name='detection_limit',
                            attrs={'long_name': 'detection limit',
                                   'units': units,
                                   })

    @property
    def error_threshold_low_asDataArray(self):
        return xr.DataArray(self.quality_params.error_threshold.low,
                            name='error_threshold_low',
                            attrs={'long_name': 'threshold for the '
                                                'relative statistical error '
                                                'below {0} km height'.
                                                format(ELDAmwl.utils.constants.RANGE_BOUNDARY_KM),
                                   'units': '1'})

    @property
    def error_threshold_high_asDataArray(self):
        return xr.DataArray(self.quality_params.error_threshold.high,
                            name='error_threshold_low',
                            attrs={'long_name': 'threshold for the '
                                                'relative statistical error '
                                                'above {0} km height'.
                                                format(ELDAmwl.utils.constants.RANGE_BOUNDARY_KM),
                                   'units': '1'})

    @property
    def smooth_params_auto(self):
        return Dict({'error_threshold_low':
                    self.error_threshold_low_asDataArray,
                     'error_threshold_high':
                    self.error_threshold_high_asDataArray,
                     'detection_limit':
                    self.det_limit_asDataArray,
                     })

    def calc_with_res(self, res):
        if self.general_params.calc_with_hr and res == HIGHRES:
            return True
        elif self.general_params.calc_with_lr and res == LOWRES:
            return True
        else:
            return False

    def mark_as_failed(self, measurement_params):
        params_table = measurement_params.product_table
        params_table.loc[params_table.id == self.prod_id_str, 'failed'] = True

    def assign_to_product_list(self, measurement_params):
        gen_params = self.general_params
        params_list = measurement_params.product_list
        params_table = measurement_params.product_table

        if self.prod_id_str not in params_list:
            params_list[self.prod_id_str] = self
            params_table.loc[len(params_table.index)] = \
                {'id': self.prod_id_str,
                 'wl': gen_params.emission_wavelength,
                 'type': gen_params.product_type,
                 'basic': gen_params.is_basic_product,
                 'derived': gen_params.is_derived_product,
                 'failed': False,
                 RESOLUTION_STR[HIGHRES]: gen_params.calc_with_hr,
                 RESOLUTION_STR[LOWRES]: gen_params.calc_with_lr,
                 'elpp_file': gen_params.elpp_file}
        else:
            df = params_table[(params_table.id == self.prod_id_str)]
            idx = df.index[0]
            highres = df[RESOLUTION_STR[HIGHRES]][idx] or gen_params.calc_with_hr
            lowres = df[RESOLUTION_STR[LOWRES]][idx] or gen_params.calc_with_lr

            params_table.loc[params_table.id == self.prod_id_str, RESOLUTION_STR[HIGHRES]] = highres  # noqa E501
            params_table.loc[params_table.id == self.prod_id_str, RESOLUTION_STR[LOWRES]] = lowres  # noqa E501

    def is_bsc_from_depol_components(self):
        if self.general_params.product_type in [RBSC, EBSC]:
            # todo: put info on COMBINE_DEPOL_USE_CASES in db table
            if self.general_params.usecase in COMBINE_DEPOL_USE_CASES[self.general_params.product_type]:  # noqa E501
                return True
            else:
                return False
        else:
            return False

    def includes_product_merging(self):
        if self.general_params.product_type in [EXT, RBSC, EBSC]:
            # todo: put info on MERGE_PRODUCT_USE_CASES in db table
            if self.general_params.usecase in MERGE_PRODUCT_USE_CASES[self.general_params.product_type]:  # noqa E501
                return True
            else:
                return False
        else:
            return False

    def add_signal_role(self, signal):
        pass

    def to_meta_ds_dict(self, dct):
        """ writes parameter content into Dict for further export in mwl file

        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        pass


class GeneralProductParams(Params):
    """
    general parameters for product retrievals
    """

    def __init__(self):
        super(GeneralProductParams, self).__init__()
        # product id
        self.prod_id = None
        self.product_type = None
        self.usecase = None
        self.emission_wavelength = None
        self.rayl_lr = None

        self.is_basic_product = False
        self.is_derived_product = False

        self.calc_with_hr = False
        self.calc_with_lr = False

        self.error_method = None

#        self.detection_limit = None
#        self.error_threshold = Dict({'low': None,
#                                     'high': None})

        self.valid_alt_range = Dict({'min_height': None,
                                     'max_height': None})

        self.elpp_file = ''

        self.signals = []

    @classmethod
    def from_extended_query(cls, query):
        result = cls.from_short_query(query)

        result.valid_alt_range.min_height = float(query.PreProcOptions.min_height)
        result.valid_alt_range.max_height = float(query.PreProcOptions.max_height)
        result.emission_wavelength = float(query.Channels.emission_wavelength)

        try:
            result.elpp_file = query.PreparedSignalFile.filename
        except AttributeError:
            pass

        return result

    @classmethod
    def from_short_query(cls, query):
        result = cls()

        result.prod_id = query.Products.ID
        result.product_type = query.Products.prod_type_id
        result.usecase = query.Products.usecase_id

        result.is_basic_product = query.ProductTypes.is_basic_product == 1
        result.is_derived_product = not result.is_basic_product

        # the MWLproducProduct and PreparedSignalFile tables
        # are not available if query is
        # related to a simple (not mwl) product. There is no way to test
        # whether the table is inside the query collection -> just try
        try:
            result.calc_with_hr = bool(query.MWLproductProduct.create_with_hr)
            result.calc_with_lr = bool(query.MWLproductProduct.create_with_lr)
        except AttributeError:
            pass

        result.rayl_lr = RayleighLidarRatio()(wavelength=result.emission_wavelength).run()

        return result

    @classmethod
    def from_id(cls, prod_id):
        db_func = component.queryUtility(IDBFunc)
        query = db_func.get_extended_general_params_query(prod_id)
        result = cls.from_extended_query(query)
        return result


class MCParams(Params):
    nb_of_iterations = None

    @classmethod
    def from_db(cls, prod_id):
        result = cls()
        db_func = component.queryUtility(IDBFunc)
        query = db_func.get_mc_params_query(prod_id)
        result.nb_of_iterations = query.iteration_count

        if result.nb_of_iterations <= 1:
            raise(NotEnoughMCIterations, prod_id)

        return result


class QualityParams(Params):
    """
    quality parameters for product retrievals
    """

    def __init__(self):
        super(QualityParams, self).__init__()
        self.detection_limit = None
        self.error_threshold = Dict({'lowrange': None,
                                     'highrange': None})

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.error_threshold.lowrange = query.ErrorThresholdsLow.value
        result.error_threshold.highrange = query.ErrorThresholdsHigh.value

        result.detection_limit = query.SmoothOptions.detection_limit
        if result.detection_limit == 0.0:
            raise (DetectionLimitZero, result.prod_id)

        return result

    @classmethod
    def from_db(cls, prod_id):
        db_func = component.queryUtility(IDBFunc)
        query = db_func.get_quality_params_query(prod_id)
        result = cls.from_query(query)
        return result


class SmoothParams(Params):
    """
    smooth parameters for product retrievals
    """

    def __init__(self):
        super(SmoothParams, self).__init__()
        self.smooth_type = None
        self.smooth_method = None

        # self.detection_limit = None
        # self.error_threshold = Dict({'lowrange': None,
        #                              'highrange': None})

        self.transition_zone = Dict({'bottom': None,
                                     'top': None})
        self.vert_res = Dict(
            {
                RESOLUTION_STR[LOWRES]: Dict(
                    {
                        'lowrange': None,
                        'highrange': None,
                    }),
                RESOLUTION_STR[HIGHRES]: Dict(
                    {
                        'lowrange': None,
                        'highrange': None,
                    }),
            })

        self.time_res = Dict(
            {
                RESOLUTION_STR[LOWRES]: Dict(
                    {
                        'lowrange': None,
                        'highrange': None,
                    }),
                RESOLUTION_STR[HIGHRES]: Dict(
                    {
                        'lowrange': None,
                        'highrange': None,
                    }),
            })

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.smooth_type = query.smooth_type_id

        # if result.smooth_type == AUTO:
        #     result.error_threshold.lowrange = query.ErrorThresholdsLow.value
        #     result.error_threshold.highrange = query.ErrorThresholdsHigh.value
        #
        #     result.detection_limit = query.SmoothOptions.detection_limit
        #     if result.detection_limit == 0.0:
        #         raise(DetectionLimitZero, result.prod_id)

        if result.smooth_type == FIXED:
            result.transition_zone.bottom = float(query.transition_zone_from)
            result.transition_zone.top = float(query.transition_zone_to)

            result.vert_res[RESOLUTION_STR[LOWRES]].lowrange \
                = float(query.lowres_lowrange_vertical_resolution)
            result.vert_res[RESOLUTION_STR[LOWRES]].highrange \
                = float(query.lowres_highrange_vertical_resolution)
            result.vert_res[RESOLUTION_STR[HIGHRES]].lowrange \
                = float(query.highres_lowrange_vertical_resolution)
            result.vert_res[RESOLUTION_STR[HIGHRES]].highrange \
                = float(query.highres_highrange_vertical_resolution)

            result.time_res[RESOLUTION_STR[LOWRES]].lowrange \
                = query.lowres_lowrange_integration_time
            result.time_res[RESOLUTION_STR[LOWRES]].highrange \
                = query.lowres_highrange_integration_time
            result.time_res[RESOLUTION_STR[HIGHRES]].lowrange \
                = query.highres_lowrange_integration_time
            result.time_res[RESOLUTION_STR[HIGHRES]].highrange \
                = query.highres_highrange_integration_time

        return result

    @classmethod
    def from_db(cls, prod_id):
        db_func = component.queryUtility(IDBFunc)

        query = db_func.get_smooth_params_query(prod_id)
        result = cls.from_query(query)
        return result


class SmoothSavGolay(BaseOperation):
    """smoothes a profile window with Savitzky-Golay method

    """

    name = 'SmoothSavGolay'

    def run(self, **kwargs):
        """starts the calculation.

        in scipy.signal.savgol_filter
        (https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html),
        the filtering is done as
        convolution (scipy.ndimage.convolve1d ) of the data and SG coefficients:
        result=convolve1d(data,sgc). Here, the filtering can be done as simple sum (which is supposedly faster)

        Keyword Args:
            window(integer): total length (diameter) of the smooth window. must be an odd number
            data(): ndarray (size=window) which contains the data to be smoothed
            err(): ndarray (size=window) which contains the errors of the data to be smoothed

        Returns:
            addict.Dict with keys 'data' and 'err' which contains the smoothed data and its error

        """

        assert 'window' in kwargs
        assert 'data' in kwargs
        assert 'err' in kwargs

        win = kwargs['window']
        err = kwargs['err']
        data = kwargs['data']

        # todo: handling of qflags
        # todo: improve calculation time

        sgc = sg_coeffs(win, 2)
        err_sm = np.sqrt(np.sum(np.power(err * sgc, 2)))
        data_sm = np.sum(data * sgc)

        return Dict({'data': data_sm, 'err': err_sm})


class SmoothSlidingAverage(BaseOperation):
    """calculates Raman backscatter profile like in ansmann et al 1992"""

    name = 'SmoothSlidingAverage'

    def run(self, **kwargs):
        raise UseCaseNotImplemented('SmoothSlidingAverage',
                                    'smoothing',
                                    'sliding average')


class SmoothRoutine(BaseOperationFactory):
    """
    Creates a Class for smoothing

    Keyword Args:
    """

    name = 'SmoothRoutine'
    method_id = None

    def __call__(self, **kwargs):
        assert 'method_id' in kwargs
        self.method_id = kwargs['method_id']
        res = super(SmoothRoutine, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the smoothing
        """
        return smooth_routine_from_db(self.method_id)


registry.register_class(SmoothRoutine,
                        SmoothSavGolay.__name__,
                        SmoothSavGolay)

registry.register_class(SmoothRoutine,
                        SmoothSlidingAverage.__name__,
                        SmoothSlidingAverage)
