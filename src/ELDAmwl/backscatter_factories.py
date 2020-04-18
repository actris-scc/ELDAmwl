# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from copy import deepcopy
from addict import Dict
from ELDAmwl.base import Params
from ELDAmwl.constants import MC
from ELDAmwl.database.db_functions import get_bsc_cal_params_query
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.log import logger
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry


class BscCalibrationParams(Params):

    def __init__(self):
        super(BscCalibrationParams, self).__init__()
        self.CalRangeSearchMethod = None
        self.WindowWidth = None
        self.CalValue = None
        self.CalInterval = Dict({'from': None, 'to': None})

    @classmethod
    def from_db(cls, general_params):
        result = cls()

        query = get_bsc_cal_params_query(general_params.prod_id,
                                         general_params.product_type)

        result.CalRangeSearchMethod = query.BscCalibrOption._calRangeSearchMethod_ID  # noqa E501
        result.WindowWidth = query.BscCalibrOption.WindowWidth
        result.CalValue = query.BscCalibrOption.calValue
        result.CalInterval['from'] = query.BscCalibrOption.LowestHeight
        result.CalInterval['to'] = query.BscCalibrOption.TopHeight

        return result


class BackscatterParams(ProductParams):

    def __init__(self):
        super(BackscatterParams, self).__init__()
        self.sub_params += ['calibration_params']
        self.calibration_params = None
        self.total_sig_id = None
        self.transm_sig_id = None
        self.refl_sig_id = None
        self.cross_sig_id = None
        self.parallel_sig_id = None

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params
        result.calibration_params = BscCalibrationParams.from_db(general_params)  # noqa E501
        return result

    def add_signal_role(self, signal):
        super(BackscatterParams, self)
        if signal.is_elast_sig:
            if signal.is_total_sig:
                self.total_sig_id = signal.channel_id_str
            if signal.is_cross_sig:
                self.cross_sig_id = signal.channel_id_str
            if signal.is_parallel_sig:
                self.parallel_sig_id = signal.channel_id_str
            if signal.is_transm_sig:
                self.transm_sig_id = signal.channel_id_str
            if signal.is_refl_sig:
                self.refl_sig_id = signal.channel_id_str
        else:
            logger.debug('channel {0} is no elast signal'.
                         format(signal.channel_id_str))


class Backscatters(Products):
    """
    time series of backscatter profiles
    """
    @classmethod
    def from_signal(cls, signal, p_params):
        """calculates Backscatters from an elastic signal.

        The signal was previously prepared by PrepareBscSignals .

        Args:
            signal (Signals): time series of signal profiles
            p_params (BackscatterParams)
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)
        return result


class BackscatterFactory(BaseOperationFactory):
    """

    """

    name = 'BackscatterFactory'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_param' in kwargs
        assert 'autosmooth' in kwargs
        res = super(BackscatterFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'BackscatterFactoryDefault' .
        """
        return BackscatterFactoryDefault.__name__


class BackscatterFactoryDefault(BaseOperation):
    """
    derives particle backscatter coefficients.
    """

    name = 'BackscatterFactoryDefault'

    data_storage = None
    elast_sig = None

    def get_product(self):
        self.data_storage = self.kwargs['data_storage']
        self.param = self.kwargs['bsc_param']

        if not self.param.includes_product_merging():
            self.elast_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.total_sig_id)

            if self.kwargs['autosmooth']:
                pass
                # smooth_res = ExtinctionAutosmooth()(
                #     signal=raman_sig.ds,
                #     smooth_params=self.param.smooth_params,
                # ).run()

            # smoothed_sig = deepcopy(raman_sig)
            # smoothed_sig.ds['binres'] = smooth_res
            # result = Backscatters.from_signal(smoothed_sig, self.param)
        else:
            # result = Extinctions.from_merged_signals()
            pass

        if self.param.error_method == MC:
            pass

        return result


class CalcRamanBscProfile(BaseOperationFactory):
    """calculates Raman bsc profile from elast and Raman signals and calibration window"""

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for bsc calculation

        Returns: name of the class for the bsc calculation
        """
        return read_extinction_algorithm(self.prod_id)

    pass


class CalcRamanBscProfileViaBR(BaseOperation):
    """calculates Raman backscatter profile via BR"""
    pass


class CalcElastBscProfile(BaseOperationFactory):
    """calculates bsc profiles from signal and calibration window"""
    pass


class CalcBscProfileKF(BaseOperation):
    """calculates bsc profiles with Klett-Fernal method"""
    pass


class CalcBscProfileIter(BaseOperation):
    """calculates bsc profiles with iterative method"""
    pass

registry.register_class(BackscatterFactory,
                        BackscatterFactoryDefault.__name__,
                        BackscatterFactoryDefault)
