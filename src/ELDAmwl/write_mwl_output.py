# -*- coding: utf-8 -*-
"""Classes for writing multi-wavelength output to NetCDF
"""
import os

from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.registry import registry
from ELDAmwl.configs.config import PRODUCT_PATH

class WriteMWLOutputDefault(BaseOperation):
    """
    """

    data_storage = None
    product_params = None
    out_filename = None

    def mwl_filename(self):
        return 'dummy.nc'

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']
        self.out_filename = os.path.join(PRODUCT_PATH, self.mwl_filename())

        ext = self.data_storage.basic_product_common_smooth('377', 0)
        ext1=xr.Dataset({'value':ext.data,
                         'absolute_statistical_uncertainty': ext.err,
                         'time_bounds':ext.ds.time_bounds})
        xr.concat([ext1.ds, ext2.ds], dim='wl')

        for param in self.product_params.basic_products():
            product = self.data_storage.data.basic_products_common_smooth.LOWRES[param.prod_id_str]
            product.ds.to_netcdf(path=self.out_filename,
                                 mode='a',
                                 format='NETCDF4',
                                 group='low_res_products')


class WriteMWLOutput(BaseOperationFactory):
    """
    Args:
        data_storage (ELDAmwl.data_storage.DataStorage): global data storage
        product_params: global MeasurementParams
    """

    name = 'WriteMWLOutput'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'product_params' in kwargs
        res = super(WriteMWLOutput, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareSignals' .
        """
        return WriteMWLOutputDefault.__name__


registry.register_class(WriteMWLOutput,
                        WriteMWLOutputDefault.__name__,
                        WriteMWLOutputDefault)
