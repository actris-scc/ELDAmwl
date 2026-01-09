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
        result = bsc.copy(target=result)

        result.ds['data'] = bsc.bsc_ratio
        result.ds['err'] = result.ds.data * bsc.rel_err

        result.params = deepcopy(bsc.params)
        result.params.general_params.product_type = BSCR
        result.params.general_params.prod_id = f'{bsc.params.general_params.prod_id}_bscr'

        return result

    def copy(self, target=None):
        if target is None:
            new = BackscatterRatios()
        else:
            new = target
        new = super(BackscatterRatios, self).copy(target=new)
        new.calibr_window = self.calibr_window.copy(deep=True)

        return new
