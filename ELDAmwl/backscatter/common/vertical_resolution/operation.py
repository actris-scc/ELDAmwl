from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.utils.constants import NC_FILL_STR

import numpy as np


class SavGolayEffBinRes(BaseOperation):
    """calculates effective bin resolution for a given number of bins
    used for smoothing a profile with Savitzky-Golay method

    The calculation is done according to Mattis et al. 2016 with the equation
    eff_binres = round(used_bins_ELDA * 1.24 - 0.24)
    In this paper, used_bins_ELDA corresponds to the radius of the smooth window.
    Here, used_bins is the diameter of the smooth window:
    used_bins = used_bins_ELDA *2 +1
    =>  eff_binres = round(used_bins_ELDA * 1.24 - 0.24) = round(used_bins * 0.62 - 0.86)
"""

    name = 'SavGolayEffBinRes'

    def run(self, **kwargs):
        """
        starts the calculation

        Keyword Args:
            used_bins(integer): number of bins used for the calculation of Sav-Gol filter
                                (= diameter of the smoothing window)

        Returns:
            eff_binres(integer): resulting effective resolution in terms of vertical bins

        """
        assert 'used_bins' in kwargs

        used_bins = kwargs['used_bins']
        eff_binres = np.array(used_bins * 0.62 - 0.86)
        result = eff_binres.round().astype(int)

        return result


class SavGolayUsedBinRes(BaseOperation):
    """calculates the number of bins which have to be
    used for smoothing a profile with Savitzky-Golay method in order to achieve
    a given effective bin resolution

    The calculation is done according to Mattis et al. 2016 with the equation
    used_bins_ELDA = round((eff_binres + 0.24) / 1.24).
    In this paper, used_bins_ELDA corresponds to the radius of the smooth window.
    Here, used_bins is the diameter of the smooth window:
    used_bins = used_bins_ELDA *2 +1 = round((eb+0.86)/0.62)
    """

    name = 'SavGolayUsedBinRes'

    def run(self, **kwargs):
        """
        starts the calculation

        Keyword Args:
            eff_binres(integer): required effective vertical resolution in terms of bins

        Returns:
            used_bins(integer): number of bins (= diameter of the smooth window) to be used for
                                the calculation of the Sav-Gol filter in order to achieve the required effective
                                vertical bin resolution. must be an odd number.

        """
        assert 'eff_binres' in kwargs

        eff_binres = np.array(kwargs['eff_binres'])
        used_binres = (eff_binres + 0.86) / 0.62
        odd_binres = ((used_binres - 1) / 2).round() * 2 + 1

        # result = sg_used_binres(eff_binres.tolist())
        result = odd_binres.astype(int)

        return result


class RamBscEffBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of the effective bin resolution for a given number of bins
    used in the retrieval of ...

    Keyword Args:
            prod_id (str): id of the product
    """

    name = 'RamBscEffBinRes'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(RamBscEffBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_raman_bsc_effbin_algorithm(self.prod_id)


class RamBscUsedBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of how many bins have to be used ...

    Keyword Args:
    """

    name = 'RamBscUsedBinRes'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(RamBscUsedBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_raman_bsc_usedbin_algorithm(self.prod_id)


class ElastBscEffBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of the effective bin resolution for a given number of bins
    used in the retrieval of ...

    Keyword Args:
            prod_id (str): id of the product
    """

    name = 'ElastBscEffBinRes'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(ElastBscEffBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_elast_bsc_effbin_algorithm(self.prod_id)


class ElastBscUsedBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of how many bins have to be used for the
    ... in order to achieve the required effective bin resolution of ...

    Keyword Args:
    """
    name = 'ElastBscUsedBinRes'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(ElastBscUsedBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_elast_bsc_usedbin_algorithm(self.prod_id)


registry.register_class(RamBscUsedBinRes,
                        SavGolayUsedBinRes.__name__,
                        SavGolayUsedBinRes)

registry.register_class(RamBscEffBinRes,
                        SavGolayEffBinRes.__name__,
                        SavGolayEffBinRes)

registry.register_class(ElastBscUsedBinRes,
                        SavGolayUsedBinRes.__name__,
                        SavGolayUsedBinRes)

registry.register_class(ElastBscEffBinRes,
                        SavGolayEffBinRes.__name__,
                        SavGolayEffBinRes)
