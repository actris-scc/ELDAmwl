# -*- coding: utf-8 -*-
"""Classes for getting basic products
"""
from copy import deepcopy
from ELDAmwl.backscatter_factories import FindCommonBscCalibrWindow
from ELDAmwl.exceptions import UseCaseNotImplemented
from ELDAmwl.extinction_factories import ExtinctionFactory
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.raman_bsc_factories import RamanBackscatterFactory
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.registry import registry
from ELDAmwl.constants import AUTO, FIXED, RESOLUTIONS


class GetBasicProductsDefault(BaseOperation):
    """
    """

    data_storage = None
    product_params = None
    smooth_method = None

    def run(self):
        self.data_storage = self.kwargs['data_storage']
        self.product_params = self.kwargs['product_params']
        self.smooth_method = self.product_params.smooth_params.smooth_method

#        bsc_calibr_window = FindCommonBscCalibrWindow()(
#            data_storage=self.data_storage,
#            bsc_params=self.product_params.all_bsc_products(),
#            ).run()

        if self.smooth_method == AUTO:
            self.get_auto_smooth_products()
            self.find_common_smooth()

        elif self.smooth_method == FIXED:
            self.get_binres_common_smooth()

        else:
            raise(UseCaseNotImplemented('self.smooth_method',
                                        'smoothing',
                                        '{0} or {1}'.format(AUTO, FIXED)))

        self.get_common_smooth_products()

    def find_common_smooth(self):
        """
        finds a common vertical resolution (for lowres and highres) of all auto smoothed products
        and calculates corresponding bin resolutions for each product

        """
        pass

    def get_binres_common_smooth(self):
        """
        calculates bin resolution (for lowres and highres) for each product according to the
        fixed vertical resolution of the mwl product

        """
        sp = self.product_params.smooth_params

        for prod_param in self.product_params.basic_products():
            pid = prod_param.prod_id_str
            for res in RESOLUTIONS:
                dummy_sig = self.data_storage.prepared_signals(pid)[0]
                if prod_param.calc_with_res(res):
                    binres = dummy_sig.get_binres_from_fixed_smooth(sp, res)
                    self.data_storage.set_binres_common_smooth(pid, res, binres)


    def get_auto_smooth_products(self):
        self.get_raman_bsc_auto_smooth()
        self.get_extinctions_auto_smooth()
        # todo: get elast_bsc
        # todo: get vol_depol

    def get_common_smooth_products(self):
        self.get_extinctions_fixed_smooth()
        # todo: raman_bsc
        # todo: elsat_bsc
        # todo: vol_depol


    def get_extinctions_auto_smooth(self):
        for ext_param in self.product_params.extinction_products():
            extinction = ExtinctionFactory()(
                data_storage=self.data_storage,
                ext_param=ext_param,
                autosmooth=True,
            ).get_product()
            self.data_storage.set_basic_product_auto_smooth(
                ext_param.prod_id_str, extinction)

    def get_extinctions_fixed_smooth(self):
        for ext_param in self.product_params.extinction_products():
            for res in RESOLUTIONS:
                if ext_param.calc_with_res(res):
                    extinction = ExtinctionFactory()(
                        data_storage=self.data_storage,
                        ext_param=ext_param,
                        autosmooth=False,
                        resolution=res
                    ).get_product()
                    self.data_storage.set_basic_product_common_smooth(
                        ext_param.prod_id_str, res, extinction)

    def get_raman_bsc_auto_smooth(self):
        for bsc_param in self.product_params.raman_bsc_products():
            bsc = RamanBackscatterFactory()(
                data_storage=self.data_storage,
                bsc_param=bsc_param,
                calibr_window=self.bsc_calibr_window,
                autosmooth=True,
            ).get_product()
            # self.data_storage.set_basic_product_auto_smooth(
            #     bsc_param.prod_id_str, bsc)


class GetBasicProducts(BaseOperationFactory):
    """
    Args:
        data_storage (ELDAmwl.data_storage.DataStorage): global data storage
        product_params: global MeasurementParams
    """

    name = 'GetBasicProducts'
    smooth_method = None

    def __call__(self, **kwargs):
        assert 'data_storage' in kwargs
        assert 'product_params' in kwargs

        self.smooth_method = kwargs['product_params'].smooth_params.smooth_method
        res = super(GetBasicProducts, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'DoPrepareSignals' .
        """
        return GetBasicProductsDefault.__name__


registry.register_class(GetBasicProducts,
                        GetBasicProductsDefault.__name__,
                        GetBasicProductsDefault)
