# -*- coding: utf-8 -*-
"""Classes for getting derived products like lidar ratio, particle depolarization ratio etc.
"""
from ELDAmwl.backscatter.bsc_ratio.operation import StandardBackscatterRatioFactory
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.lidar_ratio.operation import LidarRatioFactory
from ELDAmwl.utils.constants import RESOLUTIONS, RESOLUTION_STR
from ELDAmwl.angstroem_exponent.operation import AngstroemExpFactory
from ELDAmwl.utils.constants import RESOLUTIONS


class GetDerivedProductsDefault(BaseOperation):
    """
    """

#    data_storage = None
    product_params = None

    def run(self):
        # todo: write status of retrieval in database table eldamwl_product_status

        self.product_params = self.kwargs['product_params']

        self.get_derived_products()

    def single_products_quality_control(self):
        for res in RESOLUTIONS:
            all_products = self.product_params.derived_products(res=res)
            for prod_param in all_products:
                prod_id = prod_param.prod_id_str
                product = self.data_storage.derived_product_common_smooth(prod_id, res)
                product.quality_control()
                self.data_storage.set_derived_products_qc(prod_id, res, product)

    def get_derived_products(self):
        self.get_standard_bsc_ratio()
        self.get_lidar_ratios()
        self.get_angstroem_exps()
        self.single_products_quality_control()

    def get_standard_bsc_ratio(self):
        """
        get the standard backscatter ratio profile for determination of aerosol free layers
        Returns: None

        """
        for res in RESOLUTIONS:
            bsc_ratio = StandardBackscatterRatioFactory()(resolution=res).get_product()
            if bsc_ratio is not None:
                self.data_storage.set_bsc_ratio_532(res, bsc_ratio)

    def get_lidar_ratios(self):
        for res in RESOLUTIONS:
            lr_params = self.product_params.lidar_ratio_products(res=res)
            if len(lr_params) == 0:
                self.logger.warning(f'no lidar ratio product will be calculated with {RESOLUTION_STR[res]} resolution')

            for lr_param in lr_params:
                prod_id = lr_param.prod_id_str
                self.logger.info('get lidar ratio at {0} nm (product id {1})'.format(
                    lr_param.general_params.emission_wavelength,
                    prod_id
                ))

                lr = LidarRatioFactory()(
                    lr_param=lr_param,
                    resolution=res).get_product()

                self.data_storage.set_derived_products(
                    prod_id, res, lr)

    def get_angstroem_exps(self):
        for res in RESOLUTIONS:
            ae_params = self.product_params.angstroem_exp_products(res=res)

            if len(ae_params) == 0:
                self.logger.warning(f'no angstroem exponent product will be calculated'
                                    f'with {RESOLUTION_STR[res]} resolution')

            for ae_param in ae_params:
                prod_id = ae_param.prod_id_str
                self.logger.info('get angstroem exponent at {0} nm - {1} nm (product id {2}, {3})'.format(
                    ae_param.lambda1_params.general_params.emission_wavelength,
                    ae_param.lambda2_params.general_params.emission_wavelength,
                    prod_id,
                    RESOLUTION_STR[res]
                ))

                ae = AngstroemExpFactory()(
                    ae_param=ae_param,
                    resolution=res).get_product()

                self.data_storage.set_derived_products(
                    prod_id, res, ae)


class GetDerivedProducts(BaseOperationFactory):
    """
    Args:
        product_params: global MeasurementParams
    """

    name = 'GetDerivedProducts'

    def __call__(self, **kwargs):
        assert 'product_params' in kwargs

        self.smooth_type = kwargs['product_params'].smooth_params.smooth_type
        res = super(GetDerivedProducts, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'GetDerivedProductsDefault' .
        """
        return GetDerivedProductsDefault.__name__


registry.register_class(GetDerivedProducts,
                        GetDerivedProductsDefault.__name__,
                        GetDerivedProductsDefault)
