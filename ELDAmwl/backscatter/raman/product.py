from ELDAmwl.backscatter.common.product import Backscatters


class RamanBackscatters(Backscatters):

    @classmethod
    def init(cls, sigratio, p_params, calibr_window=None):
        """creates an empty instance of RamanBackscatters with meta data copied from sigratio.

        The signals were previously prepared by PrepareBscSignals .

        Args:
            sigratio (:class:`Signals`): time series
                                        of signal ratio profiles
            p_params (:class:`RamanBackscatterParams`):
                                    calculation params
                                    of the backscatter product
            calibr_window (xarray.DataArray): variable
                                    'backscatter_calibration_range'
                                    (time, nv: 2)
        """

        result = super(RamanBackscatters, cls).init(sigratio,
                                                    p_params,
                                                    calibr_window)

        # result.calibr_window = calibr_window

        # cal_first_lev = sigratio.heights_to_levels(
        #     calibr_window[:, 0])
        # cal_last_lev = sigratio.heights_to_levels(
        #     calibr_window[:, 1])
        #
        # error_params = Dict({'err_threshold':
        #                     p_params.quality_params.error_threshold,
        #                      })
        #
        # calibr_value = DataPoint.from_data(
        #     p_params.calibration_params.cal_value, 0, 0)
        # cal_params = Dict({'cal_first_lev': cal_first_lev.values,
        #                    'cal_last_lev': cal_last_lev.values,
        #                    'calibr_value': calibr_value})
        #
        # calc_routine = CalcRamanBscProfile()(prod_id=p_params.prod_id_str)
        #
        # result.ds = calc_routine.run(sigratio=sigratio.ds,
        #                              error_params=error_params,
        #                              calibration=cal_params)
        return result
