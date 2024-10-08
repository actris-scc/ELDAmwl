# -*- coding: utf-8 -*-
"""Classes for handling of mwl products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoProductsGenerated
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.utils.constants import EBSC, VLDR, NEG_DATA, ALL_OK, BSCR, RESOLUTION_STR, PRODUCT_TYPE_NAME, PRODUCT_TYPES
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import LR
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTIONS

import numpy as np
import xarray as xr


class GetProductMatrixDefault(BaseOperation):
    """
    brings all products onto a common grid (wavelength, time, altitude)
    """

    product_params = None  # table with all scheduled products
    shape = None
    wavelengths = None
    p_types = None
    result = None

    def prepare(self):
        self.product_params = self.kwargs['product_params']
        self.wavelengths = Dict()
        self.p_types = Dict()
        self.result = Dict()

        for res in RESOLUTIONS:
            self.wavelengths[res] = self.product_params.wavelengths(res=res)
            self.p_types[res] = self.product_params.prod_types(res=res)
            for ptype in self.p_types[res]:
                self.result[res][ptype] = None
            self.result[res]['cloud_mask'] = None
            self.result[res]['vertical_resolution'] = None

    def get_common_shape(self, res):

        # all products that have been obtained with this resolution
        params = self.product_params.all_products_of_res(res)

        # some of those products have been obtained as intermediate data only.
        # E.g., Raman backscatter profiles for lidar ratio retrievals.
        # If those products shall not be provided with this resolution,
        # do not add them to the matrix -> delete them from params list
        for param in params:
            if not param.calc_with_res(res):
                params.remove(param)

        if params == []:
            return None

        wl_array = np.array(self.product_params.wavelengths(res=res))
        wl_axis = xr.DataArray(wl_array, coords=dict(wavelength=(['wavelength'], wl_array)))
        # wl_axis = xr.DataArray(wl_array, coords={'wavelength':[wl_array]})

        wl_axis.attrs = {'long_name': 'wavelength of the transmitted laser pulse',
                         'units': 'nm',
                         }
        alt_axis = None

        for param in params:
            # todo: remove limit to EXT when all prod types are included
            if (alt_axis is None) and (param.product_type in [EXT, RBSC, EBSC, LR, VLDR]):
                product = self.data_storage.product_qc(param.prod_id_str, res)
                alt_axis = product.altitude
            else:
                # todo: find max of alt axes
                # todo: use concatenate to expand altitude axes
                pass

        return Dict({'shape': (wl_axis.size, alt_axis.shape[0], alt_axis.shape[1]),
                     'alt': alt_axis,
                     'wl': wl_axis,
                     })

    def create_empty_dataset(self, ptype, wavelengths):
        # create a common Dataset for each product type
        # with common shape and empty data variables
        array = np.ones(self.shape.shape) * np.nan
        flag_array = np.ones(self.shape.shape, dtype=int) * ALL_OK

        ds = xr.Dataset(data_vars={
            'altitude': self.shape.alt,
            'wavelength': self.shape.wl,
            'data': (
                ['wavelength', 'time', 'level'],
                deepcopy(array),
                MWLFileStructure.data_attrs(MWLFileStructure, ptype),
            ),
            'absolute_statistical_uncertainty': (
                ['wavelength', 'time', 'level'],
                deepcopy(array),
                MWLFileStructure.stat_err_attrs(MWLFileStructure, ptype),
            ),
            'quality_flag': (
                ['wavelength', 'time', 'level'],
                deepcopy(flag_array),
                MWLFileStructure.qf_attrs(MWLFileStructure, ptype),
            ),
            'meta_data': (
                ['wavelength'],
                np.empty(len(wavelengths), dtype=object),
                {'long_name': 'path to meta data'},
            ),
        })

        if MWLFileStructure.is_product_with_sys_error(MWLFileStructure, ptype):
            ds['absolute_systematic_uncertainty_negative'] = xr.DataArray(
                deepcopy(array),
                dims=['wavelength', 'time', 'level'],
                attrs=MWLFileStructure.sys_err_neg_attrs(MWLFileStructure, ptype),
            )
            ds['absolute_systematic_uncertainty_positive'] = xr.DataArray(
                deepcopy(array),
                dims=['wavelength', 'time', 'level'],
                attrs=MWLFileStructure.sys_err_pos_attrs(MWLFileStructure, ptype),
            )
        return ds

    def combine_ebsc_rbsc_matrix(self, res, wavelengths):
        rbsc_matrix = self.result[res][RBSC]
        ebsc_matrix = self.result[res][EBSC]
        combined = rbsc_matrix.combine_first(ebsc_matrix)
        # preliminray solution: write combined data in matrices of both bsc products
        # => the writing routine will overwrite the first with the second
        # todo: make writing routine intelligent that only 1 bsc matrix is needed
        for bsc_type in [RBSC, EBSC]:
            self.result[res][bsc_type] = combined

    def get_product_matrix(self, ptype, res, wavelengths):
        ds = self.create_empty_dataset(ptype, wavelengths)
        ds.load()

        for wl in wavelengths:
            # get the product param related to products type and wavelength;
            # returns None if the product does not exists
            param = self.product_params.prod_param(ptype, wl)
            if param is not None:
                if param.calc_with_res(res):
                    prod_id = param.prod_id_str
                    # get product object from data storage
                    prod = self.data_storage.product_qc(prod_id, res)
                    # write product data into common Dataset
                    prod.write_data_in_ds(ds)

                    wl_idx = wavelengths.index(wl)
                    ds.meta_data[wl_idx] = '/{}/{}'.format(
                        MWLFileStructure.GROUP_NAME[MWLFileStructure.META_DATA],
                        prod.mwl_meta_id,
                    )

        return ds

    def find_empty_time_sices(self, res):
        empty_time_slices = None

        for ptype in self.p_types[res]:
            a_matrix = self.result[res][ptype]
            if empty_time_slices is None:
                # init result with True
                empty_time_slices = np.ones_like(a_matrix.time, dtype=bool)
                empty_time_slices[:] = True
            # if a time slice in this product is empty AND was empty in other products
            empty_time_slices = empty_time_slices & a_matrix.data.isnull().all(dim=['level', 'wavelength']).values

        return empty_time_slices

    def find_empty_height_bins(self, res):
        empty_height_bins = None

        for ptype in self.p_types[res]:
            a_matrix = self.result[res][ptype]
            if empty_height_bins is None:
                empty_height_bins = np.ones_like(a_matrix.level, dtype=bool)
                empty_height_bins[:] = True

            empty_height_bins = empty_height_bins & a_matrix.data.isnull().all(dim=['time', 'wavelength']).values

        return empty_height_bins

    def find_empty_wavelengths(self, res):
        empty_wavelengths = None

        for ptype in self.p_types[res]:
            a_matrix = self.result[res][ptype]
            if empty_wavelengths is None:
                empty_wavelengths = np.ones_like(a_matrix.wavelength, dtype=bool)
                empty_wavelengths[:] = True

            empty_wavelengths = empty_wavelengths & a_matrix.data.isnull().all(dim=['time', 'level']).values

        return empty_wavelengths

    def find_empty_products(self, res):
        empty_products = []
        for ptype in self.p_types[res]:
            a_matrix = self.result[res][ptype]
            if a_matrix.data.isnull().all():
                empty_products.append(ptype)

        return empty_products

    def qc(self):
        """ identify failed product retrievals"""

        # all possibly failed products
        failed_products = []

        # are there empty product matrices ?
        for res in RESOLUTIONS:
            self.empty_products[res] = self.find_empty_products(res)

            # which individual products contributed to these matrices ?
            for ptype in self.empty_products[res]:
                self.failed_products[res] = self.product_params.all_products_of_type(ptype, res=res)
                failed_products = failed_products + self.failed_products[res]

        # check for all possibly failed products whether there is a valid retrieval with another resolution
        for param in failed_products:
            failed = True
            for res in RESOLUTIONS:
                if self.product_params.product_table and param not in self.failed_products[res]:
                    failed = False
            if failed:
                param.mark_as_failed(self.product_params)


            self.empty_wavelengths[res] = self.find_empty_wavelengths(res)


    def clip_data(self, res):
        """remove product types, wavelengths, time slices and altitude ranges without valid data
        from product matrices"""
        if len(self.p_types[res]) == 0:
            self.logger.warning(f'no products were derived for resolution {RESOLUTION_STR[res]}')
            return None

        empty_time_slices = self.find_empty_time_sices(res)
        empty_height_bins = self.find_empty_height_bins(res)
        empty_products = self.find_empty_products(res)
        empty_wavelengths = self.find_empty_wavelengths(res)

        if empty_time_slices.all():
            self.logger.error(f'no valid products for {RESOLUTION_STR[res]}')
            self.result[res] = None
            return None

        valid_time_slices = np.where(~empty_time_slices)[0]
        valid_height_bins = np.where(~ empty_height_bins)[0]
        valid_wavelengths = np.where(~ empty_wavelengths)[0]

        for ptype in self.p_types[res]:
            if ptype in empty_products:
                self.result[res][ptype] = None
                self.logger.warning(f'no valid data were derived for product type {PRODUCT_TYPE_NAME[ptype]} '
                                    f'with resolution {RESOLUTION_STR[res]}')

            else:
                a_matrix = self.result[res][ptype]
                a_matrix = a_matrix.isel({'level': valid_height_bins,
                                          'time': valid_time_slices,
                                          'wavelength': valid_wavelengths,
                                          })
                self.result[res][ptype] = a_matrix

        # clip cloud mask and vertical resolution
        cm = self.data_storage.get_common_cloud_mask(res)
        self.result[res]['cloud_mask'] = cm.sel({'level': a_matrix.level, 'time': a_matrix.time})

        vert_res = self.data_storage.common_vertical_resolution(res)
        self.result[res]['vertical_resolution'] = vert_res.sel({'level': a_matrix.level, 'time': a_matrix.time})

    def filter_data(self, res):
        """set data points with critical quality flags to nan
        """
        # all product types that are defined for this resolution
        for ptype in self.p_types[res]:
            a_matrix = self.result[res][ptype]
            for qf in self.cfg.CRITICAL_FLAGS:
                a_matrix['data'] = a_matrix.data.where((a_matrix.quality_flag & qf) != qf)

    def store_matrices(self, res):
        if len(self.p_types[res]) > 0:
            for ptype in self.p_types[res]:
                self.data_storage.set_product_matrix(ptype, res, self.result[res][ptype])

            self.data_storage.set_clipped_cloud_mask(res, self.result[res].cloud_mask)
            self.data_storage.set_clipped_vertical_resolution(res, self.result[res].vertical_resolution)

    def run(self):
        self.prepare()

        if len(self.product_params.basic_products()) == 0:
            self.logger.error('no products were derived -> cannot get common matrix')
            raise NoProductsGenerated(self.product_params.measurement_params.mwl_product_id)

        for res in RESOLUTIONS:
            self.shape = self.get_common_shape(res)

            for ptype in self.p_types[res]:
                self.result[res][ptype] = self.get_product_matrix(ptype, res, self.wavelengths[res])

            if (RBSC in self.p_types[res]) and (EBSC in self.p_types[res]):
                self.combine_ebsc_rbsc_matrix(res, self.wavelengths[res])

            self.filter_data(res)
            self.clip_data(res)

            self.store_matrices(res)


class GetProductMatrix(BaseOperationFactory):
    """
    Args:
        data_storage (ELDAmwl.data_storage.DataStorage): global data storage
        product_params: global MeasurementParams
    """

    name = 'GetProductMatrix'

    def __call__(self, **kwargs):
        assert 'product_params' in kwargs

        res = super(GetProductMatrix, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'GetProductMatrixDefault' .
        """
        return GetProductMatrixDefault.__name__


registry.register_class(GetProductMatrix,
                        GetProductMatrixDefault.__name__,
                        GetProductMatrixDefault)
