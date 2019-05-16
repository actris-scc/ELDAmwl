# -*- coding: utf-8 -*-
from math import pi
from attrdict import AttrDict


LIGHT_SPEED = 3.E8  # m / s
RAYL_LR = 8. * pi / 3

PRODUCT_TYPES = AttrDict({'Rbsc': 0,
                          'ext': 1,
                          'lr': 2,
                          'Ebsc': 3,
                          'mwl': 10,
                          'ae': 11,
                          'cr': 12,
                          'vldr': 13,
                          'pldr': 14,
                          })

ALGO1 = 'algo1'
ALGO2 = 'algo2'

ALGOS = [ALGO1, ALGO2]

