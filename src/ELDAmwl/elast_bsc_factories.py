# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""

from ELDAmwl.backscatter_factories import BackscatterParams
from ELDAmwl.base import Params
from ELDAmwl.constants import IT
from ELDAmwl.constants import NC_FILL_INT
from ELDAmwl.database.db_functions import read_elast_bsc_params
from ELDAmwl.database.db_functions import read_iter_bsc_params
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory

import numpy as np


class ElastBscParams(BackscatterParams):

    def __init__(self):
        super(ElastBscParams, self).__init__()
        self.sub_params += ['iter_params']
        self.iter_params = None

        self.elast_bsc_method = None
        self.lr_input_method = None

    def from_db(self, general_params):
        super(ElastBscParams, self).from_db(general_params)

        ebp = read_elast_bsc_params(general_params.prod_id)

        self.elast_bsc_method = ebp['elast_bsc_method']
        if self.elast_bsc_method == IT:
            self.iter_params = IterBscParams.from_db(general_params)  # noqa E501

        self.lr_input_method = ebp['lr_input_method']

        self.get_error_params(ebp)


class IterBscParams(Params):

    conv_crit = np.nan
    max_iteration_count = NC_FILL_INT
    ram_bsc_method = None

    @classmethod
    def from_db(cls, general_params):
        result = cls

        ibp = read_iter_bsc_params(general_params.prod_id)

        result.conv_crit = ibp['conv_crit']
        result.max_iteration_count = ibp['max_iteration_count']
        result.ram_bsc_method = ibp['ram_bsc_method']

        return result


class ElastBscEffBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of the effective bin resolution for a given number of bins
    used in the retrieval of ...

    Keyword Args:
    """

    pass


class ElastBscUsedBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of how many bins have to be used for the
    ... in order to achieve the required effective bin resolution of ...

    Keyword Args:
    """

    pass

class CalcElastBscProfile(BaseOperationFactory):
    """calculates bsc profiles from signal and calibration window"""
    pass


class CalcBscProfileKF(BaseOperation):
    """calculates bsc profiles with Klett-Fernal method"""
    pass


class CalcBscProfileIter(BaseOperation):
    """calculates bsc profiles with iterative method"""
    pass
