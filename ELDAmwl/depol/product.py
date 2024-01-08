from ELDAmwl.products import Products
from ELDAmwl.utils.constants import VALUE_OUTSIDE_VALID_RANGE

class VLDRs(Products):
    """
    time series of volume linear depolarization ratio profiles
    """
    @classmethod
    def init(cls, sigratio, p_params, **kwargs):
        """creates an empty instance of volume linear depolarization ratios with meta data copied from sigratio.

        The signals were previously prepared by `.PrepareDepolSignals` .

        Args:
            sigratio (`.Signals`): time series of signal ratio profiles (enumerator = reflected, denominator = transmitted signal)  # noqa E501
            p_params (`.VLDRParams`): retrieval params
                                    of the VLDR product
        """

        result = super(VLDRs, cls).from_signal(sigratio, p_params)

        result.has_sys_err = True

        return result

    def screen_valid_data_range(self):
        # todo: test if the mol depol is available here
        min_value = self.ds.molecular_depolarization_ratio
        max_value = self.cfg.VALID_DATA_RANGE[self.product_type][1]

        self.flag_values_below_threshold(min_value, VALUE_OUTSIDE_VALID_RANGE)
        self.flag_values_above_threshold(max_value, VALUE_OUTSIDE_VALID_RANGE)

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(VLDRs, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
