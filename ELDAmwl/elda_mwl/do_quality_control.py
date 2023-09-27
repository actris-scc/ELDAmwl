from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.utils.constants import NEG_DATA
from ELDAmwl.utils.constants import RESOLUTIONS

import numpy as np


class QualityControlDefault(BaseOperation):
    """
    synergetic quality control of all products
    """

    product_params = None
    qc_product_matrix = None

    def prepare(self):
        """
        makes a local copy (self.qc_product_matrix) of the matrices of all resolutions and product types in data storage
        this copy will then be modified by the class methods
        Returns: None

        """
        self.product_params = self.kwargs['product_params']

        self.qc_product_matrix = Dict()
        for res in RESOLUTIONS:
            p_types = self.product_params.prod_types(res=res)
            for prod_type in p_types:
                self.qc_product_matrix[res][prod_type] = self.data_storage.product_matrix(prod_type, res)

    def screen_negative_values(self, a_matrix):
        """

        """
        # maximum possible value = value + 2 * uncertainty
        max_values = a_matrix.data + 2 * a_matrix.absolute_statistical_uncertainty
        bad_idxs = np.where(max_values < 0)
        # a_matrix.data[bad_idxs] = np.nan
        # do not exclude bad data points in every step in order to allow accumulation of flags
        # todo: remove bad points in the end

        a_matrix.qflag[bad_idxs] = a_matrix.qflag[bad_idxs] | NEG_DATA

    def run_single_product_tests(self):
        for res in RESOLUTIONS:
            p_types = self.product_params.prod_types(res=res)
            for prod_type in p_types:
                a_matrix = self.qc_product_matrix[res][prod_type]

                self.screen_negative_values(a_matrix)

    def run(self):
        self.prepare()

        self.run_single_product_tests()

        # todo: implement quality control
        # todo: add quality flag for complete profile (e.g. this profile causes bad angströms,
        #                                               aod / integral of this profile too large, )
        #                                               additionally to flag profile
        # todo: 1) screen for negative values
        # todo: 1a) if bsc profile has negative area in the middle -> skip complete profile
        # todo: 2) screen for too large error
        # todo: 3) screen derived products for layers with no aerosol (bsc ratio < threshold)
        # todo: 4) if there are more than 1 bsc at the same wavelegnth
        #           -> decide which one to use (use the one with best test results on angstroem and lidar ratio)
        # todo: 5) test data in aerosol layers for thresholds in lidar ratio and angström exp
        # todo: 5a) based on lidar ratio and angström profiles: select if one profile is bad
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
