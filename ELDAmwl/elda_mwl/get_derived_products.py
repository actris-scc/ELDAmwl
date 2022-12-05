# -*- coding: utf-8 -*-
"""Classes for getting derived products like lidar ratio, particle depolarization ratio etc.
"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.lidar_ratio.operation import LidarRatioFactory
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

    def get_derived_products(self):
        self.get_lidar_ratios()

    def get_lidar_ratios(self):
        for lr_param in self.product_params.lidar_ratio_products():
            prod_id = lr_param.prod_id_str

            for res in RESOLUTIONS:
                if lr_param in self.product_params.all_products_of_res(res):
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
