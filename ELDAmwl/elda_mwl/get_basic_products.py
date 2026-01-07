# -*- coding: utf-8 -*-
"""Classes for getting basic products
"""
import psutil
from addict import Dict
from copy import deepcopy
from ELDAmwl.backscatter.bsc_ratio.product import BackscatterRatios
from ELDAmwl.backscatter.common.calibration.operation import FindCommonBscCalibrWindow
from ELDAmwl.backscatter.common.vertical_resolution.operation import ElastBscEffBinRes
from ELDAmwl.backscatter.common.vertical_resolution.operation import ElastBscUsedBinRes
from ELDAmwl.backscatter.common.vertical_resolution.operation import RamBscEffBinRes
from ELDAmwl.backscatter.common.vertical_resolution.operation import RamBscUsedBinRes
from ELDAmwl.backscatter.elastic.operation import ElastBackscatterFactory
from ELDAmwl.backscatter.raman.operation import RamanBackscatterFactory
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.depol.operation import VLRDFactory
from ELDAmwl.depol.vertical_resolution.operation import VLDREffBinRes
from ELDAmwl.depol.vertical_resolution.operation import VLDRUsedBinRes
from ELDAmwl.errors.exceptions import ELDAmwlException
from ELDAmwl.errors.exceptions import NoCalibrWindowFound
from ELDAmwl.errors.exceptions import UseCaseNotImplemented
from ELDAmwl.extinction.operation import ExtinctionFactory
from ELDAmwl.extinction.vertical_resolution.operation import ExtEffBinRes
from ELDAmwl.extinction.vertical_resolution.operation import ExtUsedBinRes
from ELDAmwl.utils.constants import AUTO, P_ALL_OK, LOWRES, HIGHRES
from ELDAmwl.utils.constants import EBSC
from ELDAmwl.utils.constants import EXT
from ELDAmwl.utils.constants import FIXED
from ELDAmwl.utils.constants import RBSC
from ELDAmwl.utils.constants import RESOLUTION_STR
from ELDAmwl.utils.constants import RESOLUTIONS
from ELDAmwl.utils.constants import VLDR

import numpy as np
import xarray as xr


# classes to convert effective bin resolution into bin resolution to use in retrievals
GET_USED_BINRES_CLASSES = {
    RBSC: RamBscUsedBinRes,
    EBSC: ElastBscUsedBinRes,
    EXT: ExtUsedBinRes,
    VLDR: VLDRUsedBinRes,
}

# classes to convert bin resolution used in retrievals into effective resolution
GET_EFF_BINRES_CLASSES = {
    RBSC: RamBscEffBinRes,
    EBSC: ElastBscEffBinRes,
    EXT: ExtEffBinRes,
    VLDR: VLDREffBinRes,
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
        # todo: write status of retrieval in database table eldamwl_product_status
        self.product_params = self.kwargs['product_params']
        self.smooth_type = self.product_params.smooth_params.smooth_type

        if len(self.product_params.all_bsc_products()) > 0:
            self.bsc_calibr_window = FindCommonBscCalibrWindow()(
                data_storage=self.data_storage,
                bsc_params=self.product_params.all_bsc_products()
            ).run()

        if self.smooth_type == AUTO:
            self.get_auto_smooth_products()
            self.find_common_smooth()

        elif self.smooth_type == FIXED:
            self.calc_common_vertical_resolution()
            self.get_binres_common_smooth()

        else:
            raise(UseCaseNotImplemented('self.smooth_type',
                                        'smoothing',
                                        '{0} or {1}'.format(AUTO, FIXED)))

        self.get_common_smooth_products()
        self.data_storage.remove('integrated_signals')

    def find_common_smooth(self):
        """
        finds a common vertical resolution (for lowres and highres) of all auto smoothed products
        and calculates corresponding bin resolutions for each product

        """
        pass

    def calc_common_vertical_resolution(self):
        """calculates an array of height resolution (for lowres and highres) according to the
        fixed vertical resolution of the mwl product

        """
        print('calculate profile of common height resolution')
        sp = self.product_params.smooth_params
        station_height = float(self.data_storage.header.vars.station_altitude)

        for res in RESOLUTIONS:
            # use dimensions and axes of cloud_mask
            cm = self.data_storage.integrated_cloud_mask(res)

            # create empty array
            vres = xr.DataArray(np.ones(cm.shape)*np.nan,
                                dims=cm.dims,
                                name='vertical_resolution',
                                coords=cm.coords,
                                attrs={
                                    'long_name': 'effective vertical resolution of the products',
                                    '_FillValue': np.nan,
                                    'units': 'm',
                                    })

            # resolutions below and above transition zone
            vert_res_low = sp.vert_res[RESOLUTION_STR[res]]['lowrange']
            vert_res_high = sp.vert_res[RESOLUTION_STR[res]]['highrange']

            for t in range(cm.time.shape[0]):
                # first and last bin of transition zone
                tz_bottom_bin = np.where(cm.altitude[t].values > (sp.transition_zone.bottom + station_height))[0][0]
                tz_top_bin = np.where(cm.altitude[t].values > (sp.transition_zone.top + station_height))[0][0]

                # gradient within transition zone
                delta_res = (vert_res_high - vert_res_low) / (tz_top_bin - tz_bottom_bin)

                # ! reversed logic! because
                # where(condition, fillvalue where condition is not true)
                vres[t] = vres[t].where(vres.level > tz_bottom_bin, vert_res_low)
                vres[t] = vres[t].where(vres.level < tz_top_bin, vert_res_high)

                # fill data in transition zone
                for idx in range(int(tz_bottom_bin), int(tz_top_bin)):
                    vres[t, idx] = float(vert_res_low + delta_res * (idx - tz_bottom_bin))

            # write vres in data storage
            self.data_storage.set_common_vertical_resolution(res, vres)

    def get_binres_common_smooth(self):
        """
        calculates bin resolution (for lowres and highres) for each basic product according to the
        fixed vertical resolution of the mwl product

        """
        self.logger.info('get bin resolution of products for common smoothing')
        sp = self.product_params.smooth_params

        for res in RESOLUTIONS:
            for prod_param in self.product_params.basic_products(res=res):
                pid = prod_param.prod_id_str
                used_binres_routine = GET_USED_BINRES_CLASSES[prod_param.product_type]()(prod_id=pid)
                # todo: get binres for all signals involved in the product and then store the max of them
                # dummy_sig is a deepcopy from data storage
                dummy_sig = self.data_storage.prepared_signals(pid, res)[0]
                binres = dummy_sig.get_binres_from_fixed_smooth(
                    sp,
                    res,
                    used_binres_routine=used_binres_routine,
                )
                self.data_storage.set_binres_common_smooth(pid, res, binres)

    def get_auto_smooth_products(self):
        """get all basic products with automatic smoothing

        """
        self.logger.info('get automatically smoothed products')
        self.get_raman_bsc_auto_smooth()
        self.get_extinctions_auto_smooth()
        # todo: get elast_bsc
        # todo: get vol_depol

    def get_common_smooth_products(self):
        """get all basic products with pre-defined smoothing

        """
        self.logger.info('get products on common smooth grid')  # pmem(rss=208.117.760
        print(psutil.Process().memory_full_info().uss)
        # self.get_extinctions_fixed_smooth()
        # print(psutil.Process().memory_full_info().uss)  # -> 209 346 560
        # self.get_raman_bsc_fixed_smooth()  # -> 322 306 048 (ohne ext)

        # print(psutil.Process().memory_full_info().uss)
        self.get_elast_bsc_fixed_smooth()  # MEM -> 969 400 320 ohne ext, mit Rbsc
        print(psutil.Process().memory_full_info().uss)
        self.get_bsc_ratios_fixed_smooth()  # MEM -> 969 400 320
        print(psutil.Process().memory_full_info().uss)
        self.get_vldr_fixed_smooth()  # MEM -> 3.307.786.240
        print(psutil.Process().memory_full_info().uss)
        self.single_products_quality_control()  # MEM -> pmem(rss=7.881.302.016
        print(psutil.Process().memory_full_info().uss)

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
        for res in RESOLUTIONS:
            ext_params = self.product_params.extinction_products(res=res)
            if len(ext_params) == 0:
                self.logger.warning(f'no extinction products will be calculated with {RESOLUTION_STR[res]}')
            for ext_param in ext_params:
                self.logger.info('get extinction at {0} nm (product id {1})'.format(
                    ext_param.general_params.emission_wavelength, ext_param.prod_id_str))

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
        if len(self.product_params.raman_bsc_products()) == 0:
            self.logger.warning('no Raman backscatter products will be calculated')

        for bsc_param in self.product_params.raman_bsc_products():
            prod_id = bsc_param.prod_id_str
            self.logger.info('get Raman backscatter at {0} nm (product id {1})'.format(
                bsc_param.general_params.emission_wavelength,
                prod_id
            ))

            # if no common calibration window for all bsc has been found
            # -> use calibration window of the individual bsc product
            if self.bsc_calibr_window is not None:
                cal_win = self.bsc_calibr_window
            elif bsc_param.calibr_window is not None:
                cal_win = bsc_param.calibr_window
            else:
                raise NoCalibrWindowFound(prod_id)

            # calc preliminary bsc
            if self.data_storage.time_integration_multiple(LOWRES) == \
                    self.data_storage.time_integration_multiple(HIGHRES):
                calculator = RamanBackscatterFactory()(
                    data_storage=self.data_storage,
                    bsc_param=bsc_param,
                    calibr_window=cal_win,
                    autosmooth=False,
                    resolution=HIGHRES,
                    )
                bsc = calculator.get_product()
                del calculator
            else:
                bsc = None

            for res in RESOLUTIONS:
                # if resolution res is required: make a copy of bsc and smooth it
                if bsc_param in self.product_params.all_products_of_res(res):
                    if bsc is None:
                        calculator = RamanBackscatterFactory()(
                            data_storage=self.data_storage,
                            bsc_param=bsc_param,
                            calibr_window=cal_win,
                            autosmooth=False,
                            resolution=res,
                        )
                        res_bsc = calculator.get_product()
                        # del calculator
                    else:
                        res_bsc = bsc

                    smooth_bsc = res_bsc.copy()
                    smooth_bsc.smooth(self.data_storage.binres_common_smooth(prod_id, res))
                    smooth_bsc.resolution = res
                    self.data_storage.set_basic_product_common_smooth(
                        prod_id, res, smooth_bsc)
                bsc = None  # pmem(rss=237252608, vms=1148125184, shared=72712192, text=2658304, lib=0, data=482574336, dirty=0)
                del res_bsc

    def get_elast_bsc_fixed_smooth(self):
        if len(self.product_params.elast_bsc_products()) == 0:
            self.logger.warning('no elastic backscatter products will be calculated')

        for bsc_param in self.product_params.elast_bsc_products():
            self.logger.info('get elastic backscatter at {0} nm  (product id {1})'.format(
                bsc_param.general_params.emission_wavelength,
                bsc_param.prod_id_str
            ))
            prod_id = bsc_param.prod_id_str

            # if no common calibration window for all bsc has been found
            # -> use calibration window of the individual bsc product
            if self.bsc_calibr_window is not None:
                cal_win = self.bsc_calibr_window
            elif bsc_param.calibr_window is not None:
                cal_win = bsc_param.calibr_window
            else:
                raise NoCalibrWindowFound(prod_id)

            try:
                if self.data_storage.time_integration_multiple(LOWRES) == \
                        self.data_storage.time_integration_multiple(HIGHRES):
                    # calc preliminary bsc
                    bsc = ElastBackscatterFactory()(
                        data_storage=self.data_storage,
                        bsc_param=bsc_param,
                        calibr_window=cal_win,
                        autosmooth=False,
                        resolution=HIGHRES,
                    ).get_product()
                else:
                    bsc = None

                for res in RESOLUTIONS:
                    # if resolution res is required: make a copy of bsc and smooth it
                    if bsc_param in self.product_params.all_products_of_res(res):
                        if bsc is None:
                            res_bsc = ElastBackscatterFactory()(
                                data_storage=self.data_storage,
                                bsc_param=bsc_param,
                                calibr_window=cal_win,
                                autosmooth=False,
                                resolution=res,
                            ).get_product()
                        else:
                            res_bsc = bsc
                        smooth_bsc = deepcopy(res_bsc)
                        smooth_bsc.smooth(self.data_storage.binres_common_smooth(prod_id, res))
                        smooth_bsc.resolution = res
                        self.data_storage.set_basic_product_common_smooth(
                            prod_id, res, smooth_bsc)
                bsc = None
                del res_bsc
            except ELDAmwlException as e:
                self.logger.error('cannot get backscatter product {}'.format(bsc_param.prod_id_str))
                bsc_param.mark_as_failed(self.product_params)

    def get_bsc_ratios_fixed_smooth(self):
        """"get backscatter ratios from all scheduled backscatter coefficients
        """

        for res in RESOLUTIONS:
            bsc_params = self.product_params.all_bsc_products(res=res)
            num_bsc = len(bsc_params)
            if num_bsc == 0:
                self.logger.warning(f'no backscatter ratio can be calculated with '
                                    f'{RESOLUTION_STR[res]} because no bsc coef is available')
            for bsc_param in bsc_params:
                prod_id = bsc_param.prod_id_str
                wl = bsc_param.general_params.emission_wavelength
                self.logger.info(f'get backscatter ratio at {wl} nm '
                                 f'from product {prod_id} '
                                 f'with {RESOLUTION_STR[res]} resolution')
                # find corresponding bsc profile
                bsc = self.data_storage.basic_product_common_smooth(prod_id, res)
                # calculate backscatter ratio and put it in data storage
                bsc_ratio = BackscatterRatios.from_bsc(bsc)
                self.data_storage.set_basic_product_common_smooth(
                    bsc_ratio.product_id_str, res, bsc_ratio)

                del bsc

    def get_vldr_fixed_smooth(self):
        if len(self.product_params.vldr_products()) == 0:
            self.logger.warning('no VLDR products will be calculated')

        for depol_param in self.product_params.vldr_products():
            prod_id = depol_param.prod_id_str
            self.logger.info('get VLDR at {0} nm (product id {1})'.format(
                depol_param.general_params.emission_wavelength,
                prod_id
            ))

            # calc preliminary vlrd
            if self.data_storage.time_integration_multiple(LOWRES) == \
                    self.data_storage.time_integration_multiple(HIGHRES):
                vldr = VLRDFactory()(
                    data_storage=self.data_storage,
                    vldr_param=depol_param,
                    autosmooth=False,
                    resolution=HIGHRES,
                ).get_product()
            else:
                vldr = None

            for res in RESOLUTIONS:
                # if resolution res is required: make a copy of bsc and smooth it
                if depol_param in self.product_params.all_products_of_res(res):
                    if vldr is None:
                        res_vlrd = VLRDFactory()(
                            data_storage=self.data_storage,
                            vldr_param=depol_param,
                            autosmooth=False,
                            resolution=res,
                            ).get_product()
                    else:
                        res_vlrd = vldr
                    smooth_vldr = deepcopy(res_vlrd)
                    smooth_vldr.smooth(self.data_storage.binres_common_smooth(prod_id, res))
                    smooth_vldr.resolution = res
                    self.data_storage.set_basic_product_common_smooth(
                        prod_id, res, smooth_vldr)
            del vldr
            del res_vlrd

    def single_products_quality_control(self):
        self.logger.info('quality control of individual basic products')
        for res in RESOLUTIONS:
            all_products = self.product_params.basic_products(res=res)
            # todo: add bsc ratio
            for prod_param in all_products:
                prod_id = prod_param.prod_id_str
                print(f'quality control of product {prod_id} with resolution {RESOLUTION_STR[res]}')
                product = self.data_storage.basic_product_common_smooth(prod_id, res)
                product.quality_control()
                self.data_storage.set_basic_product_qc(prod_id, res, product)
        self.data_storage.remove('basic_products_common_smooth')


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
