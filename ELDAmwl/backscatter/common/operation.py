# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.utils.constants import NC_FILL_STR


class BackscatterFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`Backscatters`.
    """

    _name = 'BackscatterFactoryDefault'

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

    _name = 'BackscatterFactory'

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
