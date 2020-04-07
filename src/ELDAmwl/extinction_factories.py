# -*- coding: utf-8 -*-
"""Classes for extinction calculation"""
from addict import Dict
from copy import deepcopy

from ELDAmwl.constants import NC_FILL_STR, MC
from ELDAmwl.database.db_functions import read_extinction_algorithm, read_extinction_params
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.log import logger
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry
import numpy as np
import xarray as xr

class ExtinctionParams(ProductParams):

    def __init__(self):
        super(ExtinctionParams, self).__init__()
        self.raman_sig_id = None
        self.ext_method = np.nan
        self.angstroem = np.nan
        self.correct_ovl = False
        self.ovl_filename = NC_FILL_STR

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params

        ep = read_extinction_params(general_params.prod_id)

        result.angstroem = ep['angstroem']
        result.correct_ovl = ep['overlap_correction']
        result.ovl_filename = ep['overlap_file']
        result.ext_method = ep['ext_method']
        result.general_params.error_method = ep['error_method']

        return result

    def add_signal_role(self, signal):
        super(ExtinctionParams, self)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str
        else:
            logger.debug('channel {0} is no Raman signal'.
                         format(signal.channel_id_str))

class Extinctions(Products):
    """
    time series of extinction profiles
    """
    @classmethod
    def from_signal(cls, signal, p_params):
        result = cls()

        ext_params = Dict({'detection_wavelength': signal.detection_wavelength,
                           'emission_wavelength': signal.emission_wavelength,
                           'angstroem': xr.DataArray(p_params.angstroem,
                                                     name='angstroem_exponent',
                                                     attrs={'long_name':
                                                                'Angstroem exponent '
                                                                'for the extinction retrieval'})})
        sig_slope = SignalSlope()(signal=signal.ds).run()
        result.ds = SlopeToExtinction()(slope=sig_slope,
                                        ext_params=ext_params).run()

        return result


class SlopeToExtinction(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
    extinction coefficient from signal slope. In this case, it
    will be always an instance of getSlopeToExtinction().
    """

    name = 'SlopeToExtinction'

    def __call__(self, **kwargs):
        assert 'slope' in kwargs
        assert 'ext_params' in kwargs
        res = super(SlopeToExtinction, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'getSlopeToExtinction' .
        """
        return 'getSlopeToExtinction'


class getSlopeToExtinction(BaseOperation):
    """
    Calculates particle extinction coefficient from signal slope.
    """
    def run(self):
        """
        """
        slope = self.kwargs['slope']
        ext_params = self.kwargs['ext_params']

        det_wl = ext_params.detection_wavelength
        em_wl = ext_params.emission_wavelength
        wl_dep = ext_params.wavelength_dependence

        wl_factor = 1 / (1 + pow((det_wl/em_wl), wl_dep))

        result = deepcopy(slope)
        result['data'] = slope.data * wl_factor
        result['err'] = slope.err * wl_factor

        return result


registry.register_class(SlopeToExtinction, 'getSlopeToExtinction',
                        getSlopeToExtinction)


class Extinction(BaseOperationFactory):
    """

    """

    name = 'Extinction'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'ext_param' in kwargs
        res = super(Extinction, self).__call__(**kwargs)
        return res


    def get_classname_from_db(self):
        """

        return: always 'getExtinction' .
        """
        return getExtinction.__class__.__name__


class getExtinction(BaseOperation):
    """
    derives particle extinction coefficient.
    """

    data_storage = None

    def get_product(self):
        self.data_storage = self.kwargs['data_storage']
        self.param = self.kwargs['ext_param']

        if not self.param.includes_product_merging():
            raman_sig = self.data_storage.prepared_signal(self.param.prod_id_str,
                                                          self.param.raman_sig_id)
            result = Extinctions.from_signal(raman_sig, self.param)
        else:
            #result = Extinctions.from_merged_signals()
            pass

        if self.param.error_method == MC:
            pass

        return result


registry.register_class(Extinction,
                        getExtinction.__class__.__name__,
                        getExtinction)


class SignalSlope(BaseOperationFactory):
    """
    Calculates signal slope.
    """

    name = 'SignalSlope'

    def get_classname_from_db(self):
        return read_extinction_algorithm(281)


class LinFit(BaseOperation):
    """

    """
    name = 'LinFit'

    def __init__(self, weight):
        super(LinFit, self).__init__()
        # print('calculate linear fit with weight', weight)


class WeightedLinFit(BaseOperation):
    """

    """
    def __init__(self, str):
        super(WeightedLinFit, self).__init__()
        # print('WeightedLinFit sagt ', str)
        LinFit(True)


registry.register_class(SignalSlope, 'WeightedLinearFit', WeightedLinFit)


class NonWeightedLinFit(BaseOperation):
    """

    """

    def __init__(self, str):
        super(NonWeightedLinFit, self).__init__()
        # print('NonWeightedLinFit sagt ', str)
        LinFit(False)


registry.register_class(SignalSlope, 'NonWeightedLinearFit', NonWeightedLinFit)
