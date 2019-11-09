# -*- coding: utf-8 -*-
"""plugin for calculation of slope with Savitzky-Golay method"""

from ELDAmwl.extinction_factories import SignalSlope
from ELDAmwl.registry import registry


class SavGolaySlope(object):

    def __init__(self, str):
        pass
        # print('SavGolaySlope ', str)


registry.register_class(SignalSlope, 'SavitzkyGolay', SavGolaySlope)
