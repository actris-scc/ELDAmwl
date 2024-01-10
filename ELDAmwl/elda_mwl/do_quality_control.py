from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NotFoundInStorage
from ELDAmwl.utils.constants import NEG_DATA, UNCERTAINTY_TOO_LARGE, BSCR, RESOLUTION_STR, PRODUCT_TYPE_NAME, \
    BELOW_MIN_BSCR, LOWRES, EBSC, RBSC
from ELDAmwl.utils.constants import RESOLUTIONS


import numpy as np


class QualityControlDefault(BaseOperation):
    """
    synergetic quality control of all products
    """

    product_params = None
    failed_products = None

    def prepare(self):
        """
        makes a local copy (self.qc_product_matrix) of the matrices of all resolutions and product types in data storage
        this copy will then be modified by the class methods
        Returns: None

        """
        self.product_params = self.kwargs['product_params']
        self.failed_products = Dict()

    def test_vldr(self):
        for vldr_param in self.find_vldr_out_of_range():
            vldr_id = vldr_param.prod_id_str
            wl = vldr_param.emission_wavelength
            self.logger.warning(f'VLDR product {vldr_id} did not pass the quality check. '
                                f'It is marked as "failed".')

            for bsc_type in [EBSC, RBSC]:
                for related_bsc_param in self.product_params.prod_params(bsc_type, wl, include_failed=True):
                    if related_bsc_param.is_bsc_from_depol_components():
                        self.logger.warning(f'Backscatter product {related_bsc_param.prod_id_str} is related '
                                            f'to the failed VLDR product {vldr_id}. ')
                        self.handle_failed_basic_products([related_bsc_param])

    def find_vldr_out_of_range(self):
        """VLDR out of range  those for which at all resolutions and
        all time slices the profile flags are P_VALUE_OUTSIDE_VALID_RANGE"""

        result = []
        for prod_param in self.product_params.vldr_products(include_failed=True):
            prod_id = prod_param.prod_id_str

            retrieval_failed = True
            for res in RESOLUTIONS:
                if prod_param in self.product_params.all_products_of_res(res, include_failed=True):
                    profile = self.data_storage.product_qc(prod_id, res)
                    retrieval_failed = retrieval_failed & profile.is_out_of_range()

            if retrieval_failed:
                result.append(prod_id)

        return result

    def find_failed_basic_products(self):
        """failed basic products are those for which at all resolutions and
        all time slices the profile flags are not ALL_OK"""

        result = []
        for prod_param in self.product_params.basic_products():
            prod_id = prod_param.prod_id_str

            retrieval_failed = True
            for res in RESOLUTIONS:
                if prod_param in self.product_params.all_products_of_res(res):
                    profile = self.data_storage.product_qc(prod_id, res)
                    retrieval_failed = retrieval_failed & profile.retrieval_failed()

            if retrieval_failed:
                result.append(prod_param)

        return result

    def find_related_derived_products(self, basic_prod_param):
        result = []
        prod_id = basic_prod_param.prod_id_str

        for lr_param in self.product_params.lidar_ratio_products():
            if (lr_param.bsc_prod_id == prod_id) or (lr_param.ext_prod_id == prod_id):
                result.append(lr_param)

        # todo: do the same for other derived product types
        # for ae_param in self.product_params.ang_exp_params():
        #     if (ae_param.prod_id_1 == prod_id) or (ae_param.prod_id_2 == prod_id):
        #         result.append(ae_param)
        #
        # for cr_param, pldr_params ...

        return result

    def handle_failed_basic_products(self, failed_basic_products):
        """
        flag products as failed,
        find related derived products and flag them as failed
        """
        for fbp_param in failed_basic_products:
            self.logger.warning(f'Product {fbp_param.prod_id_str} did not pass the quality check. '
                                f'It is marked as "failed".')
            fbp_param.mark_as_failed(self.product_params)

            for rdp_param in self.find_related_derived_products(fbp_param):
                self.logger.warning(f'Product {rdp_param.prod_id_str} was derived from a failed product. '
                                    f'It is marked as "failed", too.')
                rdp_param.mark_as_failed(self.product_params)

    def run(self):
        # 0a) products with bad profile flags in all res -> set as failed
        # 0b) for all failed products -> set invalid all derived products
        # 1) if vldr out of range -> if bsc at same wl is from_depol_components -> set invalid (all res, + related derived_products
        # 2) per time slice: if LR is out of range -> tag related bsc and ext
        # 3) per time slice: if ae is out of range -> tag related basic prods
        # 4) set invalid: basic prod with most tags + related derived prods
        # 5) repeat 2-4 until no tags left

        self.prepare()

        failed_basic_products = self.find_failed_basic_products()
        self.handle_failed_basic_products(failed_basic_products)

        self.test_vldr()
        # check whether low and high resolution of a product overlap

        res = LOWRES


        # : implement quality control
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
        #  5) test data in aerosol layers for thresholds in lidar ratio and angstroem exp
        # todo: 5a) based on lidar ratio and angstroem profiles: select if one profile is bad
        #           (remove the profile in a way that NUMBER of remaining good profiles is max
        #
        #  6) profiles which has more than 10% bad points in 5) -> skip completely
        #  7) do not allow empty matrix (1 variable with no data at all
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
