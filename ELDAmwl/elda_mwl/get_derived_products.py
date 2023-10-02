# -*- coding: utf-8 -*-
"""Classes for getting derived products like lidar ratio, particle depolarization ratio etc.
"""
from ELDAmwl.backscatter.bsc_ratio.operation import StandardBackscatterRatioFactory
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.lidar_ratio.operation import LidarRatioFactory
from ELDAmwl.utils.constants import RESOLUTIONS, RESOLUTION_STR


class GetDerivedProductsDefault(BaseOperation):
    """
    """

#    data_storage = None
    product_params = None

    def run(self):
        # todo: write status of retrieval in database table eldamwl_product_status

        self.product_params = self.kwargs['product_params']

        self.get_derived_products()

    def get_derived_products(self):
        self.get_standard_bsc_ratio()
        self.get_lidar_ratios()

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
