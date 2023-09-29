from copy import deepcopy

from ELDAmwl.products import Products
from ELDAmwl.utils.constants import BSCR


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

    @property
    def bsc_ratio(self):
        """xarray.DataArray(imensions = time, level): bckscatter ratio (dimensionless)
        """
        result = self.data / self.ds.mol_backscatter + 1
        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Backscatters, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
        dct.data_vars.calibration_range = self.calibr_window


class BackscatterRatios(Products):
    """
    time series of backscatter ratio profiles
    """

    calibr_window = None

    @classmethod
    def from_bsc(cls, bsc):
        """creates an instance of BackscatterRatios with meta data and values from bsc.

        Args:
            bsc (:class:`Backscatters`): time series of backscatter coefficient profiles
        """
        result = cls()

        result.ds = deepcopy(bsc.ds)
        result.ds['data'] = bsc.bsc_ratio
        result.ds['err'] = result.ds.data * bsc.rel_err

        result.emission_wavelength = bsc.emission_wavelength
        result.num_scan_angles = bsc.num_scan_angles

        result.params = deepcopy(bsc.params)
        result.params.general_params.product_type = BSCR
        result.params.general_params.prod_id = f''
        # result.params.general_params.prod_id = f'{bsc.prod_id}_bscr'
        result.params.general_params.prod_id = f'{bsc.params.general_params.prod_id}_bscr'

        result.calibr_window = deepcopy(bsc.calibr_window)
        result.smooth_routine = bsc.smooth_routine

        return result

    # def to_meta_ds_dict(self, meta_data):
    #     # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
    #     # and attributes it with key self.mwl_meta_id to meta_data
    #     super(Backscatters, self).to_meta_ds_dict(meta_data)
    #     dct = meta_data[self.mwl_meta_id]
    #     self.params.to_meta_ds_dict(dct)
    #     dct.data_vars.calibration_range = self.calibr_window
