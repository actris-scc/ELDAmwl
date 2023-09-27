# -*- coding: utf-8 -*-
"""Classes for handling of mwl products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoProductsGenerated
from ELDAmwl.output.mwl_file_structure import MWLFileStructure
from ELDAmwl.utils.constants import EBSC, VLDR, NEG_DATA
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

    # data_storage = None
    product_params = None
    shape = None

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
            # todo: remove limit to EXT when other prod types are included
            if (alt_axis is None) and (param.product_type in [EXT, RBSC, EBSC, LR, VLDR]):
                product = self.data_storage.product_common_smooth(param.prod_id_str, res)
                alt_axis = product.altitude
            else:
                # todo: find max of alt axes
                # todo: use concatenate to expand altitude axes
                pass

        return Dict({'shape': (wl_axis.size, alt_axis.shape[0], alt_axis.shape[1]),
                     'alt': alt_axis,
                     'wl': wl_axis,
                     })

    def run(self):
        self.product_params = self.kwargs['product_params']
        if len(self.product_params.basic_products()) == 0:
            self.logger.error('no products were derived -> cannot get common matrix')
            raise NoProductsGenerated(self.product_params.measurement_params.mwl_product_id)

        for res in RESOLUTIONS:
            wavelengths = self.product_params.wavelengths(res=res)
            p_types = self.product_params.prod_types(res=res)

            self.shape = self.get_common_shape(res)

            for ptype in p_types:
                # create a common Dataset for each product type
                # with common shape and empty data variables
                array = np.ones(self.shape.shape) * np.nan

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

                ds.load()

                for wl in wavelengths:
                    # get the product param related to products type and wavelength;
                    # returns None if the product does not exists
                    param = self.product_params.prod_param(ptype, wl)
                    if param is not None:
                        if param.calc_with_res(res):
                            prod_id = param.prod_id_str
                            # get product object from data storage
                            prod = self.data_storage.product_common_smooth(prod_id, res)
                            # write product data into common Dataset
                            prod.write_data_in_ds(ds)

                            wl_idx = wavelengths.index(wl)
                            ds.meta_data[wl_idx] = '/{}/{}'.format(
                                MWLFileStructure.GROUP_NAME[MWLFileStructure.META_DATA],
                                prod.mwl_meta_id,
                            )

                self.data_storage.set_product_matrix(ptype, res, ds)

            if (RBSC in p_types) and (EBSC in p_types):
                bsc_unique = True
                for wl in wavelengths:
                    if (self.product_params.prod_param(EBSC, wl) is not None) and \
                        (self.product_params.prod_param(RBSC, wl) is not None):
                        bsc_unique = False
                        self.logger.warning(f'Raman bsc product {self.product_params.prod_param(RBSC, wl).prod_id_str} '
                                            f'and elast bsc product {self.product_params.prod_param(EBSC, wl).prod_id_str} '
                                            f'at the same wavelength {wl}')
                    # todo: check input and make sure that not more than
                    #       1 bsc product is assigned per wavelength (Raman + elsat)
                if bsc_unique:
                    rbsc_matrix = self.data_storage.final_product_matrix(RBSC, res)
                    ebsc_matrix = self.data_storage.final_product_matrix(EBSC, res)
                    combined = rbsc_matrix.combine_first(ebsc_matrix)
                    # preliminray solution: write combined data in matrices of both bsc products
                    # => the writing routine will overwrite the first with the second
                    # todo: make writing routine intelligent that only 1 bsc matrix is needed
                    for bsc_type in [RBSC, EBSC]:
                        self.data_storage.set_final_product_matrix(bsc_type, res, combined)


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


class QualityControlDefault(BaseOperation):
    """
    synergetic quality control of all products
    """

    product_params = None
    qc_product_matrix = None

    def prepare(self):
        """
        makes a local copy (self.qc_product_matrix) of the matrices of all resolutions and product types in data storage
        this copy will then be modified by the class methods
        Returns: None

        """
        self.product_params = self.kwargs['product_params']

        self.qc_product_matrix = Dict()
        for res in RESOLUTIONS:
            p_types = self.product_params.prod_types(res=res)
            for prod_type in p_types:
                self.qc_product_matrix[res, prod_type] = self.data_storage.product_matrix(prod_type, res)

    def screen_negative_values(self, a_matrix):
        """

        """
        # maximum possible value = value + 2 * uncertainty
        max_values = a_matrix.data + 2 * a_matrix.error
        bad_idxs = np.where(max_values < 0)
        a_matrix.data[bad_idxs] = np.nan
        a_matrix.qflag[bad_idxs] = a_matrix.qflag[bad_idxs] | NEG_DATA

    def run_single_product_tests(self):
        for res in RESOLUTIONS:
            p_types = self.product_params.prod_types(res=res)
            for prod_type in p_types:
                a_matrix = self.qc_product_matrix[res][prod_type]

                self.screen_negative_values(a_matrix)

    def run(self):
        self.prepare()

        self.run_single_product_tests()

        # todo: implement quality control
        # todo: add quality flag for complete profile (e.g. this profile causes bad angströms,
        #                                               aod / integral of this profile too large, )
        #                                               additionally to flag profile
        # todo: 1) screen for negative values
        # todo: 1a) if bsc profile has negative area in the middle -> skip complete profile
        # todo: 2) screen for too large error
        # todo: 3) screen derived products for layers with no aerosol (bsc ratio < threshold)
        # todo: 4) if there are more than 1 bsc at the same wavelegnth
        #           -> decide which one to use (use the one with best test results on angstroem and lidar ratio)
        # todo: 5) test data in aerosol layers for thresholds in lidar ratio and angström exp
        # todo: 5a) based on lidar ratio and angström profiles: select if one profile is bad
        #           (remove the profile in a way that NUMBER of remaining good profiles is max
        # todo: 6) profiles which has more than 10% bad points in 5) -> skip completely
        # todo: do not allow empty matrix (1 variable with no data at all
        # todo: 2 file versions: one with quality controlled and screened data (for user),
        #                       one with full profiles and qc flag (only for CARS internal use)
        #         maybe the full output is written only if a certain command line parameter is set
        # todo: write quality flags in regular output files (in expert user section)



class QualityControl(BaseOperationFactory):
    """
    Args:
        product_params: global MeasurementParams
    """

    name = 'QualityControl'

    def __call__(self, **kwargs):
        assert 'product_params' in kwargs

        res = super(QualityControl, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'GetProductMatrixDefault' .
        """
        return QualityControlDefault.__name__


registry.register_class(GetProductMatrix,
                        GetProductMatrixDefault.__name__,
                        GetProductMatrixDefault)

registry.register_class(QualityControl,
                        QualityControlDefault.__name__,
                        QualityControlDefault)
