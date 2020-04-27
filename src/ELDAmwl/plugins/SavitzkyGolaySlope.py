# -*- coding: utf-8 -*-
"""plugin for calculation of slope with Savitzky-Golay method"""

from ELDAmwl.extinction_factories import SignalSlope
from ELDAmwl.factory import BaseOperation
from ELDAmwl.log import logger
from ELDAmwl.registry import registry


class SavGolaySlope(BaseOperation):

    name = 'SavGolaySlope'

    def __init__(self, **kwargs):
        logger.debug('create SavGolaySlope ')

    def run(self, **kwargs):
        logger.debug('run SavGolaySlope ')


registry.register_class(SignalSlope,
                        SavGolaySlope.__name__,
                        SavGolaySlope)
