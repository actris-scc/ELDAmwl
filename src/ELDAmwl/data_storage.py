# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict
from ELDAmwl.exceptions import NotFoundInStorage
from ELDAmwl.log import logger


class DataStorage(object):

    def __init__(self):
        self._data = Dict({'products': Dict()})

    def products(self):
        return self._data.products

    def signals(self, prod_id):
        try:
            return self._data.products[prod_id].signals
        except AttributeError:
            logger.error('cannot find signals for product {0} '
                         'in data storage'.format(prod_id))
            raise NotFoundInStorage

    def cloud_flag(self, prod_id):
        try:
            return self._data.products[prod_id].cloud_mask
        except AttributeError:
            logger.error('cannot find cloud mask for product {0} '
                         'in data storage'.format(prod_id))
            raise NotFoundInStorage
