# -*- coding: utf-8 -*-
"""Classes for backscatter calculation"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory


class BackscatterFactoryDefault(BaseOperation):
    """ derives a single instance of :class:`Backscatters`.

    """

    name = 'BackscatterFactoryDefault'

    data_storage = None
    elast_sig = None
    calibr_window = None
    param = None
    empty_bsc = None
    prod_id = None
    resolution = None

    def prepare_calibr_window(self):
        # if time axis of calibr_window and signals are not equal -> interpolate calibr_window
        if self.elast_sig.ds.time.equals(self.calibr_window.time):
            return
        else:
            new_time_axis = self.elast_sig.ds.time
            new_calibr_window = self.calibr_window.interp(
                time=new_time_axis,
                method='nearest',
                kwargs={"fill_value": "extrapolate"})
            new_calibr_window['resolution'] = self.resolution
            self.calibr_window = new_calibr_window

    def prepare(self):
        self.resolution = self.kwargs['resolution']
        self.param = self.kwargs['bsc_param']
        self.calibr_window = self.kwargs['calibr_window']
        self.prod_id = self.param.prod_id_str

        if not self.param.includes_product_merging():
            self.elast_sig = self.data_storage.prepared_signal(
                self.param.prod_id_str,
                self.param.total_sig_id_str,
                self.resolution)

        self.prepare_calibr_window()

    def get_non_merge_product(self):
        pass

    def get_product(self):
        """get the products

        Returns: `.Backscatters`

        """
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
        assert 'resolution' in kwargs
        res = super(BackscatterFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        pass


# these are virtual classes, therefore, they need no registration
# registry.register_class(BackscatterFactory,
#                         BackscatterFactoryDefault.__name__,
#                         BackscatterFactoryDefault)
