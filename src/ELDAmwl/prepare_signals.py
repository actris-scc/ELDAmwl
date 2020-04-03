# -*- coding: utf-8 -*-
"""Classes for preparation of signals
(combining depol comonents, ttempoaral integration, .."""
from copy import deepcopy

from ELDAmwl.constants import EBSC, KF
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.log import logger
from ELDAmwl.registry import registry
from ELDAmwl.signals import Signals


class DoPrepareSignals(BaseOperation):
    """
    """

    data_storage = None

    def combine_depol_components(self, p_param):
        if p_param.is_bsc_from_depol_components():
            pid = p_param.prod_id_str
            transm_sig = self.data_storage.elpp_signal(pid, p_param.transm_sig_id)
            refl_sig = self.data_storage.elpp_signal(pid, p_param.refl_sig_id)
            total_sig = Signals.from_depol_components(transm_sig, refl_sig)
            self.data_storage.set_prepared_signal(p_param.prod_id_str, total_sig)
            total_sig.register(p_param)

    def normalize_by_shots(self, p_param):
        pid = p_param.prod_id_str
        for sig in self.data_storage.elpp_signals(pid):
           new_sig = deepcopy(sig)
           new_sig.normalize_by_shots()
           self.data_storage.set_prepared_signal(pid, new_sig)


    def correct_molecular_transmission(self, p_param):
#        if (p_param.product_type == EBSC ) and \
#            (p_param.elast_bsc_method == KF):
#            pass
        pid = p_param.prod_id_str
        for sig in self.data.signals(p_param.prod_id_str):
           new_sig = deepcopy(sig)
           new_sig.correct_for_mol_transmission()
           self.data_storage.set_prepared_signal(pid, new_sig)

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        products = self.kwargs['products']

        for p_param in products:
            self.normalize_by_shots(p_param)
            self.combine_depol_components(p_param)
#            self.correct_molecular_transmission(p_param)


class PrepareSignals(BaseOperationFactory):
    """
    Args:
        data_storage: global data storage (:class:`DataStorage`)
        products: list of parameters of all basic
                products (list of :class:
                `ELDAmwl.products.ProductParams`)
    """

    name = 'PrepareSignals'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'products' in kwargs
        res = super(PrepareSignals, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareSignals' .
        """
        return DoPrepareSignals.__class__.__name__


registry.register_class(PrepareSignals,
                        DoPrepareSignals.__class__.__name__,
                        DoPrepareSignals)

