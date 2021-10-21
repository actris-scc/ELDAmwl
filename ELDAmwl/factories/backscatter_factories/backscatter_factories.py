# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from ELDAmwl.bases.factory import BaseOperation, BaseOperationFactory
from ELDAmwl.errors.exceptions import CalRangeHigherThanValid
from ELDAmwl.factories.backscatter_factories.backscatter_calibration import BscCalibrationParams
from ELDAmwl.output.mwl_file_structure import MWLFileVarsFromDB
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.signals import Signals
from ELDAmwl.utils.constants import NC_FILL_STR


class BackscatterParams(ProductParams):

    def __init__(self):
        super(BackscatterParams, self).__init__()
        self.sub_params += ['calibration_params']
        self.calibration_params = None
        self.total_sig_id = None
        self.transm_sig_id = None
        self.refl_sig_id = None
        self.cross_sig_id = None
        self.parallel_sig_id = None
        self.bsc_method = None

    def from_db(self, general_params):
        super(BackscatterParams, self).from_db(general_params)

        self.calibration_params = BscCalibrationParams.from_db(general_params)  # noqa E501
        if self.calibration_params.cal_interval.max_height > \
                self.general_params.valid_alt_range.max_height:
            raise CalRangeHigherThanValid(self.prod_id_str)

    def add_signal_role(self, signal):
        super(BackscatterParams, self)
        if signal.is_elast_sig:
            if signal.is_total_sig:
                self.total_sig_id = signal.channel_id_str
            if signal.is_cross_sig:
                self.cross_sig_id = signal.channel_id_str
            if signal.is_parallel_sig:
                self.parallel_sig_id = signal.channel_id_str
            if signal.is_transm_sig:
                self.transm_sig_id = signal.channel_id_str
            if signal.is_refl_sig:
                self.refl_sig_id = signal.channel_id_str
        else:
            self.logger.debug('channel {0} is no elast signal'.format(signal.channel_id_str))

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        mwl_vars = MWLFileVarsFromDB()
        dct.data_vars.retrieval_method = mwl_vars.bsc_method_var(self.bsc_method)
        self.calibration_params.to_meta_ds_dict(dct)


class Backscatters(Products):
    """
    time series of backscatter profiles
    """

    calibr_window = None

    @classmethod
    def init(cls, signal, p_params, calibr_window=None):
        """calculates Backscatters from an elastic signal.

        The signal was previously prepared by PrepareBscSignals .

        Args:
            signal (:class:`Signals`): time series of signal profiles
            p_params (:class:`BackscatterParams`):
                        calculation params of the backscatter product
            calibr_window (tuple):
                        first and last height_axis of the calibration window [m]
        """
        result = super(Backscatters, cls).from_signal(signal, p_params)
        # cls.calibr_window = calibr_window  ToDo: Ina debug

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(Backscatters, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)
        dct.data_vars.calibration_range = self.calibr_window


class BackscatterFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`Backscatters`.
    """

    name = 'BackscatterFactoryDefault'

    data_storage = None
    elast_sig = None
    calibr_window = None
    param = None
    empty_bsc = None
    prod_id = NC_FILL_STR

    def prepare(self):
        self.param = self.kwargs['bsc_param']
        self.calibr_window = self.kwargs['calibr_window']
        self.prod_id = self.param.prod_id_str

        if not self.param.includes_product_merging():
            self.elast_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.total_sig_id)

    def get_non_merge_product(self):
        pass

    def get_product(self):
        self.prepare()

        if not self.param.includes_product_merging():
            bsc = self.get_non_merge_product()
        else:
            bsc = None

        return bsc


class BackscatterFactory(BaseOperationFactory):
    """
    derives a single instance of :class:`Backscatters`.
    """

    name = 'BackscatterFactory'

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'bsc_param' in kwargs
        assert 'autosmooth' in kwargs
        assert 'calibr_window' in kwargs
        res = super(BackscatterFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        pass


# these are virtual classes, therefore, they need no registration
# registry.register_class(BackscatterFactory,
#                         BackscatterFactoryDefault.__name__,
#                         BackscatterFactoryDefault)
