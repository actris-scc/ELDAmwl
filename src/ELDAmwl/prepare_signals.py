# -*- coding: utf-8 -*-
"""Classes for preparation of signals
(combining depol component, temporal integration, .."""
from addict import Dict
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import KF
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.signals import Signals


class PrepareBscSignalsDefault(BaseOperation):
    """prepare ELPP signals for extinction retrieval with the steps:
    1) set data points outside valid altitude range as invalid
    2) normalization by number of shots
    3) combination of depol component (if needed)
    4) correction of atmospheric transmission due to molecular scattering
    (not for Klett-Fernald)

    """
    data_storage = None
    bsc_param = None

    def combine_depol_components(self, p_param):
        self.logger.debug('PrepareBscSignalsDefault.combine_depol_components')
        pid = p_param.prod_id_str
        # transm_sig and refl_sig are deepcopies from the data storage
        transm_sig = self.data_storage.prepared_signal(pid,
                                                       p_param.transm_sig_id)
        refl_sig = self.data_storage.prepared_signal(pid,
                                                     p_param.refl_sig_id)
        total_sig = Signals.from_depol_components(transm_sig,
                                                  refl_sig)
        self.data_storage.set_prepared_signal(p_param.prod_id_str,
                                              total_sig)
        total_sig.register(p_param)

        # free the copies
        del transm_sig
        del refl_sig

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.bsc_param = self.kwargs['prod_param']

        pid = self.bsc_param.prod_id_str
        # sig is a deepcopy from the data storage
        for sig in self.data_storage.elpp_signals(pid):
            sig.set_valid_height_range(self.bsc_param.valid_alt_range)
            sig.normalize_by_shots()
            if (self.bsc_param.product_type == EBSC) and \
                (self.bsc_param.elast_bsc_algorithm == KF):
                pass
            else:
                sig.correct_for_mol_transmission()

            self.data_storage.set_prepared_signal(pid, sig)

        if self.bsc_param.is_bsc_from_depol_components():
            self.combine_depol_components(self.bsc_param)


class PrepareBscSignals(BaseOperationFactory):
    """
    Args:
        data_storage (:class:`ELDAmwl.data_storage.DataStorage`):
                            global data storage
        prod_param (:class:`ELDAmwl.products.ProductParams`):
                            params of the product
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
        return PrepareBscSignalsDefault.__name__


class PrepareExtSignalsDefault(BaseOperation):
    """prepare ELPP signals for extinction retrieval with the steps:
    1) set data points outside valid altitude range as invalid
    2) normalization by number of shots
    3) correction of atmospheric transmission due to molecular scattering
    4) divide by Rayleigh scattering and calculate logarithm

    """
    data_storage = None
    ext_param = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.ext_param = self.kwargs['prod_param']

        pid = self.ext_param.prod_id_str
        # sig is deepcopy from data storage
        for sig in self.data_storage.elpp_signals(pid):
            if sig.is_Raman_sig:
                sig.set_valid_height_range(self.ext_param.valid_alt_range)
                sig.normalize_by_shots()
                sig.correct_for_mol_transmission()
                sig.prepare_for_extinction()

                self.data_storage.set_prepared_signal(pid, sig)


class PrepareExtSignals(BaseOperationFactory):
    """
    Args:
        data_storage (:class:`ELDAmwl.data_storage.DataStorage`):
                            global data storage
        prod_param (:class:`ELDAmwl.products.ProductParams`):
                            params of the product
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
        return PrepareExtSignalsDefault.__name__


PREP_SIG_CLASSES = {EXT: PrepareExtSignals,
                    RBSC: PrepareBscSignals,
                    EBSC: PrepareBscSignals,
                    }


class PrepareSignalsDefault(BaseOperation):
    """
    """

    data_storage = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        products = self.kwargs['products']

        for p_param in products:
            if p_param.product_type in PREP_SIG_CLASSES:
                PREP_SIG_CLASSES[p_param.product_type]()(
                    data_storage=self.data_storage,
                    prod_param=p_param)\
                    .run()


class PrepareSignals(BaseOperationFactory):
    """
    Args:
        data_storage: global data storage
                (:class:`ELDAmwl.data_storage.DataStorage`)
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
        return PrepareSignalsDefault.__name__


registry.register_class(PrepareSignals,
                        PrepareSignalsDefault.__name__,
                        PrepareSignalsDefault)

registry.register_class(PrepareExtSignals,
                        PrepareExtSignalsDefault.__name__,
                        PrepareExtSignalsDefault)

registry.register_class(PrepareBscSignals,
                        PrepareBscSignalsDefault.__name__,
                        PrepareBscSignalsDefault)
