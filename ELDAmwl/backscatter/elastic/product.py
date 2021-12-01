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
