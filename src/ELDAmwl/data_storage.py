# -*- coding: utf-8 -*-
"""ELDAmwl factories"""
from copy import deepcopy

from addict import Dict

from ELDAmwl.constants import HIGHRES, LOWRES, RESOLUTION_STR, NC_FILL_BYTE
from ELDAmwl.exceptions import DifferentCloudMaskExists
from ELDAmwl.exceptions import DifferentHeaderExists
from ELDAmwl.exceptions import NotFoundInStorage
from ELDAmwl.log import logger
from ELDAmwl.products import Products

import numpy as np
import xarray as xr


class DataStorage(object):
    """ global data storage

    All signals, intermediate products, products etc. are stored
    in the central :obj:`Dict` of this class.
    The access to the stored data (reading and writing) must
    occur exclusively via the implemented properties and methods.
    This restriction allows to implement e.g.
    intelligent memory caching in future (if needed).

    """
    def __init__(self):
        self.data = Dict({'elpp_signals': Dict(),
                          'prepared_signals': Dict(),
                          'basic_products_auto_smooth': Dict(),
                          'binres_common_smooth': Dict({LOWRES: Dict(),
                                                        HIGHRES: Dict()}),
                          'basic_products_common_smooth': Dict({LOWRES: Dict(),
                                                                HIGHRES: Dict()}),
                          'derived_products_common_smooth': Dict({LOWRES: Dict(),
                                                                HIGHRES: Dict()}),
                          'final_product_matrix': Dict({LOWRES: Dict(),
                                                        HIGHRES: Dict()}),
                          'header': None,
                          'cloud_mask': None,
                          })

    def set_prepared_signal(self, prod_id_str, new_signal):
        """write new prepared signal to storage"""

        self.data.prepared_signals[prod_id_str][new_signal.channel_id_str] = new_signal  # noqa E501

    def set_elpp_signal(self, prod_id_str, new_signal):
        """write new ELPP signal to storage"""

        self.data.elpp_signals[prod_id_str][new_signal.channel_id_str] = new_signal  # noqa E501

    def set_basic_product_auto_smooth(self, prod_id_str, new_product):
        """write new auto smoothed basic product to storage
        """
        self.data.basic_products_auto_smooth[prod_id_str] = new_product  # noqa E501

    def set_basic_product_common_smooth(self, prod_id_str, res, new_product):
        """write a basic product that was smoothed with onto a common grid to storage
        """
        self.data.basic_products_common_smooth[res][prod_id_str] = new_product  # noqa E501

    def set_final_product_matrix(self, prod_type, res, new_dataset):
        """write a dataset with common grid (wavelength, time, altitude) to storage

        one dataset per product type and resolution
        """
        self.data.final_product_matrix[res][prod_type] = new_dataset  # noqa E501

    def set_binres_common_smooth(self, prod_id_str, resolution, new_res_array):
        """

        Args:
            prod_id_str:
            resolution:
            new_res_array: xarray.DataArray

        """
        self.data.binres_common_smooth[resolution][prod_id_str] = new_res_array

    def elpp_signals(self, prod_id_str):
        """all ELPP signals of one product

        Those are the original signals of one basic product from
        the corresponding ELPP file.

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`list` of :obj:`Signals`: list of all signals related
                                            to the product id

        Raises:
             NotFoundInStorage: if no signals for the given product id
                are found in storage
        """
        try:
            result = []
            for ch_id in self.data.elpp_signals[prod_id_str]:
                result.append(self.data.elpp_signals[prod_id_str][ch_id])
            return result
        except AttributeError:
            raise NotFoundInStorage('ELPP signals',
                                    'product {0}'.format(prod_id_str))

    def elpp_signal(self, prod_id_str, ch_id_str):
        """one ELPP signal

        Args:
            prod_id_str (str):  product id
            ch_id_str (str):  channel id

        Returns:
            :obj:`Signals`: the requested ELPP signal

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and signal id was found in storage
        """
        try:
            return self.data.elpp_signals[prod_id_str][ch_id_str]
        except AttributeError:
            raise NotFoundInStorage('ELPP signal {0}'.format(ch_id_str),
                                    'product {0}'.format(prod_id_str))

    def prepared_signals(self, prod_id_str):
        """all prepared signals of one product

        Those are the prepared signals of one basic product .

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`list` of :obj:`Signals`: list of all signals related
                                            to the product id

        Raises:
             NotFoundInStorage: if no signals for the given product id
                are found in storage
        """
        try:
            result = []
            for ch_id in self.data.prepared_signals[prod_id_str]:
                result.append(self.data.prepared_signals[prod_id_str][ch_id])
            return result
        except AttributeError:
            raise NotFoundInStorage('prepared signals',
                                    'product {0}'.format(prod_id_str))

    def prepared_signal(self, prod_id_str, ch_id_str):
        """one prepared signal

        The preparation includes normalization by number of laser shots,
        combination of depolarization components(where necessary),
        and correction for molecular transmission (except for KF retrieval).

        Args:
            prod_id_str (str):  product id
            ch_id_str (str):  channel id

        Returns:
            :obj:`Signals`: the requested prepared signal

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and signal id was found in storage
        """
        try:
            return self.data.prepared_signals[prod_id_str][ch_id_str]
        except AttributeError:
            raise NotFoundInStorage('prepared signal {0}'.format(ch_id_str),
                                    'product {0}'.format(prod_id_str))

    def get_prod_res_entry(self, prod_id_str, resolution, source, what_str, where_str):
        try:
            result = self.data[source][resolution][prod_id_str]
        except AttributeError:
            raise NotFoundInStorage('{0} {1}'.format(what_str, prod_id_str),
                                    '{0} {1}'.format(where_str, RESOLUTION_STR[resolution]))

        if isinstance(result, xr.DataArray):
            return result
        elif isinstance(result, Products):
            return result
        else:
            # Dict returns {} instead of AttributeError
            raise NotFoundInStorage('{0} {1}'.format(what_str, prod_id_str),
                                    '{0} {1}'.format(where_str, RESOLUTION_STR[resolution]))

    def basic_product_common_smooth(self, prod_id_str, resolution):
        """a basic product, derived with common smooth

        Args:
            prod_id_str (str):  product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`Products` the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        return self.get_prod_res_entry(prod_id_str, resolution,
                                       'basic_products_common_smooth',
                                       'product',
                                       'basic products with common smoothing with')

    def derived_product_common_smooth(self, prod_id_str, resolution):
        """a basic product, derived with common smooth

        Args:
            prod_id_str (str):  product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`Products` the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        return self.get_prod_res_entry(prod_id_str, resolution,
                                       'derived_products_common_smooth',
                                       'product',
                                       'derived products with common smoothing with')

    def product_common_smooth(self, prod_id_str, resolution):
        """a product, derived with common smooth

        Args:
            prod_id_str (str):  product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns:
            :obj:`Products` the requested product

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


    def binres_common_smooth(self, prod_id_str, resolution):
        """ bin resolution profile of a product

        The bin resolution corresponds to the common vertical resolution
        of all basic and derived products. Some products are smoothed with
        high resolution and low resolution.
        The transformation between bin resolution and effective
        vertical resolution is done with :obj:`GetEffVertRes` and
        :obj:`GetUsedBinRes` corresponding to the retrieval method of the product

        Args:
            prod_id_str (str): product id
            resolution (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns: xarray.DataArray

        Raises:
             NotFoundInStorage: if no entry for the given product id
                and resolution was found in storage
        """
        return self.get_prod_res_entry(prod_id_str, resolution,
                                       'binres_common_smooth',
                                       'common bin resolution profile',
                                       'product {0} in '.format(prod_id_str))

    def final_product_matrix(self, prod_type, res):
        """ 3-dimensional (wavelength, time, altitude) data matrix

        Product matrix contains all product profiles and cloud mask.
        All data are on the same grid of time, altitude and wavelength.
        Except cloud mask, which has no wavelength dimension.
        Missing data are filled with nan.

        Args:
            prod_type :
            res (int): can be LOWRES (=0) or HIGHRES (=1)

        Returns: xarray.Dataset

        """
        return self.data.final_product_matrix[res][prod_type]

    @property
    def cloud_mask(self):
        """two-dimensional (time, level) cloud mask

        The cloud mask of the measurement, read from the ELPP files.

        Returns:
            cloud_mask (xarray.Dataset): cloud mask of the measurement

        Raises:
            DifferentCloudMaskExists: if a cloud_mask
            shall be written to the data storage but
            there is already one from a previously read ELPP file
            which is different from the new one
        """
        return self.data.cloud_mask

    @cloud_mask.setter
    def cloud_mask(self, new_mask):
        if self.cloud_mask is not None:
            if not self.cloud_mask.equals(new_mask):
                raise DifferentCloudMaskExists

        self.data.cloud_mask = new_mask

    def get_max_binres(self, res):
        """
        gets maximum of binres of all products with resolution=res
        Args:
            res:

        Returns:
            xr.DataArray with same shape as single binres arrays
        """
        if self.data.binres_common_smooth[res] == {}:
            return None

        all_binres = xr.concat(list(self.data.binres_common_smooth[res].values()), 'x')
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
        lb = lb.where(lb < num_levels, num_levels -1)

        for t in range(num_times):
            for lev in range(num_levels):
                cm[t,lev] = np.bitwise_or.reduce(self.cloud_mask.values[t, int(fb[lev,t]):int(lb[lev,t])])
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
            shall be written to the data storage but
            there is already one from a previously read ELPP file
            which is different from the new one
        """
        return self.data.header

    @header.setter
    def header(self, new_header):
        if self.header is None:
            self.data.header = new_header
        else:
            self.header.append(new_header)
