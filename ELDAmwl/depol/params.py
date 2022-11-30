from zope.component import queryUtility

from ELDAmwl.bases.base import Params
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams
from datetime import datetime
from numpy import square as sqr

from ELDAmwl.utils.constants import MAX_CALIBR_DPEOL


class DepolUncertaintyParams(Params):
    a_K = None
    b_K = None
    c_K = None
    a_upper = None
    b_upper = None
    c_upper = None
    a_lower = None
    b_lower = None
    c_lower = None

    gain_factor_correction = None

    @classmethod
    def from_db(cls, general_params, measurement_date):
        result = cls()
        db_func = queryUtility(IDBFunc)
        query = db_func.get_depol_uncertainties_query(general_params.prod_id, measurement_date)
        # query = db_func.get_depol_uncertainties_query(365, datetime(2017,7,1))

        result.a_K = query.a_K
        result.b_K = query.b_K
        result.c_K = query.c_K
        result.a_upper = query.a_upperbound
        result.b_upper = query.b_upperbound
        result.c_upper = query.c_upperbound
        result.a_lower = query.a_lowerbound
        result.b_lower = query.b_lowerbound
        result.c_lower = query.c_lowerbound

        result.gain_factor_correction = result.a_K \
                                        + result.b_K * MAX_CALIBR_DPEOL \
                                        + result.c_K * sqr(MAX_CALIBR_DPEOL)

        return result


class VLDRParams(ProductParams):

    def __init__(self):
        super(VLDRParams, self).__init__()
        self.sub_params += ['depol_uncertainty_params']

        self.transm_sig_id_str = None
        self.transm_sig_id = None
        self.refl_sig_id_str = None
        self.refl_sig_id = None
        self.cross_sig_id_str = None
        self.cross_sig_id = None
        self.parallel_sig_id_str = None
        self.parallel_sig_id = None

        self.vldr_algorithm = None

        self.crosstalk_g_refl = None
        self.crosstalk_h_refl = None
        self.crosstalk_g_transm = None
        self.crosstalk_h_transm = None

    def from_db(self, general_params):
        super(VLDRParams, self).from_db(general_params)

        # the measurement time is not yet known when this parameters are created
        self.depol_uncertainty_params = None

        vdp = self.db_func.read_vldr_params(general_params.prod_id)
        self.vldr_algorithm = vdp['vldr_method']
        self.get_error_params(vdp)
        self.smooth_params.smooth_method = vdp['smooth_method']

    def add_params_from_signal(self, signal):
        # there can be different parameters for calculation the uncertainty of
        # VLDR for different measurement times. When creating the VLDR parameter,
        # the measurement time is not yet known.
        # therefore, read the H, G, and uncertainty parameters now with the start time of the signal
        self.logger.debug('add depol parameters of signal {0} to VLDRParams'.format(int(signal.channel_id)))

        if self.depol_uncertainty_params is None:
            self.depol_uncertainty_params = DepolUncertaintyParams.from_db(
                self.general_params,
                signal.ds.time[0].values)

        if signal.channel_id == self.refl_sig_id:
            self.crosstalk_g_refl = float(signal.g.value)
            self.crosstalk_h_refl = float(signal.h.value)

        elif signal.channel_id == self.transm_sig_id:
            self.crosstalk_g_transm = float(signal.g.value)
            self.crosstalk_h_transm = float(signal.h.value)
        else:
            self.logger.error('signal {} is neither reflected nor transmitted one '
                              '(as it should be)'.format(signal.channel_id))


    def add_signal_role(self, signal):
        super(VLDRParams, self)
        if signal.is_elast_sig:
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
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        mwl_vars = MWLFileVarsFromDB()
        # dct.data_vars.retrieval_method = mwl_vars.bsc_method_var(self.bsc_method)
        # self.calibration_params.to_meta_ds_dict(dct)
