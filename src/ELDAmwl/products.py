# -*- coding: utf-8 -*-
"""base classes for products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.base import Params
from ELDAmwl.configs.config import RANGE_BOUNDARY_KM
from ELDAmwl.constants import COMBINE_DEPOL_USE_CASES, MC, AUTO, FIXED, HIGHRES, LOWRES, RESOLUTION_STR
from ELDAmwl.constants import EBSC
from ELDAmwl.constants import EXT
from ELDAmwl.constants import MERGE_PRODUCT_USE_CASES
from ELDAmwl.constants import NC_FILL_BYTE
from ELDAmwl.constants import NC_FILL_INT
from ELDAmwl.constants import RBSC
from ELDAmwl.mwl_file_structure import UNITS
from ELDAmwl.database.db_functions import get_general_params_query, get_mc_params_query, get_smooth_params_query
from ELDAmwl.exceptions import DetectionLimitZero, NotEnoughMCIterations
from ELDAmwl.log import logger
from ELDAmwl.mwl_file_structure import NC_VAR_NAMES, error_method_var
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.signals import Signals

import numpy as np
import xarray as xr


class Products(Signals):
    p_params = None

    @classmethod
    def from_signal(cls, signal, p_params):
        """creates an instance of Products with from general data of signal.

        data, err, qf, and binres have the same shape as signal,
        but are filled with nan.

        """
        result = cls()
        result.ds = deepcopy(signal.ds)
        result.ds['data'][:] = np.nan
        result.ds['err'][:] = np.nan
        result.ds['qf'][:] = NC_FILL_BYTE
        result.ds['binres'][:] = NC_FILL_INT

        result.params = p_params

        # todo: copy other general parameter
        result.emission_wavelength = signal.emission_wavelength
        result.num_scan_angles = signal.num_scan_angles

        result.mwl_meta_id = '{}_{}'.format(NC_VAR_NAMES[p_params.general_params.product_type],
                                            round(float(result.emission_wavelength)))

        return result

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
            subset.variables['data'][:, idx ] = self.data[:, :]

    def to_meta_ds_dict(self, meta_data):
        dict = Dict({'attrs': Dict(), 'data_vars': Dict()})

        dict.data_vars.error_retrieval_method = error_method_var(self.params.general_params.error_method)
        meta_data[self.mwl_meta_id] = dict


class ProductParams(Params):

    def __init__(self):
        super(ProductParams, self).__init__()
        self.sub_params = ['general_params', 'mc_params', 'smooth_params']
        self.general_params = None
        self.mc_params = None
        self.smooth_params = None

    def from_db(self, general_params):
        self.general_params = general_params
        self.smooth_params = SmoothParams.from_db(general_params.prod_id)

    def get_error_params(self, db_options):
        """reads error params
        Args:
            db_options {}: product params, read from
                    SCC db with read_elast_bsc_params(),
                    read_extinction_params(), or
                    read_raman_bsc_params
            """
        self.general_params.error_method = db_options['error_method']
        if self.error_method == MC:
            self.mc_params = MCParams.from_db(self.prod_id)

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
    def det_limit_asDataArray(self):
        units = UNITS[self.general_params.product_type]
        return xr.DataArray(self.smooth_params.detection_limit,
                            name='detection_limit',
                            attrs={'long_name': 'detection limit',
                                   'units': units,
                                   })

    @property
    def error_threshold_low_asDataArray(self):
        return xr.DataArray(self.smooth_params.error_threshold.low,
                            name='error_threshold_low',
                            attrs={'long_name': 'threshold for the '
                                                'relative statistical error '
                                                'below {0} km height'.
                                                format(RANGE_BOUNDARY_KM),
                                   'units': '1'})

    @property
    def error_threshold_high_asDataArray(self):
        return xr.DataArray(self.smooth_params.error_threshold.high,
                            name='error_threshold_low',
                            attrs={'long_name': 'threshold for the '
                                                'relative statistical error '
                                                'above {0} km height'.
                                                format(RANGE_BOUNDARY_KM),
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

    def to_meta_ds_dict(self, dict):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dict (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        pass


class GeneralProductParams(Params):
    """
    general parameters for product retrievals
    """

    def __init__(self):
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
    def from_query(cls, query):
        result = cls()

        result.prod_id = query.Products.ID
        result.product_type = query.Products._prod_type_ID
        result.usecase = query.Products._usecase_ID
        result.emission_wavelength = float(query.Channels.emission_wavelength)

        result.is_basic_product = query.ProductTypes.is_basic_product == 1
        result.is_derived_product = not result.is_basic_product

#        result.error_threshold.low = query.ErrorThresholdsLow.value
#        result.error_threshold.high = query.ErrorThresholdsHigh.value
#        result.detection_limit = query.ProductOptions.detection_limit
#        if result.detection_limit == 0.0:
#            raise(DetectionLimitZero, result.prod_id)

        result.valid_alt_range.min_height = query.PreProcOptions.min_height
        result.valid_alt_range.max_height = query.PreProcOptions.max_height

        # the MWLproducProduct and PreparedSignalFile tables
        # are not available if query is
        # related to a simple (not mwl) product. There is no way to test
        # whether the table is inside the query collection -> just try
        try:
            result.calc_with_hr = bool(query.MWLproductProduct.create_with_hr)
            result.calc_with_lr = bool(query.MWLproductProduct.create_with_lr)
            result.elpp_file = query.PreparedSignalFile.filename
        except AttributeError:
            pass

        result.rayl_lr = RayleighLidarRatio()(
                wavelength=result.emission_wavelength).run()

        return result

    @classmethod
    def from_id(cls, prod_id):
        query = get_general_params_query(prod_id)
        result = cls.from_query(query)
        return result


class MCParams(Params):
    nb_of_iterations = None

    @classmethod
    def from_db(cls, prod_id):
        result = cls()
        query = get_mc_params_query(prod_id)
        result.nb_of_iterations = query.iteration_count

        if result.nb_of_iterations <= 1:
            raise(NotEnoughMCIterations, prod_id)

        return result


class SmoothParams(Params):
    """
    smooth parameters for product retrievals
    """

    def __init__(self):
        self.smooth_type = None

        self.detection_limit = None
        self.error_threshold = Dict({'lowrange': None,
                                     'highrange': None})

        self.transition_zone = Dict({'bottom': None,
                                     'top': None})
        self.vert_res = Dict({RESOLUTION_STR[LOWRES]: Dict({'lowrange': None,
                                                'highrange': None}),
                              RESOLUTION_STR[HIGHRES]: Dict({'lowrange': None,
                                                'highrange': None}),
                              })
        self.time_res = Dict({RESOLUTION_STR[LOWRES]: Dict({'lowrange': None,
                                                'highrange': None}),
                              RESOLUTION_STR[HIGHRES]: Dict({'lowrange': None,
                                                'highrange': None}),
                              })

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.smooth_type = query.SmoothOptions._smooth_type

        if result.smooth_type == AUTO:
            result.error_threshold.lowrange = query.ErrorThresholdsLow.value
            result.error_threshold.highrange = query.ErrorThresholdsHigh.value

            result.detection_limit = query.SmoothOptions.detection_limit
            if result.detection_limit == 0.0:
                raise(DetectionLimitZero, result.prod_id)

        if result.smooth_type == FIXED:
            result.transition_zone.bottom = float(query.SmoothOptions.transition_zone_from)
            result.transition_zone.top = float(query.SmoothOptions.transition_zone_to)

            result.vert_res[RESOLUTION_STR[LOWRES]].lowrange \
                = float(query.SmoothOptions.lowres_lowrange_vertical_resolution)
            result.vert_res[RESOLUTION_STR[LOWRES]].highrange \
                = float(query.SmoothOptions.lowres_highrange_vertical_resolution)
            result.vert_res[RESOLUTION_STR[HIGHRES]].lowrange \
                = float(query.SmoothOptions.highres_lowrange_vertical_resolution)
            result.vert_res[RESOLUTION_STR[HIGHRES]].highrange \
                = float(query.SmoothOptions.highres_highrange_vertical_resolution)

            result.time_res[RESOLUTION_STR[LOWRES]].lowrange \
                = query.SmoothOptions.lowres_lowrange_integration_time
            result.time_res[RESOLUTION_STR[LOWRES]].highrange \
                = query.SmoothOptions.lowres_highrange_integration_time
            result.time_res[RESOLUTION_STR[HIGHRES]].lowrange \
                = query.SmoothOptions.highres_lowrange_integration_time
            result.time_res[RESOLUTION_STR[HIGHRES]].highrange \
                = query.SmoothOptions.highres_highrange_integration_time

        return result

    @classmethod
    def from_db(cls, prod_id):
        query = get_smooth_params_query(prod_id)
        result = cls.from_query(query)
        return result
