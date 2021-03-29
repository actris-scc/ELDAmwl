# -*- coding: utf-8 -*-
"""Classes for handling of mwl products"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.constants import EXT, RBSC, EBSC
from ELDAmwl.constants import RESOLUTIONS
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
#from ELDAmwl.log import logger
from ELDAmwl.registry import registry

import numpy as np
import xarray as xr


class GetProductMatrixDefault(BaseOperation):
    """
    brings all products onto a common grid (wavelength, time, altitude)
    """

    data_storage = None
    product_params = None

    def get_common_shape(self, res):

        wl_array = np.array(self.product_params.wavelengths(res=res))
        wl_axis = xr.DataArray(wl_array, dims=['wavelength'], coords=[wl_array])
        wl_axis.attrs = {'long_name': 'wavelength of the transmitted laser pulse',
                         'units': 'nm',
                         }
        alt_axis = None

        for param in self.product_params.all_products(res):
            if (alt_axis is None) and (param.product_type==EXT):  # todo: remove limit to EXT when other prod types are included
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
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']


        for res in RESOLUTIONS:
            wavelengths = self.product_params.wavelengths(res=res)
            p_types = self.product_params.prod_types(res=res)
            self.shape = self.get_common_shape(res)

            # todo: remove limit to EXT when other prod types are included
            for prod_type in [EXT]:#d_types:
                # create a common Dataset for each product type
                # with common shape and empty data variables
                array = np.ones(self.shape.shape) * np.nan
                ds = xr.Dataset(data_vars={'altitude': self.shape.alt,
                                          'wavelength': self.shape.wl,
                                          'values':
                                              (['wavelength', 'time', 'level'], deepcopy(array)),
                                          'absolute_statistical_uncertainty':
                                              (['wavelength', 'time', 'level'], deepcopy(array)),
                                          })

                for wl in wavelengths:
                    # get the product id related to products type and wavelength;
                    # returns None if the product does not exists
                    prod_id = self.product_params.prod_id(prod_type, wl)
                    # if product exists
                    if prod_id is not None:
                        # get product object from data storage
                        prod = self.data_storage.product_common_smooth(prod_id, res)
                        # write product data into common Dataset
                        prod.write_in_ds(ds)

                self.data_storage.set_final_product(prod_type, res, ds)

            if (RBSC in p_types) and (EBSC in p_types):
                # todo: check input and make sure that not more than
                #       1 bsc product is assigned per wavelength (Raman + elsat)
                # todo: combine datasets of RBsc and EBsc using combine_first()
                pass


class GetProductMatrix(BaseOperationFactory):
    """
    Args:
        data_storage (ELDAmwl.data_storage.DataStorage): global data storage
        product_params: global MeasurementParams
    """

    name = 'GetProductMatrix'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
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

    data_storage = None
    product_params = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']

        # todo: implement quality control


class QualityControl(BaseOperationFactory):
    """
    Args:
        data_storage (ELDAmwl.data_storage.DataStorage): global data storage
        product_params: global MeasurementParams
    """

    name = 'QualityControl'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
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
