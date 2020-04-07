# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.exceptions import DifferentCloudMaskExists
from ELDAmwl.exceptions import DifferentHeaderExists
from ELDAmwl.exceptions import NotFoundInStorage
from ELDAmwl.log import logger


class DataStorage(object):
    """ global data storage

    All signals, intermediate products, products etc. are stored in the central :obj:`Dict`
    of this class. The access to the stored data (reading and writing) must occur exclusively
    via the implemented properties and methods. This restriction allows to implement e.g.
    intelligent memory caching in future (if needed).

    """
    def __init__(self):
        self.data = Dict({'elpp_signals': Dict(),
                          'prepared_signals': Dict(),
                          'basic_products_auto_smooth': Dict(),
                          'basic_products_common_smooth': Dict(),
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
        self.data.elpp_signals[prod_id_str] = new_product  # noqa E501

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
            logger.error('cannot find signals for product {0} '
                         'in data storage'.format(prod_id_str))
            raise NotFoundInStorage

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
            logger.error('cannot find signal {0} for product {1} '
                         'in data storage'.format(ch_id_str, prod_id_str))
            raise NotFoundInStorage

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
            logger.error('cannot find signal {0} for product {1} '
                         'in data storage'.format(ch_id_str, prod_id_str))
            raise NotFoundInStorage

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
                logger.error('cloud mask already exists '
                             'in data storage and is different ')
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
                logger.error('header already exists '
                             'in data storage and is different ')
                raise DifferentHeaderExists
        self.data.header = new_header
