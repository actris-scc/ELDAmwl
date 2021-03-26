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
from ELDAmwl.constants import ELDA_MWL_VERSION, MWL
from ELDAmwl.constants import HIGHRES, LOWRES, RESOLUTIONS, RESOLUTION_STR, NC_VAR_NAMES
from ELDAmwl.exceptions import NotFoundInStorage


class WriteMWLOutputDefault(BaseOperation):
    """
    """

    data_storage = None
    product_params = None
    out_filename = None

    def mwl_filename(self):
        header = self.data_storage.header

        template = '{stat_id}_{prod_type_id}_{prod_id}_{start}_{end}_{meas_id}_ELDAmwl_v{version}.nc'
        result = template.format(stat_id=header.attrs.station_ID,
                                 prod_type_id=str(MWL).zfill(3),
                                 prod_id=str(self.product_params.mwl_product_id).zfill(7),
                                 start=header.start_time.strftime('%Y%m%d%H%M'),
                                 end=header.end_time.strftime('%Y%m%d%H%M'),
                                 meas_id=header.attrs.measurement_ID,
                                 version=ELDA_MWL_VERSION,
                                 )
        return result

    def write_header(self):
        # create empty container for global attributes and variables
        global_data = Dict({'attrs': Dict(), 'data_vars': Dict()})
        # fill container with header information
        self.data_storage.header.to_ds_dict(global_data)
        # convert into Dataset
        ds = xr.Dataset(data_vars=global_data.data_vars,
                        coords={},
                        attrs=global_data.attrs)
        # write global attributes and variables
        ds.to_netcdf(path=self.out_filename, mode='w', format='NETCDF4')
        ds.close()

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']
        self.out_filename = os.path.join(PRODUCT_PATH, self.mwl_filename())

        self.write_header()  # must be called first because this function creates the file

        meta_data = Dict()
        for res in RESOLUTIONS:
            group_data = Dict({'attrs': Dict(), 'data_vars': Dict()})
            meta_data[res] = Dict()

            # todo cloudmask shall have common altitude, time and timebounds variables
            group_data.data_vars.cloud_mask = self.data_storage.get_common_cloud_mask(res)

            for prod_type in self.product_params.prod_types(res=res):
                for wl in self.product_params.wavelengths(res=res):
                    prod_str = '{type}_{wl}'.format(type=NC_VAR_NAMES[prod_type],
                                                    wl=str(wl))
                    meta_data[res][prod_str] = Dict()
                    prod_id = self.product_params.prod_id(prod_type, wl)
                    if prod_id:
                        try:
                            prod = self.data_storage.basic_product_common_smooth(prod_id, res)
                            # write meta data into dataset, add link to meta data to var ?
                            prod.params.to_dataset(meta_data[res][prod_str])
                            # if not first, concat with previous
                            pass
                        except NotFoundInStorage:
                            # add empty profile
                            pass
                    else:
                        # add empty profile
                        pass

            ds = xr.Dataset(data_vars=group_data.data_vars,
                            coords={},
                            attrs=group_data.attrs)
            ds.to_netcdf(path=self.out_filename,
                         mode='a',
                         format='NETCDF4',
                         group='{}_products'.format(RESOLUTION_STR[res]))
            ds.close()



        # write group attributes and variables
        #ds.to_netcdf(path='d:/temp/dummy.nc', mode='a', format='NETCDF4', group='b')
        #ds.to_netcdf(path='d:/temp/dummy.nc', mode='a', format='NETCDF4', group='/b/a')

        ext = self.data_storage.basic_product_common_smooth('377', LOWRES)
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
