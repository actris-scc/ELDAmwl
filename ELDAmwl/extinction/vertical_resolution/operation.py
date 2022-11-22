from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.registry import registry
from zope import component

import numpy as np


class ExtEffBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of the effective bin resolution for a given number of bins
    used in the retrieval of the signal slope.

    Keyword Args:
        prod_id (str): id of the product
    """

    name = 'ExtEffBinRes'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']

        res = super(ExtEffBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ creates the classname from the name of the slope algorithm or the product id

        Returns: name of the class for the calculation of the effective bin resolution of the slope retrieval
        """
        db_func = component.queryUtility(IDBFunc)
        return db_func.read_ext_effbin_algorithm(self.prod_id)


class ExtUsedBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of how many bins have to be used for the linear fit
    in order to achieve the required effective bin resolutionof signal slope.

    Keyword Args:
        prod_id (str): id of the product
    """

    name = 'ExtUsedBinRes'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']

        res = super(ExtUsedBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ creates the classname from the name of the slope algorithm or the product id

        Returns: name of the class for the calculation of the used bin resolution of the slope retrieval
        """
        return self.db_func.read_ext_usedbin_algorithm(self.prod_id)


class LinFitEffBinRes(BaseOperation):
    """
    The calculation is done according to Mattis et al. 2016 with the equation
    eff_binres = round(used_bins * 0.85934 - 0.17802)
    """
    name = 'LinFit_EffBinRes'

    def run(self, **kwargs):
        """
        starts the calculation

        Keyword Args:
            used_bins(integer): number of bins used for the calculation of the linear fit (= diameter of the fit window)

        Returns:
            eff_binres(integer): resulting effective resolution in terms of vertical bins

        """
        assert 'used_bins' in kwargs

        used_bins = kwargs['used_bins']
        eff_binres = np.array(used_bins * 0.85934 - 0.17802)
        result = eff_binres.round().astype(int)

        return result


class LinFitUsedBinRes(BaseOperation):
    """
    The calculation is done according to Mattis et al. 2016 with the equation
    used_bins = round((eff_binres + 0.17802) / 0.85934)
    """
    name = 'LinFit_UsedBinRes'

    def run(self, **kwargs):
        """
        starts the calculation

        Keyword Args:
            eff_binres(integer): required effective vertical resolution in terms of bins

        Returns:
            used_bins(integer): number of bins (= diameter of the fit window) to be used for
                                the calculation of the linear fit in order to achieve the required effective
                                vertical bin resolution

        """
        assert 'eff_binres' in kwargs

        eff_binres = kwargs['eff_binres']
        used_binres = np.array((eff_binres + 0.17802) / 0.85934)
        result = used_binres.round().astype(int)

        return result


registry.register_class(ExtUsedBinRes,
                        LinFitUsedBinRes.__name__,
                        LinFitUsedBinRes)

registry.register_class(ExtEffBinRes,
                        LinFitEffBinRes.__name__,
                        LinFitEffBinRes)
