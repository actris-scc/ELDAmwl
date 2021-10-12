# -*- coding: utf-8 -*-
"""Classes for writing multi-wavelength output to NetCDF
"""
import os
import xarray as xr

from addict import Dict
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.component.registry import registry
from ELDAmwl.configs.config import PRODUCT_PATH
from ELDAmwl.utils.constants import ELDA_MWL_VERSION, MWL, EXT, LOWRES, HIGHRES, RBSC
from ELDAmwl.utils.constants import RESOLUTIONS


class WriteMWLOutputDefault(BaseOperation):
    """
    """

    data_storage = None
    product_params = None
    out_filename = None
    data = Dict()  # data of all main groups
    meta_data = Dict()  # meta_data of individual products

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

    def collect_header_info(self):
        for group in [MWLFileStructure.GENERAL, MWLFileStructure.META_DATA]:
            # create empty container for global attributes and variables
            header_data = Dict({'attrs': Dict(), 'data_vars': Dict()})
            # fill container with header information
            self.data_storage.header.to_ds_dict(header_data, group)

            self.data[group] = header_data

    def collect_meta_data(self):
        # read meta data of all products into meta_data
        for pid, param in self.product_params.product_list.items():
            # todo: remove limit to EXT when other prod types are included
            if param.calc_with_res(LOWRES) and param.product_type in [EXT, RBSC]:
                prod = self.data_storage.product_common_smooth(pid, LOWRES)
            elif param.product_type in [EXT, RBSC]:
                prod = self.data_storage.product_common_smooth(pid, HIGHRES)
            # Todo Ina fix error
            if param.product_type in [EXT, RBSC]:
                prod.to_meta_ds_dict(self.meta_data)

    def write_groups(self):
        for group in MWLFileStructure.MAIN_GROUPS:
            # todo: pass if group is empty
            # convert Dict into Dataset
            ds = xr.Dataset(data_vars=self.data[group].data_vars,
                            coords={},
                            attrs=self.data[group].attrs)
            # write attributes and variables into netCDF file
            # ToDo ina indentation
            ds.to_netcdf(path=self.out_filename,
                                mode=MWLFileStructure.WRITE_MODE[group],
                                group=MWLFileStructure.GROUP_NAME[group],
                                format='NETCDF4')
            ds.close()

        for mwl_id, md in self.meta_data.items():
            ds = xr.Dataset(data_vars=md.data_vars,
                            coords={},
                            attrs=md.attrs)
            ds.to_netcdf(path=self.out_filename,
                                mode='a',
                                group='{}/{}'.format(MWLFileStructure.GROUP_NAME[MWLFileStructure.META_DATA], mwl_id),
                                format='NETCDF4')
            ds.close()

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']
        self.out_filename = os.path.join(PRODUCT_PATH, self.mwl_filename())

        self.collect_header_info()
        self.collect_meta_data()

        for res in RESOLUTIONS:
            # collect all data with this resolution
            group_data = Dict({'attrs': Dict(), 'data_vars': Dict()})

            # all product types that are available for this resolution
            p_types = self.product_params.prod_types(res=res)

            # todo: remove limit to EXT when other prod types are included
            for pt in p_types:
                if pt not in [EXT, RBSC]:
                    p_types.remove(pt)

            # todo cloudmask shall have common altitude, time and timebounds variables
            group_data.data_vars.cloud_mask = self.data_storage.get_common_cloud_mask(res)

            for ptype in p_types:
                p_matrix = self.data_storage.final_product_matrix(ptype, res)
                var_name = MWLFileStructure.NC_VAR_NAMES[ptype]
                group_data.data_vars[var_name] = p_matrix.data
                group_data.data_vars['error_{}'.format(var_name)] = p_matrix.absolute_statistical_uncertainty
                group_data.data_vars['{}_meta_data'.format(var_name)] = p_matrix.meta_data

            self.data[MWLFileStructure.RES_GROUP[res]] = group_data

        self.write_groups()


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