# -*- coding: utf-8 -*-
"""ELDAmwl factories"""
from copy import deepcopy

from addict import Dict

from ELDAmwl.utils.constants import HIGHRES, LOWRES, RESOLUTION_STR, NC_FILL_BYTE
from ELDAmwl.errors.exceptions import DifferentCloudMaskExists
from ELDAmwl.errors.exceptions import NotFoundInStorage
from ELDAmwl.products import Products

import numpy as np
import xarray as xr


class DataStorage(object):
    """ global __data storage

    All signals, intermediate products, products etc. are stored
    in the central :obj:`Dict` of this class.
    The access to the stored __data (reading and writing) must
    occur exclusively via the implemented properties and methods.
    This restriction allows to implement e.g.
    intelligent memory caching in future (if needed).

    """

    name = 'Datastorage'

    def __init__(self):
        self.__data = Dict({'elpp_signals': Dict(),
                          'prepared_signals': Dict(),

                          'basic_products_raw': Dict(),
                          'basic_products_auto_smooth': Dict(),
                          'binres_auto_smooth': Dict(),

                          'binres_common_smooth': Dict(
                              {
                                LOWRES: Dict(),
                                HIGHRES: Dict()
                                }
                          ),
                            'basic_products_common_smooth': Dict(
                              {
                                LOWRES: Dict(),
                                HIGHRES: Dict()
                              }
                          ),
                            'derived_products_common_smooth': Dict(
                              {
                                LOWRES: Dict(),
                                HIGHRES: Dict()
                              }
                          ),
                            'final_product_matrix': Dict(
                              {
                                LOWRES: Dict(),
                                HIGHRES: Dict()
                              }
                          ),

                            'header': None,
                            'cloud_mask': None,
                            })

    def set_elpp_signal(self, prod_id_str, new_signal):
        """write new ELPP signal to storage"""

        self.__data.elpp_signals[prod_id_str][new_signal.channel_id_str] = new_signal  # noqa E501

    def set_prepared_signal(self, prod_id_str, new_signal):
        """write new prepared signal to storage"""

        self.__data.prepared_signals[prod_id_str][new_signal.channel_id_str] = new_signal  # noqa E501

    def set_basic_product_raw(self, prod_id_str, new_product):
        """write new un-smoothed basic product to storage
        """
        self.__data.basic_products_raw[prod_id_str] = new_product  # noqa E501

    def set_basic_product_auto_smooth(self, prod_id_str, new_product):
        """write new auto smoothed basic product to storage
        """
        self.__data.basic_products_auto_smooth[prod_id_str] = new_product  # noqa E501

    def set_binres_auto_smooth(self, prod_id_str, new_res_array):
        """write new auto smoothed basic product to storage

        Args:
            prod_id_str:
            new_res_array: xarray.DataArray

        """
        self.__data.binres_auto_smooth[prod_id_str] = new_res_array  # noqa E501

    def set_basic_product_common_smooth(self, prod_id_str, res, new_product):
        """write a basic product that was smoothed with onto a common grid to storage
        """
        self.__data.basic_products_common_smooth[res][prod_id_str] = new_product  # noqa E501

    def set_final_product_matrix(self, prod_type, res, new_dataset):
        """write a dataset with common grid (wavelength, time, altitude) to storage

        one dataset per product type and resolution
        """
        self.__data.final_product_matrix[res][prod_type] = new_dataset  # noqa E501

    def set_binres_common_smooth(self, prod_id_str, resolution, new_res_array):
        """

        Args:
            prod_id_str:
            resolution:
            new_res_array: xarray.DataArray

        """
        self.__data.binres_common_smooth[resolution][prod_id_str] = new_res_array

    def elpp_signals(self, prod_id_str):
        """copies of all ELPP signals of one product

        Those are the original signals of one basic product from
        the corresponding ELPP file.

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`list` of :obj:`Signals`: list with deepcopies of all signals related
                                            to the product id

        Raises:
             NotFoundInStorage: if no signals for the given product id
                are found in storage
        """
        try:
            result = []
            for ch_id in self.__data.elpp_signals[prod_id_str]:
                result.append(deepcopy(self.__data.elpp_signals[prod_id_str][ch_id]))
            return result
        except AttributeError:
            raise NotFoundInStorage('ELPP signals',
                                    'product {0}'.format(prod_id_str))

    def elpp_signal(self, prod_id_str, ch_id_str):
        """copy of an ELPP signal

        Args:
            prod_id_str (str):  product id
            ch_id_str (str):  channel id

        Returns:
            :obj:`Signals`: deepcopy of the requested ELPP signal

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and signal id was found in storage
        """
        try:
            return deepcopy(self.__data.elpp_signals[prod_id_str][ch_id_str])
        except AttributeError:
            raise NotFoundInStorage('ELPP signal {0}'.format(ch_id_str),
                                    'product {0}'.format(prod_id_str))

    def prepared_signals(self, prod_id_str):
        """copies of all prepared signals of one product

        Those are the prepared signals of one basic product .

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`list` of :obj:`Signals`: list with deepcopies of all signals related
                                            to the product id

        Raises:
             NotFoundInStorage: if no signals for the given product id
                are found in storage
        """
        try:
            result = []
            for ch_id in self.__data.prepared_signals[prod_id_str]:
                result.append(deepcopy(self.__data.prepared_signals[prod_id_str][ch_id]))
            return result
        except AttributeError:
            raise NotFoundInStorage('prepared signals',
                                    'product {0}'.format(prod_id_str))

    def prepared_signal(self, prod_id_str, ch_id_str):
        """copy of an prepared signal

        The preparation includes normalization by number of laser shots,
        combination of depolarization component(where necessary),
        and correction for molecular transmission (except for KF retrieval).

        Args:
            prod_id_str (str):  product id
            ch_id_str (str):  channel id

        Returns:
            :obj:`Signals`: deepcopy of the requested prepared signal

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and signal id was found in storage
        """
        try:
            return deepcopy(self.__data.prepared_signals[prod_id_str][ch_id_str])
        except AttributeError:
            raise NotFoundInStorage('prepared signal {0}'.format(ch_id_str),
                                    'product {0}'.format(prod_id_str))

    def _get_prod_res_entry(self, prod_id_str, resolution, source, what_str, where_str):
        """copy of a result with a certain resolution

        Args:
            prod_id_str (str):  product id
            resolution (int): can be None or LOWRES (=0) or HIGHRES (=1)
            source (str): part of the DataStorage where to look
            what_str (str): description of searched object (used for log output)
            where_str (str): description of the source (used for log output)

        Returns:
            :obj:`xarray.DataArray` or :obj:'Products': deepcopy of the requested result

        Raises:
             NotFoundInStorage: if no entry for the given parameter was found in storage
        """
        try:
            if resolution is not None:
                result = self.__data[source][resolution][prod_id_str]
            else:
                result = self.__data[source][prod_id_str]
        except AttributeError:
            raise NotFoundInStorage('{0} {1}'.format(what_str, prod_id_str),
                                    '{0} {1}'.format(where_str, RESOLUTION_STR[resolution]))

        if isinstance(result, xr.DataArray):
            return deepcopy(result)
        elif isinstance(result, Products):
            return deepcopy(result)
        else:
            # Dict returns {} instead of AttributeError
            if resolution is not None:
                raise NotFoundInStorage('{0} {1}'.format(what_str, prod_id_str),
                                        '{0} {1}'.format(where_str, RESOLUTION_STR[resolution]))
            else:
                raise NotFoundInStorage('{0} {1}'.format(what_str, prod_id_str),
                                        '{0}'.format(where_str))

    def basic_product_raw(self, prod_id_str):
        """copy of a basic product, derived without smoothing

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`Products` deepcopy of the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        return self._get_prod_res_entry(prod_id_str, None,
                                       'basic_products_raw',
                                       'product',
                                       'basic products without smoothing')

    def basic_product_auto_smooth(self, prod_id_str):
        """copy of a basic product, derived with automatic smooth

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`Products` deepcopy of the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        return self._get_prod_res_entry(prod_id_str, None,
                                       'basic_products_auto_smooth',
                                       'product',
                                       'basic products with automatic smoothing')

    def binres_auto_smooth(self, prod_id_str):
        """ copy of the bin resolution profile of a product

        The bin resolution corresponds to the automatically derived vertical resolution
        of a basic product.
        The transformation between bin resolution and effective
        vertical resolution is done with :obj:`GetEffVertRes` and
        :obj:`GetUsedBinRes` corresponding to the retrieval method of the product

        Args:
            prod_id_str (str): product id

        Returns:
            :obj:`xarray.DataArray`: copy of the bin resolution profile

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and resolution was found in storage
        """
        return self._get_prod_res_entry(prod_id_str, None,
                                       'binres_auto_smooth',
                                       'automatically derived bin resolution profile',
                                       'product {0}'.format(prod_id_str))

    def binres_common_smooth(self, prod_id_str, resolution):
        """ copy of a bin resolution profile of a product

        The bin resolution corresponds to the common vertical resolution
        of all basic and derived products. Some products are smoothed with
        high resolution and low resolution.
        The transformation between bin resolution and effective
        vertical resolution is done with :obj:`GetEffVertRes` and
        :obj:`GetUsedBinRes` corresponding to the retrieval method of the product

        Args:
            prod_id_str (str): product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`xarray.DataArray`: deepcopy of the requested resolution profile

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and resolution was found in storage
        """
        return self._get_prod_res_entry(prod_id_str, resolution,
                                       'binres_common_smooth',
                                       'common bin resolution profile',
                                       'product {0} in '.format(prod_id_str))

    def basic_product_common_smooth(self, prod_id_str, resolution):
        """copy of a basic product, derived with common smooth

        Args:
            prod_id_str (str):  product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`Products` deepcopy of the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        return self._get_prod_res_entry(prod_id_str, resolution,
                                       'basic_products_common_smooth',
                                       'product',
                                       'basic products with common smoothing with')

    def derived_product_common_smooth(self, prod_id_str, resolution):
        """copy of a basic product, derived with common smooth

        Args:
            prod_id_str (str):  product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`Products`: deepcopy of the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        return self._get_prod_res_entry(prod_id_str, resolution,
                                       'derived_products_common_smooth',
                                       'product',
                                       'derived products with common smoothing with')

    def product_common_smooth(self, prod_id_str, resolution):
        """copy of a product, derived with common smooth

        Args:
            prod_id_str (str):  product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`Products`: deepcopy of the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """
        try:
            result = self.basic_product_common_smooth(prod_id_str, resolution)
        except NotFoundInStorage:
            try:
                result = self.derived_product_common_smooth(prod_id_str, resolution)
            except NotFoundInStorage:
                raise NotFoundInStorage('product {0}'.format(prod_id_str),
                                        'products with common smoothing with {0}'.format(RESOLUTION_STR[resolution]))

        return result

    def final_product_matrix(self, prod_type, res):
        """ 3-dimensional (wavelength, time, altitude) data matrix

        Product matrix contains all product profiles and cloud mask.
        All data are on the same grid of time, altitude and wavelength.
        Except cloud mask, which has no wavelength dimension.
        Missing data are filled with nan.

        Args:
            prod_type :
            res (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:'xarray.Dataset': deepcopy of the final product matrix

        """
        return deepcopy(self.__data.final_product_matrix[res][prod_type])

    @property
    def cloud_mask(self):
        """two-dimensional (time, level) cloud mask

        The cloud mask of the measurement, read from the ELPP files.

        Returns:
            cloud_mask (xarray.Dataset): cloud mask of the measurement

        Raises:
            DifferentCloudMaskExists: if a cloud_mask
            shall be written to the __data storage but
            there is already one from a previously read ELPP file
            which is different from the new one
        """
        return self.__data.cloud_mask

    @cloud_mask.setter
    def cloud_mask(self, new_mask):
        if self.cloud_mask is not None:
            if not self.cloud_mask.equals(new_mask):
                raise DifferentCloudMaskExists

        self.__data.cloud_mask = new_mask

    def get_max_binres(self, res):
        """
        gets maximum of binres of all products with resolution=res
        Args:
            res:

        Returns:
            xr.DataArray with same shape as single binres arrays
        """
        if self.__data.binres_common_smooth[res] == {}:
            return None

        all_binres = xr.concat(list(self.__data.binres_common_smooth[res].values()), 'x')
        maxres = all_binres.max('x')

        return maxres

    def get_common_cloud_mask(self, res):
        maxres = self.get_max_binres(res)
        if maxres is None:
            return None

        cm = deepcopy(self.cloud_mask)
        cm[:] = NC_FILL_BYTE

        num_times = cm.shape[0]
        num_levels = cm.shape[1]

        fb = maxres.level - maxres // 2
        lb = maxres.level + maxres // 2
        fb = fb.where(fb >= 0, 0)
        lb = lb.where(lb < num_levels, num_levels - 1)

        for t in range(num_times):
            for lev in range(num_levels):
                cm[t, lev] = np.bitwise_or.reduce(self.cloud_mask.values[t, int(fb[lev, t]):int(lb[lev, t])])
        # self.cloud_mask[0, 50] =2
        # self.cloud_mask[:, 100] = 1
        # np.bitwise_or.reduce(self.cloud_mask.values[:,40:110], axis=1)
        # self.cloud_mask[:, 40:110].reduce(np.bitwise_or.reduce, axis=1)
        return cm

    @property
    def header(self):
        """header of the measurement, read from ELPP files.

        Returns:
            header (:obj:`Header`): header of the measurement

        Raises: DifferentHeaderExists: if a header
            shall be written to the __data storage but
            there is already one from a previously read ELPP file
            which is different from the new one
        """
        return self.__data.header

    @header.setter
    def header(self, new_header):
        if self.header is None:
            self.__data.header = new_header
        else:
            self.header.append(new_header)
