from copy import deepcopy
from ELDAmwl.products import Products
from ELDAmwl.utils.constants import BSCR


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
        result.profile_qf = deepcopy(bsc.profile_qf)

        return result
