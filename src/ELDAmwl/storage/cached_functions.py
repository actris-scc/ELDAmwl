# -*- coding: utf-8 -*-
"""functions which are often calles with same parameters. Their results can be cached"""

from functools import lru_cache
from scipy.signal import savgol_coeffs
from zope import component

from ELDAmwl.component.interface import IDBFunc


@lru_cache(maxsize=100)
def sg_coeffs(window_length, order):
    return savgol_coeffs(window_length, order)


@lru_cache(maxsize=100)
def sg_used_binres(eff_binres):
    used_binres = (eff_binres + 0.86) / 0.62
    odd_binres = ((used_binres - 1)/2).round() * 2 + 1

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
