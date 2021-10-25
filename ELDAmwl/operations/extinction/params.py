import numpy as np
import xarray as xr

from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams
from ELDAmwl.utils.constants import NC_FILL_STR


class ExtinctionParams(ProductParams):

    def __init__(self):
        super(ExtinctionParams, self).__init__()
        self.raman_sig_id = None
        self.ext_method = np.nan
        self.angstroem = np.nan
        self.correct_ovl = False
        self.ovl_filename = NC_FILL_STR

    def from_db(self, general_params):
        super(ExtinctionParams, self).from_db(general_params)

        ep = self.db_func.read_extinction_params(general_params.prod_id)

        self.angstroem = ep['angstroem']
        self.correct_ovl = ep['overlap_correction']
        self.ovl_filename = ep['overlap_file']
        self.ext_method = ep['ext_method']

        self.get_error_params(ep)

    def add_signal_role(self, signal):
        super(ExtinctionParams, self)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str
        else:
            self.logger.debug('channel {0} is no Raman signal'.format(signal.channel_id_str))

    @property
    def ang_exp_asDataArray(self):
        return xr.DataArray(self.angstroem,
                            name='assumed_angstroem_exponent',
                            attrs={'long_name': 'assumed Angstroem exponent '
                                                'for the extinction '
                                                'retrieval',
                                   'units': '1'})

    @property
    def smooth_params_auto(self):
        res = super(ExtinctionParams, self).smooth_params_auto()
        # todo: get bin resolutions from actual height
        #  resolution of the used algorithm
        res.max_binres_low = 39
        res.max_binres_high = 155
        res.max_bin_delta = 2
        return res

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(ExtinctionParams, self).to_meta_ds_dict(dct)
        dct.data_vars.assumed_angstroem_exponent = self.ang_exp_asDataArray
        mwl_vars = MWLFileVarsFromDB()
        dct.data_vars.evaluation_algorithm = mwl_vars.ext_algorithm_var(self.ext_method)

        if self.correct_ovl:
            dct.attrs.overlap_correction_file = self.ovl_filename
