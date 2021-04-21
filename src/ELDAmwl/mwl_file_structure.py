# -*- coding: utf-8 -*-
"""constants describing the structure of mwl output file"""

from addict import Dict
import xarray as xr
import numpy as np

from ELDAmwl.constants import LOWRES, HIGHRES, RESOLUTION_STR, NC_FILL_BYTE, MC, ASS
from ELDAmwl.constants import RBSC, EBSC, EXT, LR, AE, CR, VLDR, PLDR
from ELDAmwl.database.db_functions import read_ext_algorithms

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
               META_DATA: ['cloud_mask_type',
                           'scc_product_type',
                           'molecular_calculation_source'],
               }

HEADER_ATTRS = {GENERAL: ['measurement_ID',
                          'system', 'hoi_system_ID', 'hoi_configuration_ID',
                          'institution', 'location', 'station_ID',
                          'pi', 'data_originator',
                          'data_processing_institution', 'comment', 'title',
                          'source', 'references', 'processor_name',
                          'measurement_start_datetime', 'measurement_stop_datetime'],
                META_DATA: ['hoi_system_ID',
                            'hoi_configuration_ID',
#                            'elpp_history',
                            'molecular_calculation_source_file'],
                }

TITLE = 'Profiles of aerosol optical properties'
REFERENCES = 'Project website at http://www.earlinet.org'
PROCESSOR_NAME = 'ELDAmwl'

NC_VAR_NAMES = {RBSC: 'backscatter',
                EBSC: 'backscatter',
                EXT: 'extinction',
                LR: 'lidarratio',
                AE: 'angstroemexponent',
                CR: 'colorratio',
                VLDR: 'volumedepolarization',
                PLDR: 'particledepolarization',
                }

UNITS = {RBSC: '1/(m*sr)',
         EBSC: '1/(m*sr)',
         EXT: '1/m',
         LR: 'sr',
         AE: '1',
         CR: '1',
         VLDR: '1',
         PLDR: '1',
         }

LONG_NAMES = {RBSC: 'particle backscatter coefficient',
         EBSC: 'particle backscatter coefficient',
         EXT: 'particle extinction coefficient',
         LR: 'particle lidar ratio',
#         AE: 'particle angstroem exponent',
#         CR: 'color ratio',
         VLDR: 'volume linear depolarization ratio',
         PLDR: 'particle linear depolarization ratio',
         }

COO_ATTR = 'longitude latitude'
ANC_VAR_ATT = 'error_{} vertical_resolution'

def data_attrs(p_type):
    return {'long_name': LONG_NAMES[p_type],
            'units': UNITS[p_type],
            'ancillary_variables': ANC_VAR_ATT.format(NC_VAR_NAMES[p_type]),
#            'coordinates': COO_ATTR,
            }

def err_attrs(p_type):
    return {'long_name': 'absolute statistical uncertainty of {}'.format(NC_VAR_NAMES[p_type]),
            'units': UNITS[p_type],
            'coordinates': COO_ATTR,
            }

def error_method_var(value):
    var = xr.DataArray(np.int8(value),
                       name='error_retrieval_method',
                       attrs={'long_name': 'method used for the retrieval of uncertainties',
                              'flag_values': [np.int8(MC), np.int8(ASS)],
                              'flag_meanings': 'monte_carlo error_propagation',
                              '_FillValue': NC_FILL_BYTE})
    return var

def ext_method_var(value):
    ext_methods = read_ext_algorithms()
    values=[]
    meanings = []
    for v, m in ext_methods.items():
        values.append(np.int8(v))
        meanings.append(m.replace(' ', '_'))
    meanings_str = ' '.join(meanings)

    var = xr.DataArray(np.int8(value),
                       name='evaluation_algorithm',
                       attrs={'long_name': 'algorithm used for the extinction retrieval',
                              'flag_values': values,
                              'flag_meanings': meanings_str,
                              '_FillValue': NC_FILL_BYTE})
    return var
