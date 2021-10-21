# -*- coding: utf-8 -*-
"""Classes for getting basic products
"""
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoCalibrWindowFound
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.factories.backscatter_factories.backscatter_calibration import FindCommonBscCalibrWindow
from ELDAmwl.factories.backscatter_factories.bsc_vertical_resolution import ElastBscEffBinRes
from ELDAmwl.factories.backscatter_factories.bsc_vertical_resolution import ElastBscUsedBinRes
from ELDAmwl.factories.backscatter_factories.bsc_vertical_resolution import RamBscEffBinRes
from ELDAmwl.factories.backscatter_factories.bsc_vertical_resolution import RamBscUsedBinRes
from ELDAmwl.factories.backscatter_factories.raman_bsc_factories import RamanBackscatterFactory
from ELDAmwl.factories.extinction_factories.ext_vertical_resolution import ExtEffBinRes
from ELDAmwl.factories.extinction_factories.ext_vertical_resolution import ExtUsedBinRes
from ELDAmwl.factories.extinction_factories.extinction_factories import ExtinctionFactory
from ELDAmwl.utils.constants import AUTO
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import FIXED
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTIONS


# classes to convert effective bin resolution into bin resolution to use in retrievals
GET_USED_BINRES_CLASSES = {
    RBSC: RamBscUsedBinRes,
    EBSC: ElastBscUsedBinRes,
    EXT: ExtUsedBinRes,
}

# classes to convert bin resolution used in retrievals into effective resolution
GET_EFF_BINRES_CLASSES = {
    RBSC: RamBscEffBinRes,
    EBSC: ElastBscEffBinRes,
    EXT: ExtEffBinRes,
}


class GetBasicProductsDefault(BaseOperation):
    """
    """
    name = 'GetBasicProductsDefault'

    data_storage = None
    product_params = None
    smooth_type = None
    bsc_calibr_window = None

    def run(self):
        self.product_params = self.kwargs['product_params']
        self.smooth_type = self.product_params.smooth_params.smooth_type

        self.bsc_calibr_window = FindCommonBscCalibrWindow()(
            data_storage=self.data_storage,
            bsc_params=self.product_params.all_bsc_products()).run()

        if self.smooth_type == AUTO:
            self.get_auto_smooth_products()
            self.find_common_smooth()

        elif self.smooth_type == FIXED:
            self.get_binres_common_smooth()

        else:
            raise(UseCaseNotImplemented('self.smooth_type',
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
        calculates bin resolution (for lowres and highres) for each basic product according to the
        fixed vertical resolution of the mwl product

        """
        sp = self.product_params.smooth_params

        for prod_param in self.product_params.basic_products():
            pid = prod_param.prod_id_str
            if prod_param.product_type in [EXT, RBSC]:  # todo remove this limit
                used_binres_routine = GET_USED_BINRES_CLASSES[prod_param.product_type]()(prod_id=pid)
                for res in RESOLUTIONS:
                    # dummy_sig is a deepcopy from data storage
                    dummy_sig = self.data_storage.prepared_signals(pid)[0]
                    if prod_param in self.product_params.all_products_of_res(res):
                        binres = dummy_sig.get_binres_from_fixed_smooth(
                            sp,
                            res,
                            used_binres_routine=used_binres_routine,
                        )
                        self.data_storage.set_binres_common_smooth(pid, res, binres)

    def get_auto_smooth_products(self):
        """get all basic products with automatic smoothing

        """
        self.get_raman_bsc_auto_smooth()
        self.get_extinctions_auto_smooth()
        # todo: get elast_bsc
        # todo: get vol_depol

    def get_common_smooth_products(self):
        """get all basic products with pre-defined smoothing

        """
        self.get_extinctions_fixed_smooth()
        self.get_raman_bsc_fixed_smooth()
        # todo: elsat_bsc
        # todo: vol_depol

    def get_extinctions_auto_smooth(self):
        """get extinction products with automatic smoothing

        """
        for ext_param in self.product_params.extinction_products():
            extinction = ExtinctionFactory()(
                data_storage=self.data_storage,
                ext_param=ext_param,
                autosmooth=True,
            ).get_product()
            self.data_storage.set_basic_product_auto_smooth(
                ext_param.prod_id_str, extinction)

    def get_extinctions_fixed_smooth(self):
        """get extinction products with pre-defined smoothing

        """
        for ext_param in self.product_params.extinction_products():
            for res in RESOLUTIONS:
                if ext_param.calc_with_res(res):
                    extinction = ExtinctionFactory()(
                        data_storage=self.data_storage,
                        ext_param=ext_param,
                        autosmooth=False,
                        resolution=res,
                    ).get_product()
                    self.data_storage.set_basic_product_common_smooth(
                        ext_param.prod_id_str, res, extinction)

    def get_raman_bsc_auto_smooth(self):
        for bsc_param in self.product_params.raman_bsc_products():
            prod_id = bsc_param.prod_id_str

            bsc = RamanBackscatterFactory()(
                data_storage=self.data_storage,
                bsc_param=bsc_param,
                calibr_window=self.bsc_calibr_window,
                autosmooth=True,
            ).get_product()

            self.data_storage.set_basic_product_raw(
                prod_id, bsc)

            smooth_bsc = self.data_storage.basic_product_raw(prod_id)
            smooth_bsc.smooth(self.data_storage.binres_auto_smooth(prod_id))
            self.data_storage.set_basic_product_auto_smooth(
                prod_id, smooth_bsc)

    def get_raman_bsc_fixed_smooth(self):
        for bsc_param in self.product_params.raman_bsc_products():
            prod_id = bsc_param.prod_id_str

            # if no common calibration window for all bsc has been found
            # -> use calibration window of the individual bsc product
            if self.bsc_calibr_window is not None:
                cal_win = self.bsc_calibr_window
            elif bsc_param.calibr_window is not None:
                cal_win = bsc_param.calibr_window
            else:
                raise NoCalibrWindowFound(prod_id)

            # calc preliminary bsc
            bsc = RamanBackscatterFactory()(
                data_storage=self.data_storage,
                bsc_param=bsc_param,
                calibr_window=cal_win,
                autosmooth=False,
            ).get_product()

            for res in RESOLUTIONS:
                # if resolution res is required: make a copy of bsc and smooth it
                if bsc_param in self.product_params.all_products_of_res(res):
                    smooth_bsc = deepcopy(bsc)
                    smooth_bsc.smooth(self.data_storage.binres_common_smooth(prod_id, res))
                    self.data_storage.set_basic_product_common_smooth(
                        prod_id, res, smooth_bsc)
            del bsc


class GetBasicProducts(BaseOperationFactory):
    """
    Args:
        product_params: global MeasurementParams
    """

    name = 'GetBasicProducts'
    smooth_type = None

    def __call__(self, **kwargs):
        assert 'product_params' in kwargs

        self.smooth_type = kwargs['product_params'].smooth_params.smooth_type
        res = super(GetBasicProducts, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'GetBasicProductsDefault' .
        """
        return GetBasicProductsDefault.__name__


registry.register_class(GetBasicProducts,
                        GetBasicProductsDefault.__name__,
                        GetBasicProductsDefault)
