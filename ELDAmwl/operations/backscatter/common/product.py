from ELDAmwl.products import Products


class Backscatters(Products):
    """
    time series of backscatter profiles
    """

    calibr_window = None

    @classmethod
    def init(cls, signal, p_params, calibr_window=None):
        """calculates Backscatters from an elastic signal.

        The signal was previously prepared by PrepareBscSignals .

        Args:
            signal (:class:`Signals`): time series of signal profiles
            p_params (:class:`ELDAmwl.operations.backscatter.common.params.BackscatterParams`):
                        calculation params of the backscatter product
            calibr_window (tuple):
                        first and last height_axis of the calibration window [m]
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)
        # cls.calibr_window = calibr_window  ToDo: Ina debug

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Backscatters, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
        dct.data_vars.calibration_range = self.calibr_window


class RamanBackscatters(Backscatters):

    @classmethod
    def init(cls, sigratio, p_params, calibr_window=None):
        """calculates RamanBackscatters from a signal ratio.

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
        # todo ina: check documentation calibr_window is tupe or dataarray?

        result.calibr_window = calibr_window

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


