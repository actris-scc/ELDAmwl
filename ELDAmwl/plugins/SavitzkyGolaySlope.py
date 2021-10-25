# -*- coding: utf-8 -*-
"""plugin for calculation of slope with Savitzky-Golay method"""

from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.component.registry import registry
from ELDAmwl.operations.extinction.ext_calc_tools import SignalSlope


class SavGolaySlope(BaseOperation):

    name = 'SavGolaySlope'

    def __init__(self, **kwargs):
        super(SavGolaySlope, self).__init__(**kwargs)
        self.logger.debug('create SavGolaySlope ')

    def run(self, **kwargs):
        self.logger.debug('run SavGolaySlope ')


registry.register_class(SignalSlope,
                        SavGolaySlope.__name__,
                        SavGolaySlope)
