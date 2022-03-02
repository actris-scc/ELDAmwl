# -*- coding: utf-8 -*-
"""Classes for getting derived products like lidar ratio, particle depolarization ratio etc.
"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.lidar_constant.operation import LidarConstantFactory
from ELDAmwl.lidar_ratio.operation import LidarRatioFactory
from ELDAmwl.utils.constants import RESOLUTIONS


class GetLidarConstantsDefault(BaseOperation):
    """
    """

    product_params = None

    def run(self):
        self.mwl_product_params = self.kwargs['product_params']
        self.get_lidar_constants()

    def get_lidar_constants(self):
        wavelengths = self.mwl_product_params.wavelengths()
        for wl in wavelengths:
            lc = LidarConstantFactory()(
                wl=wl,
                mwl_product_params=self.mwl_product_params).run()

            self.data_storage.set_lidar_constant(lc)


class GetLidarConstants(BaseOperationFactory):
    """
    Args:
        product_params: global MeasurementParams
    """

    name = 'GetLidarConstants'

    def __call__(self, **kwargs):
        assert 'product_params' in kwargs

        self.smooth_type = kwargs['product_params'].smooth_params.smooth_type
        res = super(GetLidarConstants, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'GetLidarConstantsDefault' .
        """
        return GetLidarConstantsDefault.__name__


registry.register_class(GetLidarConstants,
                        GetLidarConstantsDefault.__name__,
                        GetLidarConstantsDefault)
