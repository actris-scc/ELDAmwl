# -*- coding: utf-8 -*-
"""Classes for preparation of signals
(combining depol component, temporal integration, .."""
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import EBSC, VLDR, RESOLUTIONS, RESOLUTION_STR
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import KF
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import FIXED
from ELDAmwl.utils.numerical import bitwise_or_reduce, the_other_res


class PrepareSignalsForProductDefault(BaseOperation):
    """prepare ELPP signals for a product retrieval
    """
    resolution = None
    existing_signals = None
    pid = None
    data_already_exist = False

    def check_data_already_exist(self):
        # if integration time of low and high resolutions are the same
        # and one set of prepared signals already exists -> just make a copy
        current_res = self.resolution
        other_res = the_other_res(current_res)

        if self.data_storage.time_integration_multiple(current_res) == \
            self.data_storage.time_integration_multiple(other_res):
            existing_signals = self.data_storage.prepared_signals(self.pid, other_res)
            if len(existing_signals) > 0:
                self.data_already_exist = True

    def run(self):
        self.resolution = self.kwargs['resolution']

        self.bsc_param = self.kwargs['prod_param']
        pid = self.bsc_param.prod_id_str
        self.logger.debug('prepare signals for backscatter product {}'.format(pid), prod_id=pid)

        self.check_data_already_exist()
        if self.data_already_exist:
            for sig in self.existing_signals:
                self.data_storage.set_prepared_signal(pid, self.resolution, sig)


class PrepareBscSignalsDefault(PrepareSignalsForProductDefault):
    """prepare ELPP signals for extinction retrieval with the steps:
    1) set data points outside valid altitude range as invalid
    2) normalization by number of shots
    3) combination of depol component (if needed)
    4) correction of atmospheric transmission due to molecular scattering
    (not for Klett-Fernald)

    """
    bsc_param = None

    def combine_depol_components(self, p_param):
        self.logger.debug('PrepareBscSignalsDefault.combine_depol_components')
        pid = p_param.prod_id_str
        # transm_sig and refl_sig are deepcopies from the data storage
        transm_sig = self.data_storage.prepared_signal(pid,
                                                       p_param.transm_sig_id_str,
                                                       self.resolution)
        refl_sig = self.data_storage.prepared_signal(pid,
                                                     p_param.refl_sig_id_str,
                                                     self.resolution)
        total_sig = Signals.from_depol_components(transm_sig,
                                                  refl_sig)
        self.data_storage.set_prepared_signal(p_param.prod_id_str,
                                              self.resolution,
                                              total_sig)
        total_sig.register(p_param)

        # free the copies
        del transm_sig
        del refl_sig

    def run(self):
        self.bsc_param = self.kwargs['prod_param']
        self.pid = self.bsc_param.prod_id_str
        self.logger.debug('prepare signals for backscatter product {}'.format(self.pid), prod_id=self.pid)

        super(PrepareBscSignalsDefault, self).run()

        if not self.data_already_exist:
            # todo: prepare only the signals that are actually needed for the usecase
            # sig is a deepcopy from the data storage
            for sig in self.data_storage.integrated_signals(self.pid, self.resolution):
                prep_sig = deepcopy(sig)
                prep_sig.set_valid_height_range(self.bsc_param.valid_alt_range)
                prep_sig.normalize_by_shots()
                if (self.bsc_param.product_type == EBSC) and (self.bsc_param.elast_bsc_algorithm == KF):
                    pass
                else:
                    prep_sig.correct_for_mol_transmission()

                self.data_storage.set_prepared_signal(self.pid, self.resolution, prep_sig)

            if self.bsc_param.is_bsc_from_depol_components():
                self.combine_depol_components(self.bsc_param)


class PrepareBscSignals(BaseOperationFactory):
    """
    Args:
        prod_param (:class:`ELDAmwl.products.ProductParams`):
                            params of the product
    """

    name = 'PrepareBscSignals'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'prod_param' in kwargs
        assert 'resolution' in kwargs

        res = super(PrepareBscSignals, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareBscSignals' .
        """
        return PrepareBscSignalsDefault.__name__


class PrepareExtSignalsDefault(PrepareSignalsForProductDefault):
    """prepare ELPP signals for extinction retrieval with the steps:
    1) set data points outside valid altitude range as invalid
    2) normalization by number of shots
    3) correction of atmospheric transmission due to molecular scattering
    4) divide by Rayleigh scattering and calculate logarithm

    """
    ext_param = None

    def run(self):
        self.ext_param = self.kwargs['prod_param']
        self.pid = self.ext_param.prod_id_str
        self.logger.debug('prepare signals for extinction product {}'.format(self.pid))

        super(PrepareExtSignalsDefault, self).run()

        if not self.data_already_exist:
            # todo: prepare only the signals that are actually needed for the usecase
            # sig is deepcopy from data storage
            for sig in self.data_storage.integrated_signals(self.pid, self.resolution):
                if sig.is_Raman_sig:
                    prep_sig = deepcopy(sig)
                    prep_sig.set_valid_height_range(self.ext_param.valid_alt_range)
                    prep_sig.normalize_by_shots()
                    prep_sig.correct_for_mol_transmission()
                    prep_sig.prepare_for_extinction()

                    self.data_storage.set_prepared_signal(self.pid, self.resolution, prep_sig)


class PrepareExtSignals(BaseOperationFactory):
    """
    Args:
        prod_param (:class:`ELDAmwl.products.ProductParams`):
                            params of the product
    """

    name = 'PrepareExtSignals'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'prod_param' in kwargs
        assert 'resolution' in kwargs
        res = super(PrepareExtSignals, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'PrepareExtSignalsDefault' .
        """
        return PrepareExtSignalsDefault.__name__


class PrepareDepolSignals(BaseOperationFactory):
    """
    Args:
        prod_param (`.ProductParams`):
                            params of the product
    """

    name = 'PrepareDepolSignals'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'prod_param' in kwargs
        assert 'resolution' in kwargs

        res = super(PrepareDepolSignals, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'PrepareDepolSignalsDefault' .
        """
        return PrepareDepolSignalsDefault.__name__


class PrepareDepolSignalsDefault(PrepareSignalsForProductDefault):
    """prepare ELPP signals for retrieval of VLDR with the steps:
    1) set data points outside valid altitude range as invalid
    2) normalization by number of shots
    3) correction of atmospheric transmission due to molecular scattering

    """
    depol_param = None

    def run(self):
        self.depol_param = self.kwargs['prod_param']
        self.pid = self.depol_param.prod_id_str
        self.logger.debug('prepare signals for VLDR product {}'.format(self.pid))

        super(PrepareDepolSignalsDefault, self).run()

        if not self.data_already_exist:
            # todo: prepare only the signals that are actually needed for the usecase
            # sig is deepcopy from data storage
            for sig in self.data_storage.integrated_signals(self.pid, self.resolution):
                sig.set_valid_height_range(self.depol_param.valid_alt_range)
                sig.normalize_by_shots()
                sig.correct_for_mol_transmission()

                self.data_storage.set_prepared_signal(self.pid, self.resolution, sig)


PREP_SIG_CLASSES = {EXT: PrepareExtSignals,
                    RBSC: PrepareBscSignals,
                    EBSC: PrepareBscSignals,
                    VLDR: PrepareDepolSignals,
                    }


class PrepareSignalsDefault(BaseOperation):
    """
    """

    products = None  # list of products

    def time_integration(self):
        for res in RESOLUTIONS:
            multiple = self.data_storage.time_integration_multiple(res)

            cm = self.data_storage.cloud_mask.copy(deep=True)
            if multiple > 1:
                integrated_cloud_mask = cm.coarsen(time=multiple, boundary="pad").reduce(bitwise_or_reduce)
                integrated_cloud_mask['time'] = cm.time.coarsen(time=multiple, boundary='pad').min()
                self.data_storage.set_integrated_cloud_mask(res, integrated_cloud_mask)
                del cm
            else:
                self.data_storage.set_integrated_cloud_mask(res, cm)

            for p_param in self.products:
                p_id = p_param.prod_id_str
                elpp_signals = self.data_storage.elpp_signals(p_id)  # returns a deepcopy of the data in storage
                for ch_idx in range(len(elpp_signals)):
                    integrated_signal = elpp_signals[ch_idx]
                    integrated_signal.time_integration(multiple)
                    self.data_storage.set_integrated_signal(p_id, res, integrated_signal)

    def run(self):
        self.products = self.kwargs['products']

        # if the products (and signals) are to be smoothed and integrated onto a fixed, pre-defined grid
        if self.params.smooth_params.smooth_type == FIXED:
            self.logger.info('time integration of signals')
            self.time_integration()
            self.data_storage.remove('elpp_signals')
            self.data_storage.remove('cloud_mask')

        for p_param in self.products:
            if p_param.product_type in PREP_SIG_CLASSES:
                for res in RESOLUTIONS:
                    PREP_SIG_CLASSES[p_param.product_type]()(
                        data_storage=self.data_storage,
                        prod_param=p_param,
                        resolution=res)\
                        .run()
            else:
                self.logger.error(f'signal preparation for product type {p_param.product_type} '
                                  f'is not yet implemented')
                raise UseCaseNotImplemented('all', f'product type {p_param.product_type}', 'non')


class PrepareSignals(BaseOperationFactory):
    """
    Args:
        products: list of parameters of all basic
                products (list of :class:
                `ELDAmwl.products.ProductParams`)
    """

    name = 'PrepareSignals'

    def __call__(self, **kwargs):
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

registry.register_class(PrepareDepolSignals,
                        PrepareDepolSignalsDefault.__name__,
                        PrepareDepolSignalsDefault)

# virtual class PrepareSignalsForProductDefault needs no registration
