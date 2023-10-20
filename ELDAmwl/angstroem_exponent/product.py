from ELDAmwl.products import Products



class AngstroemExps(Products):
    """
    time series of angstroem exponent profiles
    """
    @classmethod
    def init(cls, lambda1, lambda2, p_params, resolution, **kwargs):
        """calculates AngstroemExp from two backscatter or two extinction profiles at different emission wavelengths

        Args:
            lambda1 (Backscatters/Extinctions): time series of backscatter/extinction coefficient profiles at the lowest wavelength
            lambda2 (Backscatters/Extinctions): time series of backscatter/extinction coefficient profiles at the highest wavelength
            p_params (ELDAmwl.operations.angstroem_exponent.params.AngstroemExpParams) # ToDo check
        """
        result = super(AngstroemExps, cls).from_signal(lambda1, p_params, **kwargs)
        result.resolution = resolution

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(AngstroemExps, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
