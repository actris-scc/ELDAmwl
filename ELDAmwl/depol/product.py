from ELDAmwl.products import Products


class VLDRs(Products):
    """
    time series of volume linear depolarization ratio profiles
    """
    @classmethod
    def init(cls, sigratio, p_params, **kwargs):
        """creates an empty instance of volume linear depolarization ratios with meta data copied from sigratio.

        The signals were previously prepared by `.PrepareDepolSignals` .

        Args:
            sigratio (`.Signals`): time series of signal ratio profiles
            p_params (`.VLDRParams`):
                                    calculation params
                                    of the VLRD product
        """

        result = super(VLDRs, cls).from_signal(sigratio, p_params)

        result.has_sys_err = True

        return result

    # @property
    # def bsc_ratio(self):
    #     """xarray.DataArray(imensions = time, level): bckscatter ratio (dimensionless)
    #     """
    #     result = self.data / self.mol_backscatter + 1
    #     return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(VLDRs, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
