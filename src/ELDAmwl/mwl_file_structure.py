# -*- coding: utf-8 -*-
"""constants describing the structure of mwl output file"""

from addict import Dict
import xarray as xr
import numpy as np

from ELDAmwl.constants import LOWRES, HIGHRES, RESOLUTION_STR, NC_FILL_BYTE, MC, ASS
from ELDAmwl.constants import RBSC, EBSC, EXT, LR, AE

GENERAL = 0
META_DATA = 1
LOWRES_PRODUCTS = 2
HIGHRES_PRODUCTS = 3

MAIN_GROUPS = [GENERAL, META_DATA, LOWRES_PRODUCTS, HIGHRES_PRODUCTS]

RES_GROUP = {LOWRES: LOWRES_PRODUCTS,
             HIGHRES: HIGHRES_PRODUCTS,
             }

GROUP_NAME = {GENERAL: '/',
              META_DATA: 'meta_data',
              LOWRES_PRODUCTS: '{}_products'.format(RESOLUTION_STR[LOWRES]),
              HIGHRES_PRODUCTS: '{}_products'.format(RESOLUTION_STR[HIGHRES])}

WRITE_MODE = {GENERAL: 'w',
              META_DATA: 'a',
              LOWRES_PRODUCTS: 'a',
              HIGHRES_PRODUCTS: 'a'}

HEADER_VARS = {GENERAL: ['latitude', 'longitude', 'station_altitude'],
               META_DATA: ['cloud_mask_type', 'scc_product_type'],
               }

HEADER_ATTRS = {GENERAL: ['measurement_ID',
                          'system', 'hoi_system_ID', 'hoi_configuration_ID',
                          'institution', 'location', 'station_ID',
                          'pi', 'data_originator',
                          'data_processing_institution', 'comment', 'title',
                          'source', 'references', 'processor_name',
                          'measurement_start_datetime', 'measurement_stop_datetime'],
                META_DATA: ['hoi_system_ID', 'hoi_configuration_ID', 'elpp_history'],
                }

TITLE = 'Profiles of aerosol optical properties'
REFERENCES = 'Project website at http://www.earlinet.org'
PROCESSOR_NAME = 'ELDAmwl'

NC_VAR_NAMES = {RBSC: 'backscatter',
                EBSC: 'backscatter',
                EXT: 'extinction',
                LR: 'lidarratio',
                AE: 'angstroemexponent',
#                CR: 'colorratio',
#                VLDR: 'volumedepolarization',
#                PLDR: 'particledepolarization',
                }

def error_method_var(value):
    var = xr.DataArray(np.int8(value),
                       name='error_retrieval_method',
                       attrs={'long_name': 'method used for the retrieval of uncertainties',
                              'flag_values': [np.int8(MC), np.int8(ASS)],
                              'flag_meanings': 'monte_carlo error_propagation',
                              '_FillValue': NC_FILL_BYTE})
    return var
