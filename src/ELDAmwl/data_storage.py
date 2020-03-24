# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.exceptions import NotFoundInStorage
from ELDAmwl.log import logger


class DataStorage(object):
    """ global data storage

    """
    def __init__(self):
        self._data = Dict({'products': Dict()})

    def products(self):
        return self._data.products

    def channel_ids(self, prod_id_str):
        try:
            return self._data.products[prod_id_str].signals
        except AttributeError:
            logger.error('cannot find signals for product {0} '
                         'in data storage'.format(prod_id_str))
            raise NotFoundInStorage

    def signals(self, prod_id_str):
        try:
            result = []
            for ch_id in self.channel_ids(prod_id_str):
                result.append(self._data.products[prod_id_str].signals[ch_id])
            return result
        except AttributeError:
            logger.error('cannot find signals for product {0} '
                         'in data storage'.format(prod_id_str))
            raise NotFoundInStorage

    def cloud_mask(self, prod_id_str):
        try:
            return self._data.products[prod_id_str].cloud_mask
        except AttributeError:
            logger.error('cannot find cloud mask for product {0} '
                         'in data storage'.format(prod_id_str))
            raise NotFoundInStorage
