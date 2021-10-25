from ELDAmwl.operations.backscatter.common.params import BackscatterParams
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.utils.constants import RAMAN


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
