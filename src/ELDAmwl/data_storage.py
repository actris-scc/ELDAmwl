# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.exceptions import NotFoundInStorage
from ELDAmwl.log import logger


class DataStorage(object):
    """ global data storage

    """
    def __init__(self):
        self._data = Dict({'elpp_signals': Dict(),
                           'prepared_signals': Dict(),
                           'header': None,
                           'cloud_mask': None,
                           })

    def elpp_signals(self, prod_id_str):
        """ELPP signals

        Those are the original signals of one basic product from
        the corresponding ELPP file.

        Args:
            prod_id_str (str):  product id

        Returns:
            :obj:`list` of :obj:`Signals`: list all signals related
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
        return self._data.cloud_mask

    @property
    def header(self):
        return self._data.header
