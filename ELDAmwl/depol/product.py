from ELDAmwl.products import Products


class VLDRs(Products):
    """
    time series of extinction profiles
    """
    @classmethod
    def init(cls, sigratio, p_params, **kwargs):
        """creates an empty instance of volume linear depolarization ratios with meta data copied from sigratio.

        The signals were previously prepared by PrepareBscSignals .

        Args:
            sigratio (:class:`Signals`): time series
                                        of signal ratio profiles
            p_params (:class:`ELDAmwl.depol.params.VLDRParams`):
                                    calculation params
                                    of the VLRD product
        """

        result = super(VLDRs, cls).init(sigratio, p_params)

        result.has_sys_err = True

        # cls.calc_eff_bin_res_routine = ExtEffBinRes()(prod_id=p_params.prod_id_str)

        return result


    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(VLDRs, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
