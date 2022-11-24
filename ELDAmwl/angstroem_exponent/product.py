from ELDAmwl.products import Products


class AngstroemExps(Products):
    """
    time series of lidar ratio profiles
    """
    @classmethod
    def init(cls, lwvl, hwvl, p_params, **kwargs):
        """calculates AngstroemExp from two backscatter or two extinction profiles at different emission wavelengths

        Args:
            lwvl (Backscatters/Extinctions): time series of backscatter/extinction coefficient profiles at the lowest wavelength
            hwvl (Backscatters/Extinctions): time series of backscatter/extinction coefficient profiles at the highest wavelength
            p_params (ELDAmwl.operations.angstroem_exponent.params.AngstroemExpParams) # ToDo check
        """
        result = super(AngstroemExps, cls).from_signal(lwvl, hwvl, p_params, **kwargs)

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(AngstroemExps, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
