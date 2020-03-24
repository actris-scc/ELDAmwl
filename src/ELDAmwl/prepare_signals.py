# -*- coding: utf-8 -*-
"""Classes for preparation of signals
(combining depol comonents, ttempoaral integration, .."""

from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.registry import registry
from ELDAmwl.signals import Signals


class GetCombinedSignal(BaseOperation):
    """
    Calculates a combined signal from depol components

    params : Dict...
    """

    def __init__(self, sig_trans, sig_refl, HR, eta):
        p = {'HR': HR}
        self._params = p

    def run(self):
        # todo: mache hier die rechnung

        # todo: der aufruf von getcombination kommt nach
        #  Signal.from_depol_components
        total_sig = Signals.from_depol_components(
            self.params.transm_sig,
            self.params.refl_sig,
            self.params.dp_cal_params,
        )
        return total_sig


class CombineDepolComponents(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which
    calculates a total signal from two signals with
    depolarization components. In this case, it will be
    always an instance of GetCombinedSignal().
    """

    name = 'CombineDepolComponents'

    def get_classname_from_db(self):
        """

        return: always 'CombineDepolComponents' .
        """
        return GetCombinedSignal.__class__.__name__


registry.register_class(CombineDepolComponents,
                        GetCombinedSignal.__class__.__name__,
                        GetCombinedSignal)
