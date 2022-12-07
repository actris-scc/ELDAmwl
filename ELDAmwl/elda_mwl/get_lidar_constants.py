# -*- coding: utf-8 -*-
"""Classes for getting derived products like lidar ratio, particle depolarization ratio etc.
"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import ELDAmwlException
from ELDAmwl.lidar_constant.operation import LidarConstantFactory
from ELDAmwl.utils.constants import EBSC, RBSC


class GetLidarConstantsDefault(BaseOperation):
    """
    """

    mwl_product_params = None

    def run(self):
        self.mwl_product_params = self.kwargs['product_params']
        self.get_lidar_constants()

    def get_lidar_constants(self):
        wavelengths = self.mwl_product_params.wavelengths(prod_types=[RBSC, EBSC])
        if len(wavelengths) == 0:
            self.logger.warning('no lidar constants can be derived because no backscatter profiles are available')

        for wl in wavelengths:
            self.logger.info('get lidar constant at {0} nm'.format(wl))
            try:
                lc = LidarConstantFactory()(
                    wavelength=wl,
                    mwl_product_params=self.mwl_product_params).run()

                self.data_storage.set_lidar_constant(wl, lc)
            except ELDAmwlException as e:
                self.logger.error('could not derive lidar constant')


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
