# -*- coding: utf-8 -*-
"""functions which are often called with same parameters. Their results can be cached"""
import pickle

from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ICfg
from functools import lru_cache
from scipy.signal import savgol_coeffs
from zope import component

from ELDAmwl.config import register_config
from ELDAmwl.utils.path_utils import abs_file_path

# register_config(args=None)
#
# DEFAULT_ORDER = 2
# SG_PARAMS_FILENAME = abs_file_path(component.queryUtility(ICfg).SAV_GOLAY_FILE)
# # SG_PARAMS_FILENAME = 'sg_params.pickle'
#
SG_PARAMS = None

def gen_sg_params():
    global SG_PARAMS
    # register_config(args=None)

    DEFAULT_ORDER = 2
    SG_PARAMS_FILENAME = abs_file_path(component.queryUtility(ICfg).SAV_GOLAY_FILE)
    # SG_PARAMS_FILENAME = 'sg_params.pickle'

    # this code is no part of gen_sg_params()
    try:
        with open(SG_PARAMS_FILENAME, 'rb') as infile:
            SG_PARAMS = pickle.load(infile)
    except Exception as e:
        sg_param = {}
        for window_length in range(DEFAULT_ORDER + 1, 100):
            sg_param[window_length] = savgol_coeffs(window_length, DEFAULT_ORDER)
        with open(SG_PARAMS_FILENAME, 'wb') as outfile:
            pickle.dump(sg_param, outfile)
        SG_PARAMS = sg_param

def sg_coeffs(window_length, order):
    return SG_PARAMS[window_length]
    # todo: if requested window is not in file -> calculate params and add to file


@lru_cache(maxsize=100)
def sg_used_binres(eff_binres):
    used_binres = (eff_binres + 0.86) / 0.62
    odd_binres = ((used_binres - 1) / 2).round() * 2 + 1

    return odd_binres.astype(int)


@lru_cache()
def smooth_routine_from_db(method_id):
    db_func = component.queryUtility(IDBFunc)
    return db_func.read_smooth_routine(method_id)


# other candidates are functions for
# * retrieval of used and effective bin resolutions
# * converting height / altitude / range /bins
# * ! getting methods/options from db !
#    e.g. RamBscUsedBinRes.get_classname_from_db
