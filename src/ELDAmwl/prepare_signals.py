# -*- coding: utf-8 -*-
"""Classes for preparation of signals (combining depol comonents, ttempoaral integration, .."""

from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.registry import registry
from ELDAmwl.signals import Signals


class GetCombinedSignal(BaseOperation):
    """
    Calculates a combined signal from depol components

    params : Dict...
    """

    def __init__(self, params):
        self._params = params

    def run(self):
        total_sig = Signals.from_depol_components(
            self.params.transm_sig,
            self.params.refl_sig,
            self.params.dp_cal_params,
        )


class CombineDepolComponents(BaseOperationFactory):
    """
    Calculates particle extinction coefficient from signal slope.
    """

    name = 'CombineDepolComponents'

    def get_classname_from_db(self):
        """

        return: always 'CombineDepolComponents' .
        """
        return GetCombinedSignal.__class__.__name__


registry.register_class(CombineDepolComponents, GetCombinedSignal)


