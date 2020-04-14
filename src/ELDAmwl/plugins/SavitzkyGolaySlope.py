# -*- coding: utf-8 -*-
"""plugin for calculation of slope with Savitzky-Golay method"""

from ELDAmwl.extinction_factories import SignalSlope
from ELDAmwl.registry import registry


class SavGolaySlope(object):

    name = 'SavGolaySlope'

    def __init__(self, **kwargs):
        print('create SavGolaySlope ')

    def run(self, **kwargs):
        print('run SavGolaySlope ')


registry.register_class(SignalSlope,
                        SavGolaySlope.__name__,
                        SavGolaySlope)
