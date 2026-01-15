from ELDAmwl.products import Products


class PLDRs(Products):
    """
    time series of particle linear depolarization ratio profiles
    """

    @classmethod
    def init(cls, vldr, p_params, resolution, **kwargs):
        """creates an empty instance of particle linear depolarization ratios with meta data copied from vldr.

        Args:
            vldr (`.VLDRs`): time series of VLDR profiles
            p_params (`.PLDRParams`): retrieval params of the PLDR product
        """
        result = super(PLDRs, cls).from_signal(vldr, p_params, **kwargs)
        result.has_sys_err = True
        result.resolution = resolution

        return result

    def copy(self, target=None):
        if target is None:
            new = PLDRs()
        else:
            new = target
        new = super(PLDRs, self).copy(target=new)

        return new

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(PLDRs, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)

