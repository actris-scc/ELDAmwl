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

    def screen_aerosol_free_layers(self, a_matrix, prod_type, res):
        # if there is a bsc ratio threshold defined for this product type
        if prod_type in self.cfg.MIN_BSC_RATIO:
            try:
                bsc_ratio_profile = self.data_storage.bsc_ratio_532(res)
                bad_idxs = np.where(bsc_ratio_profile.data < self.cfg.MIN_BSC_RATIO[prod_type])
                # apply the profile information in bad_idxs on every wavelength of matrix
                for wl in range(a_matrix.a_matrix.dims['wavelength']):
                    a_matrix.quality_flag[wl][bad_idxs] = a_matrix.quality_flag[wl][bad_idxs] | BELOW_MIN_BSCR

            except NotFoundInStorage:
                self.logger.error(f'screening for aerosol free layers cannot be done for {PRODUCT_TYPE_NAME[prod_type]} '
                                  f'because no bsc ratio is available for {RESOLUTION_STR[res]} resolution')
                # todo: discuss with giuseppe whether to raise an exception here

    def run_single_product_tests(self):
        for res in RESOLUTIONS:
            # all product types that are defined for this resolution
            p_types = self.product_params.prod_types(res=res)
            for prod_type in p_types:
                a_matrix = self.qc_product_matrix[res][prod_type]

                self.screen_aerosol_free_layers(a_matrix, prod_type, res)
        #         self.screen_uncertainties(a_matrix, prod_type)

    def run(self):
        self.prepare()

        self.run_single_product_tests()

        # todo: implement quality control
        # todo: add quality flag for complete profile (e.g. this profile causes bad angströms,
        #                                               aod / integral of this profile too large, )
        #                                               additionally to flag profile
        #  1) screen for negative values -> done on single product profile level
        # todo: 1a) if bsc profile has negative area in the middle -> skip complete profile
        #  2) screen for too large error -> done on single product profile level
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
