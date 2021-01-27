# -*- coding: utf-8 -*-
"""Classes for writing multi-wavelength output to NetCDF
"""
import os
import xarray as xr

from addict import Dict
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
        header = self.data_storage.header.attrs

        result = header.station.station_ID
        # numeric 3 digits according to db table _product_types (for example 002)
        # result += '_' +
        # numeric 7 digits (for example 0000213)
        # result += '_' +
        # result += '_' + start_time.strftime('%Y%m%d%h%m')
        # result += '_' + end_time.strftime('%Y%m%d%h%m')
        result += header.measurement_ID
        result += '_ELDAmwl'
        # result += '_v{}'.format()
        result += '.nc'

        return result

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']
        self.out_filename = os.path.join(PRODUCT_PATH, self.mwl_filename())

        file_data = Dict({'attrs': Dict(), 'data_vars': Dict()})

        self.data_storage.header.to_dataset(file_data)

        ds = xr.Dataset(data_vars=file_data.data_vars,
                        coords={},
                        attrs=file_data.attrs)
        # write global attributes and variables
        #ds.to_netcdf(path='d:/temp/dummy.nc', mode='w', format='NETCDF4')
        # write group attributes and variables
        #ds.to_netcdf(path='d:/temp/dummy.nc', mode='a', format='NETCDF4', group='b')

        ext = self.data_storage.basic_product_common_smooth('377', 0)
        ext1 = xr.Dataset({'value':ext.data,
                         'absolute_statistical_uncertainty': ext.err,
                         'time_bounds':ext.ds.time_bounds})
        #xr.concat([ext1.ds, ext2.ds], dim='wl')

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
