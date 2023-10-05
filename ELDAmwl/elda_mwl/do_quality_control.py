from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NotFoundInStorage
from ELDAmwl.utils.constants import NEG_DATA, UNCERTAINTY_TOO_LARGE, BSCR, RESOLUTION_STR, PRODUCT_TYPE_NAME, \
    BELOW_MIN_BSCR
from ELDAmwl.utils.constants import RESOLUTIONS


import numpy as np


class QualityControlDefault(BaseOperation):
    """
    synergetic quality control of all products
    """

    product_params = None

    def prepare(self):
        """
        makes a local copy (self.qc_product_matrix) of the matrices of all resolutions and product types in data storage
        this copy will then be modified by the class methods
        Returns: None

        """
        self.product_params = self.kwargs['product_params']

    def run_multi_product_tests(self):
        pass

    def run(self):
        self.prepare()

        self.run_multi_product_tests()
        #self.filter_data()
        #self.clip_data()

        # todo: implement quality control
        # done: add quality flag for complete profile (e.g. this profile causes bad angstroem exponents,
        #                                               aod / integral of this profile too large, )
        #                                               additionally to flag profile
        #  1) screen for negative values -> done on single product profile level
        #  1a) if bsc profile has negative area in the middle -> skip complete profile
        #  2) screen for too large error -> done on single product profile level
        #  3) screen derived products for layers with no aerosol (bsc ratio < threshold)
        #  4) if there are more than 1 bsc at the same wavelength
        #           -> decide which one to use (use the one with best test results on angstroem and lidar ratio)
        #           -> we have decided that this case is not allowed. check in the beginning
        # todo: 5) test data in aerosol layers for thresholds in lidar ratio and angstroem exp
        # todo: 5a) based on lidar ratio and angstroem profiles: select if one profile is bad
        #           (remove the profile in a way that NUMBER of remaining good profiles is max
        # todo: 6) profiles which has more than 10% bad points in 5) -> skip completely
        # todo: do not allow empty matrix (1 variable with no data at all
        # todo: 2 file versions: one with quality controlled and screened data (for user),
        #                       one with full profiles and qc flag (only for CARS internal use)
        #         maybe the full output is written only if a certain command line parameter is set
        # todo: write quality flags in regular output files (in expert user section)


class QualityControl(BaseOperationFactory):
    """
    """

    name = 'QualityControl'

    def __call__(self, **kwargs):
        assert 'product_params' in kwargs

        res = super(QualityControl, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'QualityControlDefault' .
        """
        return QualityControlDefault.__name__


registry.register_class(QualityControl,
                        QualityControlDefault.__name__,
                        QualityControlDefault)
