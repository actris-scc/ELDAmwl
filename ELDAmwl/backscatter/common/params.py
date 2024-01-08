from ELDAmwl.backscatter.common.calibration.params import BscCalibrationParams
from ELDAmwl.bases.base import Params
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.errors.exceptions import CalRangeHigherThanValid
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams
from zope import component

import numpy as np


class BackscatterParams(ProductParams):

    def __init__(self):
        super(BackscatterParams, self).__init__()
        self.sub_params += ['calibration_params']
        self.calibration_params = None
        self.total_sig_id_str = None
        self.total_sig_id = None
        self.transm_sig_id_str = None
        self.transm_sig_id = None
        self.refl_sig_id_str = None
        self.refl_sig_id = None
        self.cross_sig_id_str = None
        self.cross_sig_id = None
        self.parallel_sig_id_str = None
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
                self.total_sig_id_str = signal.channel_id_str
                self.total_sig_id = signal.channel_id.values
            if signal.is_cross_sig:
                self.cross_sig_id_str = signal.channel_id_str
                self.cross_sig_id = signal.channel_id.values
            if signal.is_parallel_sig:
                self.parallel_sig_id_str = signal.channel_id_str
                self.parallel_sig_id = signal.channel_id.values
            if signal.is_transm_sig:
                self.transm_sig_id_str = signal.channel_id_str
                self.transm_sig_id = signal.channel_id.values
            if signal.is_refl_sig:
                self.refl_sig_id_str = signal.channel_id_str
                self.refl_sig_id = signal.channel_id.values
        else:
            self.logger.debug('channel {0} is no elast signal'.format(signal.channel_id_str))

    def to_meta_ds_dict(self, dct):
        """writes parameter content into Dict for further export in mwl file

        Args:
            dct (addict.Dict): is a dict which will be converted into dataset. has the keys 'attrs' and 'data_vars'

        Returns:

        """
        mwl_vars = MWLFileVarsFromDB()
        dct.data_vars.retrieval_method = mwl_vars.bsc_method_var(self.bsc_method)
        self.calibration_params.to_meta_ds_dict(dct)

    @property
    def prod_id_bsc_ratio_str(self):
        return f'{self.general_params.prod_id}_bscr'


class IterBscParams(Params):

    conv_crit = np.nan
    max_iteration_count = None
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
            dct (addict.Dict): is a dict which will be converted into dataset. It has the keys 'attrs' and 'data_vars'.

        Returns:

        """
        pass
