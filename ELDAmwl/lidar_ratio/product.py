from ELDAmwl.products import Products


class LidarRatios(Products):
    """
    time series of lidar ratio profiles
    """
    @classmethod
    def init(cls, ext, bsc, p_params, **kwargs):
        """calculates LidarRatios from a backscatter and an extinction profile.

        Args:
            bsc (Backscatters): time series of backscatter coefficient profiles
            ext (Extinctions): time series of extinction coefficient profiles
            p_params (ELDAmwl.operations.lidar_ratio.params.LidarRatioParams)
        """
        result = super(LidarRatios, cls).from_signal(ext, p_params, **kwargs)

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(LidarRatios, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
