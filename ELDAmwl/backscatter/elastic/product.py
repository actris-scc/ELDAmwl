from ELDAmwl.backscatter.common.product import Backscatters


class ElastBackscatters(Backscatters):

    @classmethod
    def init(cls, elast_sig, p_params, calibr_window=None):
        """creates an empty instance of ElastBackscatters with meta data copied from elast_sig.

        The signals were previously prepared by PrepareBscSignals .

        Args:
            elast_sig (:class:`Signals`): time series
                                        of elastic signals
            p_params (:class:`RamanBackscatterParams`):
                                    calculation params
                                    of the backscatter product
            calibr_window (xarray.DataArray): variable
                                    'backscatter_calibration_range'
                                    (time, nv: 2)
        """

        result = super(ElastBackscatters, cls).init(elast_sig,
                                                    p_params,
                                                    calibr_window)
        # result.calibr_window = calibr_window

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(ElastBackscatters, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        dct.data_vars.assumed_particle_lidar_ratio = self.ds.assumed_particle_lidar_ratio
