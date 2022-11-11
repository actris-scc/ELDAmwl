from ELDAmwl.backscatter.common.vertical_resolution.operation import SavGolayUsedBinRes, SavGolayEffBinRes
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.utils.constants import NC_FILL_STR

import numpy as np


class VLDREffBinRes(BaseOperationFactory):
    """
    Creates a Class for the calculation of the effective bin resolution for a given number of bins
    used in the retrieval of the vldr.

    Keyword Args:
        prod_id (str): id of the product
    """

    name = 'VLDREffBinRes'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(VLDREffBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the vldr calculation
        """
        return self.db_func.read_vldr_effbin_algorithm(self.prod_id)


class VLDRUsedBinRes(BaseOperationFactory):
    """
   Creates a Class for the calculation of how many bins have to be used
    in order to achieve the required effective bin resolution of the vldr profile.

    Keyword Args:
        prod_id (str): id of the product
    """

    name = 'VLDRUsedBinRes'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(VLDRUsedBinRes, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use

        Returns: name of the class for the vldr calculation
        """
        return self.db_func.read_vldr_usedbin_algorithm(self.prod_id)

# todo: check whether it needs a db access here
registry.register_class(VLDRUsedBinRes,
                        SavGolayUsedBinRes.__name__,
                        SavGolayUsedBinRes)

registry.register_class(VLDREffBinRes,
                        SavGolayEffBinRes.__name__,
                        SavGolayEffBinRes)

