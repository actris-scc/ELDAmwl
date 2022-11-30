# -*- coding: utf-8 -*-
"""constants describing the structure of mwl output file"""

from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.database.tables.backscatter import BscCalibrMethod
from ELDAmwl.database.tables.backscatter import BscMethod
from ELDAmwl.database.tables.backscatter import ElastBscMethod
from ELDAmwl.database.tables.backscatter import RamanBscMethod
from ELDAmwl.database.tables.extinction import ExtMethod
from ELDAmwl.utils.constants import AE
from ELDAmwl.utils.constants import ASS
from ELDAmwl.utils.constants import CR
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import HIGHRES
from ELDAmwl.utils.constants import LOWRES
from ELDAmwl.utils.constants import LR
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_BYTE
from ELDAmwl.utils.constants import PLDR
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTION_STR
from ELDAmwl.utils.constants import VLDR
from zope import component

import numpy as np
import xarray as xr


class MWLFileStructure:

    GENERAL = 0
    META_DATA = 1
    LOWRES_PRODUCTS = 2
    HIGHRES_PRODUCTS = 3

    MAIN_GROUPS = [GENERAL, META_DATA, LOWRES_PRODUCTS, HIGHRES_PRODUCTS]

    RES_GROUP = {
        LOWRES: LOWRES_PRODUCTS,
        HIGHRES: HIGHRES_PRODUCTS,
    }

    GROUP_NAME = {
        GENERAL: '/',
        META_DATA: 'meta_data',
        LOWRES_PRODUCTS: '{}_products'.format(RESOLUTION_STR[LOWRES]),
        HIGHRES_PRODUCTS: '{}_products'.format(RESOLUTION_STR[HIGHRES]),
    }

    WRITE_MODE = {
        GENERAL: 'w',
        META_DATA: 'a',
        LOWRES_PRODUCTS: 'a',
        HIGHRES_PRODUCTS: 'a',
    }

    HEADER_VARS = {
        GENERAL: [
            'latitude',
            'longitude',
            'station_altitude',
        ],
        META_DATA: [
            'cloud_mask_type',
            'scc_product_type',
            'molecular_calculation_source',
        ],
    }

    HEADER_ATTRS = {
        GENERAL: [
            'measurement_ID',
            'system', 'hoi_system_ID', 'hoi_configuration_ID',
            'institution', 'location', 'station_ID',
            'pi', 'data_originator',
            'data_processing_institution', 'comment', 'title',
            'source', 'references', 'processor_name',
            'measurement_start_datetime', 'measurement_stop_datetime',
        ],
        META_DATA: [
            'hoi_system_ID',
            'hoi_configuration_ID',
            # 'elpp_history',
            'molecular_calculation_source_file',
        ],
    }

    TITLE = 'Profiles of aerosol optical properties'
    REFERENCES = 'Project website at https://www.earlinet.org'
    PROCESSOR_NAME = 'ELDAmwl'

    NC_VAR_NAMES = {
        RBSC: 'backscatter',
        EBSC: 'backscatter',
        EXT: 'extinction',
        LR: 'lidarratio',
        AE: 'angstroemexponent',
        CR: 'colorratio',
        VLDR: 'volumedepolarization',
        PLDR: 'particledepolarization',
    }

    UNITS = {
        RBSC: '1/(m*sr)',
        EBSC: '1/(m*sr)',
        EXT: '1/m',
        LR: 'sr',
        AE: '1',
        CR: '1',
        VLDR: '1',
        PLDR: '1',
    }

    LONG_NAMES = {
        RBSC: 'particle backscatter coefficient',
        EBSC: 'particle backscatter coefficient',
        EXT: 'particle extinction coefficient',
        LR: 'particle lidar ratio',
        # AE: 'particle angstroem exponent',
        # CR: 'color ratio',
        VLDR: 'volume linear depolarization ratio',
        PLDR: 'particle linear depolarization ratio',
    }

    COO_ATTR = 'longitude latitude'
    ANC_VAR_ATT = 'error_{} vertical_resolution'  # noqa P103

    PRODUCTS_WITH_SYS_ERROR = [VLDR]

    def is_product_with_sys_error(self, p_type):
        if p_type in self.PRODUCTS_WITH_SYS_ERROR:
            return True
        else:
            return False

    def data_attrs(self, p_type):
        return {
            'long_name': self.LONG_NAMES[p_type],
            'units': self.UNITS[p_type],
            'ancillary_variables': self.ANC_VAR_ATT.format(self.NC_VAR_NAMES[p_type]),
            # 'coordinates': COO_ATTR,
        }

    def stat_err_attrs(self, p_type):
        return {
            'long_name': 'absolute statistical uncertainty of {}'.format(self.NC_VAR_NAMES[p_type]),
            'units': self.UNITS[p_type],
            'coordinates': self.COO_ATTR,
        }

    def sys_err_neg_attrs(self, p_type):
        return {
            'long_name': 'negative absolute systematic uncertainty of {}'.format(self.NC_VAR_NAMES[p_type]),
            'units': self.UNITS[p_type],
            'coordinates': self.COO_ATTR,
        }

    def sys_err_pos_attrs(self, p_type):
        return {
            'long_name': 'positive absolute systematic uncertainty of {}'.format(self.NC_VAR_NAMES[p_type]),
            'units': self.UNITS[p_type],
            'coordinates': self.COO_ATTR,
        }

    def error_method_var(self, value):
        var = xr.DataArray(
            np.int8(value),
            name='error_retrieval_method',
            attrs={
                'long_name': 'method used for the retrieval of uncertainties',
                'flag_values': [np.int8(MC), np.int8(ASS)],
                'flag_meanings': 'monte_carlo error_propagation',
                '_FillValue': NC_FILL_BYTE,
            })
        return var

    def cal_search_range_var(self, value):
        """

        Args:
            value: addict.Dict() with 2 items

        Returns:

        """
        data = list(value.values())
        var = xr.DataArray(
            data,
            dims=('nv',),
            name='calibration_search_range',
            attrs={
                'long_name': 'height range wherein calibration range is searched',
                '_FillValue': np.nan,
                'units': 'm',
            })
        return var

    def bsc_calibr_value_var(self, value):
        """

        Args:
            value (dbl):

        Returns:

        """
        var = xr.DataArray(
            np.float(value),  # todo ina: pep8 problem with np.float
            name='calibration_value',
            attrs={
                'long_name': 'assumed backscatter-ratio value (unitless) in calibration range',
                '_FillValue': np.nan,
                'units': '1',
            })
        return var


class MWLFileVarsFromDB:

    @property
    def db_func(self):
        return component.queryUtility(IDBFunc)

    def method_var_from_db(self, value, db_table, name, long_name):
        """ read available algorithms or methods from db into a DataArray.

        """
        methods = self.db_func.read_algorithm_options(db_table)
        values = []
        meanings = []
        for v, m in methods.items():
            values.append(np.int8(v))
            meanings.append(m.replace(' ', '_'))
        meanings_str = ' '.join(meanings)

        var = xr.DataArray(
            np.int8(value),
            name=name,
            attrs={
                'long_name': long_name,
                'flag_values': values,
                'flag_meanings': meanings_str,
                '_FillValue': NC_FILL_BYTE,
            })
        return var

    def ext_algorithm_var(self, value):
        result = self.method_var_from_db(
            value,
            ExtMethod,
            'evaluation_algorithm',
            'algorithm used for the extinction retrieval')

        return result

    def ram_bsc_algorithm_var(self, value):
        result = self.method_var_from_db(
            value,
            RamanBscMethod,
            'evaluation_algorithm',
            'algorithm used for the retrieval of the Raman backscatter profile')

        return result

    def elast_bsc_algorithm_var(self, value):
        result = self.method_var_from_db(
            value,
            ElastBscMethod,
            'evaluation_algorithm',
            'algorithm used for the retrieval of the elastic backscatter profile')

        return result

    def bsc_method_var(self, value):
        result = self.method_var_from_db(
            value,
            BscMethod,
            'backscatter_retrieval_method',
            'method used for the backscatter retrieval')

        return result

    def bsc_calibr_method_var(self, value):
        # todo different values for min of signal ratio and min of elast signal
        result = self.method_var_from_db(
            value,
            BscCalibrMethod,
            'backscatter_calibration_range_search_algorithm',
            'algorithm used for the search of the calibration_range')

        return result
