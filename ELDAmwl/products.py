# -*- coding: utf-8 -*-
"""base classes for products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.base import Params
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import DetectionLimitZero
from ELDAmwl.errors.exceptions import DifferentWlForLR
from ELDAmwl.errors.exceptions import NotEnoughMCIterations
from ELDAmwl.errors.exceptions import SizeMismatch
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.signals import Signals
from ELDAmwl.storage.cached_functions import sg_coeffs
from ELDAmwl.storage.cached_functions import smooth_routine_from_db
from ELDAmwl.utils.constants import CALC_WINDOW_OUTSIDE_PROFILE
from ELDAmwl.utils.constants import COMBINE_DEPOL_USE_CASES
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import FIXED
from ELDAmwl.utils.constants import HIGHRES
from ELDAmwl.utils.constants import LOWRES
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import MERGE_PRODUCT_USE_CASES
from ELDAmwl.utils.constants import NEG_DATA
from ELDAmwl.utils.constants import NC_FILL_BYTE
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTION_STR
from ELDAmwl.utils.constants import UNCERTAINTY_TOO_LARGE
from zope import component

import ELDAmwl.utils.constants
import numpy as np
import xarray as xr


class Products(Signals):
    p_params = None
    smooth_routine = None  # class to perform smoothing
    mwl_meta_id = None
    params = None
    num_scan_angles = None

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
        result.ds['qf'][:] = NC_FILL_BYTE
        result.ds['binres'][:] = NC_FILL_INT

        result.station_altitude = signal.station_altitude
        result.params = p_params

        # todo: copy other general parameter
        result.emission_wavelength = signal.emission_wavelength
        result.num_scan_angles = signal.num_scan_angles
        result.ds['time_bounds'] = signal.ds['time_bounds']

        result.mwl_meta_id = '{}_{}'.format(MWLFileStructure.NC_VAR_NAMES[p_params.general_params.product_type],
                                            round(float(result.emission_wavelength)))

        if result.params.smooth_method is not None:
            result.smooth_routine = SmoothRoutine()(method_id=result.params.smooth_method)

        return result

    def smooth(self, binres):
        """
        performs smoothing of the data
        Args:
            binres (xarray.DataArray) array with the bin resolution which shall be used for smoothing

        Returns:

        """

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
        max_values = self.data + self.cfg.NEG_VALUES_ERR_FACTOR * self.err
        # todo: how to handle systematic errors ?
        bad_idxs = np.where(max_values < 0)

        self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | NEG_DATA

    def screen_too_large_errors(self):
        bad_idxs = np.where((self.rel_errors > self.cfg.MAX_ALLOWED_REL_ERROR[self.prod_type]) &
                            (self.err > self.cfg.MAX_ALLOWED_ABS_ERROR[self.prod_type]))

        self.ds.qf[bad_idxs] = self.ds.qf[bad_idxs] | UNCERTAINTY_TOO_LARGE

    def quality_control(self):
        self.screen_negative_data()
        self.screen_too_large_errors()

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
