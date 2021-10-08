# -*- coding: utf-8 -*-
"""plugin for preparation of ELPP for extinction retrieval"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.log import logger
from ELDAmwl.prepare_signals import PrepareExtSignals
from ELDAmwl.component.registry import registry


class PrepareExtSignalsBetter(BaseOperation):

    name = 'PrepareExtSignalsBetter'

    def __init__(self, **kwargs):
        super(PrepareExtSignalsBetter, self).__init__(**kwargs)

        logger.debug('create PrepareExtSignalsBetter ')

    def run(self, **kwargs):
        logger.debug('run PrepareExtSignalsBetter ')


registry.register_class(PrepareExtSignals,
                        PrepareExtSignalsBetter.__name__,
                        PrepareExtSignalsBetter,
                        override=True)
