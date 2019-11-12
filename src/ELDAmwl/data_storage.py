# -*- coding: utf-8 -*-
"""ELDAmwl factories"""

from addict import Dict

class DataStorage(object):

    def __init__(self):
        self._data = Dict({'products': Dict()})

    def products(self):
        return self._data.products
