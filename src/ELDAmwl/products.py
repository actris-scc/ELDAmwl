# -*- coding: utf-8 -*-
"""base classes for products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.base import Params
from ELDAmwl.configs.config import RANGE_BOUNDARY_KM
from ELDAmwl.constants import COMBINE_DEPOL_USE_CASES, MC, AUTO, FIXED, HIGHRES, LOWRES
from ELDAmwl.constants import EBSC
from ELDAmwl.constants import EXT
from ELDAmwl.constants import MERGE_PRODUCT_USE_CASES
from ELDAmwl.constants import NC_FILL_BYTE
from ELDAmwl.constants import NC_FILL_INT
from ELDAmwl.constants import RBSC
from ELDAmwl.constants import UNITS
from ELDAmwl.database.db_functions import get_general_params_query, get_mc_params_query, get_smooth_params_query
from ELDAmwl.exceptions import DetectionLimitZero, NotEnoughMCIterations
from ELDAmwl.log import logger
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.signals import Signals

import numpy as np
import xarray as xr


class Products(Signals):

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

        # todo: copy other general parameter

        return result

    def save_to_netcdf(self):
        pass


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
    def smooth_method(self):
        return self.smooth_params.smooth_method

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
                 'hres': gen_params.calc_with_hr,
                 'lres': gen_params.calc_with_lr,
                 'elpp_file': gen_params.elpp_file}
        else:
            df = params_table[(params_table.id == self.prod_id_str)]
            idx = df.index[0]
            hres = df.hres[idx] or gen_params.calc_with_hr
            lres = df.lres[idx] or gen_params.calc_with_lr

            params_table.loc[params_table.id == self.prod_id_str, 'hres'] = hres  # noqa E501
            params_table.loc[params_table.id == self.prod_id_str, 'lres'] = lres  # noqa E501

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

        result.valid_alt_range.min_height = query.ProductOptions.min_height
        result.valid_alt_range.max_height = query.ProductOptions.max_height

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
        self.smooth_method = None

        self.detection_limit = None
        self.error_threshold = Dict({'lowrange': None,
                                     'highrange': None})

        self.transition_zone = Dict({'bottom': None,
                                     'top': None})
        self.vert_res = Dict({'lowres': Dict({'lowrange': None,
                                                'highrange': None}),
                              'highres': Dict({'lowrange': None,
                                                'highrange': None}),
                              })
        self.time_res = Dict({'lowres': Dict({'lowrange': None,
                                                'highrange': None}),
                              'highres': Dict({'lowrange': None,
                                                'highrange': None}),
                              })

    @classmethod
    def from_query(cls, query):
        result = cls()

        result.smooth_method = query.ProductOptions._smooth_type

        if result.smooth_method == AUTO:
            result.error_threshold.lowrange = query.ErrorThresholdsLow.value
            result.error_threshold.highrange = query.ErrorThresholdsHigh.value

            result.detection_limit = query.ProductOptions.detection_limit
            if result.detection_limit == 0.0:
                raise(DetectionLimitZero, result.prod_id)

        if result.smooth_method == FIXED:
            result.transition_zone.bottom = query.ProductOptions.transition_zone_from
            result.transition_zone.top = query.ProductOptions.transition_zone_to

            result.vert_res.lowres.lowrange = query.ProductOptions.lowres_lowrange_vertical_resolution
            result.vert_res.lowres.highrange = query.ProductOptions.lowres_highrange_vertical_resolution
            result.vert_res.highres.lowrange = query.ProductOptions.highres_lowrange_vertical_resolution
            result.vert_res.highres.highrange = query.ProductOptions.highres_highrange_vertical_resolution

            result.time_res.lowres.lowrange = query.ProductOptions.lowres_lowrange_integration_time
            result.time_res.lowres.highrange = query.ProductOptions.lowres_highrange_integration_time
            result.time_res.highres.lowrange = query.ProductOptions.highres_lowrange_integration_time
            result.time_res.highres.highrange = query.ProductOptions.highres_highrange_integration_time

        return result

    @classmethod
    def from_db(cls, prod_id):
        query = get_smooth_params_query(prod_id)
        result = cls.from_query(query)
        return result
