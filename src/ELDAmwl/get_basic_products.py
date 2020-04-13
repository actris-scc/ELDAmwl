# -*- coding: utf-8 -*-
"""Classes for getting basic products
"""
from ELDAmwl.backscatter_factories import BackscatterFactory
from ELDAmwl.extinction_factories import ExtinctionFactory
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.registry import registry


class GetBasicProductsDefault(BaseOperation):
    """
    """

    data_storage = None
    product_params = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']

        for ext_param in self.product_params.extinction_products():
            extinction = ExtinctionFactory()(
                data_storage=self.data_storage,
                ext_param=ext_param,
                autosmooth=True,
            ).get_product()
            self.data_storage.set_basic_product_auto_smooth(
                ext_param.prod_id_str, extinction)

        for bsc_param in self.product_params.all_bsc_products():
            pass
            # bsc = BackscatterFactory()(
            #     data_storage=self.data_storage,
            #     bsc_param=bsc_param,
            #     autosmooth=True,
            # ).get_product()
            # self.data_storage.set_basic_product_auto_smooth(
            #     bsc_param.prod_id_str, bsc)


class GetBasicProducts(BaseOperationFactory):
    """
    Args:
        data_storage (ELDAmwl.data_storage.DataStorage): global data storage
        product_params: global MeasurementParams
    """

    name = 'GetBasicProducts'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'product_params' in kwargs
        res = super(GetBasicProducts, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareSignals' .
        """
        return GetBasicProductsDefault.__name__


registry.register_class(GetBasicProducts,
                        GetBasicProductsDefault.__name__,
                        GetBasicProductsDefault)
