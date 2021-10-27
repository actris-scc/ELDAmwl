from ELDAmwl.extinction.vertical_resolution.operation import ExtEffBinRes
from ELDAmwl.products import Products


class Extinctions(Products):
    """
    time series of extinction profiles
    """
    @classmethod
    def init(cls, signal, p_params, **kwargs):
        """creates an empty instance of Extinctions, meta data are copied from the Raman signal.

        The signal was previously prepared by PrepareExtSignals .

        Args:
            signal (Signals): time series of signal profiles
            p_params (ELDAmwl.operations.extinction.params.ExtinctionParams)
        """
        result = super(Extinctions, cls).from_signal(signal, p_params, **kwargs)

        cls.calc_eff_bin_res_routine = ExtEffBinRes()(prod_id=p_params.prod_id_str)

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Extinctions, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
