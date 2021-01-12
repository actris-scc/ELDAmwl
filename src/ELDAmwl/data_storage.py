# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict

from ELDAmwl.constants import HIGHRES, LOWRES, RESOLUTION_STR
from ELDAmwl.exceptions import DifferentCloudMaskExists
from ELDAmwl.exceptions import DifferentHeaderExists
from ELDAmwl.exceptions import NotFoundInStorage
from ELDAmwl.log import logger


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

    def basic_product_common_smooth(self, prod_id_str, resolution):
        """a product, derived with coomon smooth

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`Products` the requested product

        Raises:
             NotFoundInStorage: if no product for the given product id
                is found in storage
        """

        try:
            return self.data.basic_products_common_smooth[resolution][prod_id_str]
        except AttributeError:
            raise NotFoundInStorage('product {0}'.format(prod_id_str),
                                    'basic products with common smoothing with {0}'.format(RESOLUTION_STR[resolution]))

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
        try:
            return self.data.binres_common_smooth[resolution][prod_id_str]
        except AttributeError:
            raise NotFoundInStorage('common bin resolution profile',
                                    'product {0} in {1}'.format(prod_id_str, RESOLUTION_STR[resolution]))


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
        if self.header is not None:
            if not (self.header == new_header):
                raise DifferentHeaderExists
        self.data.header = new_header
