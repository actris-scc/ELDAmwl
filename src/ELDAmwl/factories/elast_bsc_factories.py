# -*- coding: utf-8 -*-
"""Classes for Raman backscatter calculation"""
from zope import component

from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.factories.backscatter_factories import BackscatterParams
from ELDAmwl.bases.base import Params
from ELDAmwl.utils.constants import IT, ELAST
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory

import numpy as np

from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB


class ElastBscParams(BackscatterParams):

    def __init__(self):
        super(ElastBscParams, self).__init__()
        self.sub_params += ['iter_params']
        self.iter_params = None

        self.bsc_method = ELAST
        self.elast_bsc_algorithm = None
        self.lr_input_method = None

    def from_db(self, general_params):
        super(ElastBscParams, self).from_db(general_params)

        ebp = self.db_func.read_elast_bsc_params(general_params.prod_id)

        self.elast_bsc_algorithm = ebp['elast_bsc_method']
        if self.elast_bsc_algorithm == IT:
            self.iter_params = IterBscParams.from_db(general_params)  # noqa E501

        self.lr_input_method = ebp['lr_input_method']

        self.get_error_params(ebp)

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(ElastBscParams, self).to_meta_ds_dict(dct)
        dct.data_vars.evaluation_algorithm = MWLFileVarsFromDB().elast_bsc_algorithm_var(self.elast_bsc_algorithm)
        if self.iter_params is not None:
            self.iter_params.to_meta_ds_dict(dct)


class IterBscParams(Params):

    conv_crit = np.nan
    max_iteration_count = NC_FILL_INT
    ram_bsc_method = None

    @classmethod
    def from_db(cls, general_params):
        result = cls
        db_func = component.queryUtility(IDBFunc)
        ibp = db_func.read_iter_bsc_params(general_params.prod_id)

        result.conv_crit = ibp['conv_crit']
        result.max_iteration_count = ibp['max_iteration_count']
        result.ram_bsc_method = ibp['ram_bsc_method']

        return result

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        pass


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
