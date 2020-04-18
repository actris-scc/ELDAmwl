# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""

from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.database.db_functions import read_raman_bsc_params


class RamanBscParams(BackscatterParams):

    def __init__(self):
        super(RamanBscParams, self).__init__()
        self.raman_sig_id = None

        self.raman_bsc_method = None

    @classmethod
    def from_db(cls, general_params):
        result = super(RamanBscParams, cls)
        rbp = read_raman_bsc_params(general_params.prod_id)
        result.raman_bsc_method = rbp['ram_bsc_method']
        return result

    def add_signal_role(self, signal):
        super(RamanBscParams, self)
        if signal.is_Raman_sig:
            self.raman_sig_id = signal.channel_id_str

