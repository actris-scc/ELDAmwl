# -*- coding: utf-8 -*-
"""plugin for preparation of ELPP for extinction retrieval"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.component.registry import registry
from ELDAmwl.prepare_signals import PrepareExtSignals


class PrepareExtSignalsBetter(BaseOperation):

    _name = 'PrepareExtSignalsBetter'

    def __init__(self, **kwargs):
        super(PrepareExtSignalsBetter, self).__init__(**kwargs)

        self.logger.debug('create PrepareExtSignalsBetter ')

    def run(self, **kwargs):
        self.logger.debug('run PrepareExtSignalsBetter ')


registry.register_class(PrepareExtSignals,
                        PrepareExtSignalsBetter.__name__,
                        PrepareExtSignalsBetter,
                        override=True)
