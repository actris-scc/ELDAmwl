from ELDAmwl.products import Products


class Backscatters(Products):
    """
    time series of backscatter profiles
    """

    calibr_window = None

    @classmethod
    def init(cls, signal, p_params, calibr_window=None):
        """creates an empty instance of Backscatters with meta data copied from signal.

        The signal was previously prepared by PrepareBscSignals.

        Args:
            signal (:class:`Signals`): time series of signal profiles
            p_params (:class:`ELDAmwl.operations.backscatter.common.params.BackscatterParams`):
                        calculation params of the backscatter product
            calibr_window (xarray.DataArray): variable
                                    'backscatter_calibration_range'
                                    (time, nv: 2)
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)

        result.calibr_window = calibr_window

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Backscatters, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
        dct.data_vars.calibration_range = self.calibr_window
