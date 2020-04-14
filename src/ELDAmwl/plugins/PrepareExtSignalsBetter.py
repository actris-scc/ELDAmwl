# -*- coding: utf-8 -*-
"""plugin for preparation of ELPP for extinction retrieval"""

from ELDAmwl.prepare_signals import PrepareExtSignals
from ELDAmwl.registry import registry

class PrepareExtSignalsBetter(object):

    name = 'PrepareExtSignalsBetter'

    def __init__(self, **kwargs):
        print('create PrepareExtSignalsBetter ')

    def run(self, **kwargs):
        print('run PrepareExtSignalsBetter ')


registry.register_class(PrepareExtSignals,
                        PrepareExtSignalsBetter.__name__,
                        PrepareExtSignalsBetter,
                        override=True)
