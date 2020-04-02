# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.exceptions import NotFoundInStorage, DifferentCloudMaskExists, DifferentHeaderExists
from ELDAmwl.log import logger


class DataStorage(object):
    """ global data storage

    """
    def __init__(self):
        self._data = Dict({'elpp_signals': Dict(),
                           'prepared_signals': Dict(),
                           'basic_products': Dict(),
                           'header': None,
                           'cloud_mask': None,
                           })

    def add_elpp_signal(self, prod_id_str, new_signal):
        """add new ELPP signal to storage"""

        self._data.elpp_signals[prod_id_str][new_signal.channel_id_str] = new_signal


    def elpp_signals(self, prod_id_str):
        """ELPP signals

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
            for ch_id in self._data.elpp_signals[prod_id_str]:
                result.append(self._data.elpp_signals[prod_id_str][ch_id])
            return result
        except AttributeError:
            logger.error('cannot find signals for product {0} '
                         'in data storage'.format(prod_id_str))
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
        return self._data.cloud_mask

    @cloud_mask.setter
    def cloud_mask(self, new_mask):
        if self.cloud_mask:
            if self.cloud_mask != new_mask:
                logger.error('cloud mask already exists '
                             'in data storage and is different ')
                raise DifferentCloudMaskExists

        self._data.cloud_mask = new_mask

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
        return self._data.header

    @header.setter
    def header(self, new_header):
        if self.header:
            if self.header != new_header:
                logger.error('header already exists '
                             'in data storage and is different ')
                raise DifferentHeaderExists
        self._data.header = new_header
