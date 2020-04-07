# -*- coding: utf-8 -*-
"""Classes for preparation of signals
(combining depol components, temporal integration, .."""
from copy import deepcopy
from ELDAmwl.constants import EBSC, EXT, RBSC
from ELDAmwl.constants import KF
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.log import logger
from ELDAmwl.registry import registry
from ELDAmwl.signals import Signals

class DoPrepareBscSignals(BaseOperation):
    """prepare ELPP signals for extinction retrieval with the steps:
    1) normalization by number of shots
    2) combination of depol components (if needed)
    3) correction of atmospheric transmission due to molecular scattering
    (not for Klett-Fernald)

    """
    data_storage = None
    bsc_param = None

    def combine_depol_components(self, p_param):
            pid = p_param.prod_id_str
            transm_sig = self.data_storage.prepared_signal(pid,
                                                       p_param.transm_sig_id)
            refl_sig = self.data_storage.prepared_signal(pid,
                                                     p_param.refl_sig_id)
            total_sig = Signals.from_depol_components(transm_sig,
                                                      refl_sig)
            self.data_storage.set_prepared_signal(p_param.prod_id_str,
                                                  total_sig)
            total_sig.register(p_param)

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.bsc_param = self.kwargs['prod_param']

        pid = self.bsc_param.prod_id_str
        for sig in self.data_storage.elpp_signals(pid):
                new_sig = deepcopy(sig)
                new_sig.normalize_by_shots()
                self.data_storage.set_prepared_signal(pid, new_sig)
        if self.bsc_param.is_bsc_from_depol_components():
            self.combine_depol_components(self.bsc_param)

        if (self.bsc_param.product_type == EBSC) and \
            (self.bsc_param.elast_bsc_method == KF):
            pass
        else:
            for sig in self.data_storage.prepared_signals(pid):
                sig.correct_for_mol_transmission()



class PrepareBscSignals(BaseOperationFactory):
    """
    Args:
        data_storage (:class:`DataStorage`): global data storage
        prod_param (:class:`ProductParams`): params of the product
    """

    name = 'PrepareBscSignals'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'prod_param' in kwargs
        res = super(PrepareBscSignals, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareBscSignals' .
        """
        return DoPrepareBscSignals.__class__.__name__


class DoPrepareExtSignals(BaseOperation):
    """prepare ELPP signals for extinction retrieval with the steps:
    1) normalization by number of shots
    2) correction of atmospheric transmission due to molecular scattering
    3) divide by Rayleigh scattering and calculate logarithm

    """
    data_storage = None
    ext_param = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.ext_param = self.kwargs['prod_param']

        pid = self.ext_param.prod_id_str
        for sig in self.data_storage.elpp_signals(pid):
            if sig.is_Raman_sig:
                new_sig = deepcopy(sig)
                new_sig.normalize_by_shots()
                new_sig.correct_for_mol_transmission()
                new_sig.prepare_for_extinction()

                self.data_storage.set_prepared_signal(pid, new_sig)

class PrepareExtSignals(BaseOperationFactory):
    """
    Args:
        data_storage (:class:`DataStorage`): global data storage
        prod_param (:class:`ProductParams`): params of the product
    """

    name = 'PrepareExtSignals'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'prod_param' in kwargs
        res = super(PrepareExtSignals, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareExtSignals' .
        """
        return DoPrepareExtSignals.__class__.__name__


PREP_SIG_CLASSES = {EXT: PrepareExtSignals,
                    RBSC: PrepareBscSignals,
                    EBSC: PrepareBscSignals,
                    }


class DoPrepareSignals(BaseOperation):
    """
    """

    data_storage = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        products = self.kwargs['products']

        for p_param in products:
            if p_param.product_type in PREP_SIG_CLASSES:
                prep_sig = PREP_SIG_CLASSES[p_param.product_type]()\
                    (data_storage=self.data_storage,
                     prod_param=p_param)\
                    .run()


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

registry.register_class(PrepareExtSignals,
                        DoPrepareExtSignals.__class__.__name__,
                        DoPrepareExtSignals)

registry.register_class(PrepareBscSignals,
                        DoPrepareBscSignals.__class__.__name__,
                        DoPrepareBscSignals)
