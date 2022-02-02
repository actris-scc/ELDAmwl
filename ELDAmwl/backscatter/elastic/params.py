from ELDAmwl.backscatter.common.params import BackscatterParams
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.utils.constants import FIXED
from ELDAmwl.utils.constants import ELAST
from ELDAmwl.utils.constants import IT


class ElastBscParams(BackscatterParams):

    def __init__(self):
        super(ElastBscParams, self).__init__()
        self.sub_params += ['iter_params']
        self.iter_params = None

        self.bsc_method = ELAST
        self.elast_bsc_algorithm = None
        self.lr_input_method = None
        self.assumed_lr = None
        self.assumed_lr_error = None

    def from_db(self, general_params):
        super(ElastBscParams, self).from_db(general_params)

        ebp = self.db_func.read_elast_bsc_params(general_params.prod_id)

        self.elast_bsc_algorithm = ebp['elast_bsc_method']
        self.smooth_params.smooth_method = ebp['smooth_method']

        if self.elast_bsc_algorithm == IT:
            self.iter_params = IterBscParams.from_db(general_params)  # noqa E501

        self.lr_input_method = ebp['lr_input_method']
        if self.lr_input_method == FIXED:
            self.assumed_lr = ebp['fixed_lr']
            self.assumed_lr_error = ebp['fixed_lr_error']

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
