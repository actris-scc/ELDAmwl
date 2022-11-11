from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams


class VLDRParams(ProductParams):

    def __init__(self):
        super(VLDRParams, self).__init__()
        # self.sub_params += ['calibration_params']
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
        super(VLDRParams, self).from_db(general_params)

    def add_signal_role(self, signal):
        super(VLDRParams, self)
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


