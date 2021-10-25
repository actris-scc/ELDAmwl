from ELDAmwl.bases.base import Params
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.errors.exceptions import CalRangeHigherThanValid
from ELDAmwl.operations.backscatter.common.backscatter_calibration import BscCalibrationParams
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.utils.constants import ELAST
from ELDAmwl.utils.constants import IT
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import RAMAN
from zope import component

import numpy as np


class Backscatters(Products):
    """
    time series of backscatter profiles
    """

    calibr_window = None

    @classmethod
    def init(cls, signal, p_params, calibr_window=None):
        """calculates Backscatters from an elastic signal.

        The signal was previously prepared by PrepareBscSignals .

        Args:
            signal (:class:`Signals`): time series of signal profiles
            p_params (:class:`BackscatterParams`):
                        calculation params of the backscatter product
            calibr_window (tuple):
                        first and last height_axis of the calibration window [m]
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)
        # cls.calibr_window = calibr_window  ToDo: Ina debug

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Backscatters, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
        dct.data_vars.calibration_range = self.calibr_window


class RamanBackscatters(Backscatters):

    @classmethod
    def init(cls, sigratio, p_params, calibr_window=None):
        """calculates RamanBackscatters from a signal ratio.

        The signals were previously prepared by PrepareBscSignals .

        Args:
            sigratio (:class:`Signals`): time series
                                        of signal ratio profiles
            p_params (:class:`RamanBackscatterParams`):
                                    calculation params
                                    of the backscatter product
            calibr_window (xarray.DataArray): variable
                                    'backscatter_calibration_range'
                                    (time, nv: 2)
        """

        result = super(RamanBackscatters, cls).init(sigratio,
                                                    p_params,
                                                    calibr_window)
        # todo ina: check documentation calibr_window is tupe or dataarray?

        result.calibr_window = calibr_window

        # cal_first_lev = sigratio.heights_to_levels(
        #     calibr_window[:, 0])
        # cal_last_lev = sigratio.heights_to_levels(
        #     calibr_window[:, 1])
        #
        # error_params = Dict({'err_threshold':
        #                     p_params.quality_params.error_threshold,
        #                      })
        #
        # calibr_value = DataPoint.from_data(
        #     p_params.calibration_params.cal_value, 0, 0)
        # cal_params = Dict({'cal_first_lev': cal_first_lev.values,
        #                    'cal_last_lev': cal_last_lev.values,
        #                    'calibr_value': calibr_value})
        #
        # calc_routine = CalcRamanBscProfile()(prod_id=p_params.prod_id_str)
        #
        # result.ds = calc_routine.run(sigratio=sigratio.ds,
        #                              error_params=error_params,
        #                              calibration=cal_params)
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
        self.bsc_method = None

    def from_db(self, general_params):
        super(BackscatterParams, self).from_db(general_params)

        self.calibration_params = BscCalibrationParams.from_db(general_params)  # noqa E501
        if self.calibration_params.cal_interval.max_height > \
                self.general_params.valid_alt_range.max_height:
            raise CalRangeHigherThanValid(self.prod_id_str)

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
            self.logger.debug('channel {0} is no elast signal'.format(signal.channel_id_str))

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        mwl_vars = MWLFileVarsFromDB()
        dct.data_vars.retrieval_method = mwl_vars.bsc_method_var(self.bsc_method)
        self.calibration_params.to_meta_ds_dict(dct)


class RamanBscParams(BackscatterParams):

    def __init__(self):
        super(RamanBscParams, self).__init__()
        self.raman_sig_id = None

        self.raman_bsc_algorithm = None
        self.bsc_method = RAMAN

    def from_db(self, general_params):
        super(RamanBscParams, self).from_db(general_params)

        rbp = self.db_func.read_raman_bsc_params(general_params.prod_id)
        self.raman_bsc_algorithm = rbp['ram_bsc_method']
        self.get_error_params(rbp)
        self.smooth_params.smooth_method = rbp['smooth_method']

    def add_signal_role(self, signal):
        super(RamanBscParams, self).add_signal_role(signal)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(RamanBscParams, self).to_meta_ds_dict(dct)
        dct.data_vars.evaluation_algorithm = MWLFileVarsFromDB().ram_bsc_algorithm_var(self.raman_bsc_algorithm)


class ElastBscParams(BackscatterParams):

    def __init__(self):
        super(ElastBscParams, self).__init__()
        self.sub_params += ['iter_params']
        self.iter_params = None

        self.bsc_method = ELAST
        self.elast_bsc_algorithm = None
        self.lr_input_method = None

    def from_db(self, general_params):
        super(ElastBscParams, self).from_db(general_params)

        ebp = self.db_func.read_elast_bsc_params(general_params.prod_id)

        self.elast_bsc_algorithm = ebp['elast_bsc_method']
        if self.elast_bsc_algorithm == IT:
            self.iter_params = IterBscParams.from_db(general_params)  # noqa E501

        self.lr_input_method = ebp['lr_input_method']

        self.get_error_params(ebp)

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(ElastBscParams, self).to_meta_ds_dict(dct)
        dct.data_vars.evaluation_algorithm = MWLFileVarsFromDB().elast_bsc_algorithm_var(self.elast_bsc_algorithm)
        if self.iter_params is not None:
            self.iter_params.to_meta_ds_dict(dct)


class IterBscParams(Params):

    conv_crit = np.nan
    max_iteration_count = NC_FILL_INT
    ram_bsc_method = None

    @classmethod
    def from_db(cls, general_params):
        result = cls
        db_func = component.queryUtility(IDBFunc)
        ibp = db_func.read_iter_bsc_params(general_params.prod_id)

        result.conv_crit = ibp['conv_crit']
        result.max_iteration_count = ibp['max_iteration_count']
        result.ram_bsc_method = ibp['ram_bsc_method']

        return result

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        pass
