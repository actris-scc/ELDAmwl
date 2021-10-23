# -*- coding: utf-8 -*-
"""Classes for lidar ratio calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.factories.backscatter_factories.bsc_data_classes import RamanBscParams
from ELDAmwl.factories.extinction_factories.extinction_factories import ExtinctionParams
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.utils.constants import ERROR_METHODS
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import NC_FILL_STR

import numpy as np
import xarray as xr
import zope


class LidarRatioParams(ProductParams):

    def __init__(self):
        super(LidarRatioParams, self).__init__()
        self.sub_params += ['backscatter_params', 'extinction_params']
        self.bsc_prod_id = None
        self.ext_prod_id = None
        self.min_BscRatio_for_LR = None

        self.extinction_params = None
        self.backscatter_params = None

    def from_db(self, general_params):
        super(LidarRatioParams, self).from_db(general_params)

        query = self.db_func.read_lidar_ratio_params(general_params.prod_id)
        self.bsc_prod_id = query.raman_backscatter_options_product_id
        self.ext_prod_id = query.extinction_options_product_id
        self.general_params.error_method = ERROR_METHODS[query.error_method_id]  # noqa E501
        self.min_BscRatio_for_LR = query.min_BscRatio_for_LR

        bsc_general_params = self.from_id(self.bsc_prod_id)
        self.backscatter_params = RamanBscParams()
        self.backscatter_params.from_db(bsc_general_params)  # noqa E501
        self.backscatter_params.general_params.calc_with_lr = True
        self.backscatter_params.general_params.elpp_file = general_params.elpp_file  # noqa E501

        ext_general_params = self.from_id(self.ext_prod_id)
        self.extinction_params = ExtinctionParams()
        self.extinction_params.from_db(ext_general_params)
        self.extinction_params.general_params.calc_with_lr = True
        self.extinction_params.general_params.elpp_file = general_params.elpp_file  # noqa E501

    def assign_to_product_list(self, global_product_list):
        super(LidarRatioParams, self).assign_to_product_list(
            global_product_list,
        )
        self.backscatter_params.assign_to_product_list(global_product_list)
        self.extinction_params.assign_to_product_list(global_product_list)

    def to_meta_ds_dict(self, dct):
        """
        writes parameter content into Dict for further export in mwl file
        Args:
            dct (addict.Dict): is a dict which will be converted into dataset.
                            has the keys 'attrs' and 'data_vars'

        Returns:

        """
        super(LidarRatioParams, self).to_meta_ds_dict(dct)   # ToDo Ina debug
        # dct.data_vars.minimum_backscatter_ratio = self.min_BscRatio_for_LR


class LidarRatioFactory(BaseOperationFactory):
    """
     argument resolution, can be LOWRES(=0) or HIGHRES(=1)
    """

    name = 'LidarRatioFactory'

    def __call__(self, **kwargs):
        # assert 'data_storage' in kwargs
        assert 'lr_param' in kwargs
        assert 'resolution' in kwargs
        res = super(LidarRatioFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'lidarRatioFactoryDefault' .
        """
        return LidarRatioFactoryDefault.__name__


class LidarRatioFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`LidarRatios`.
    """

    name = 'lidarRatioFactoryDefault'

    param = None
    resolution = None
    ext = None
    bsc = None
    empty_lr = None
    result = None
    prod_id = NC_FILL_STR
    resolution = NC_FILL_INT

    def prepare(self):
        self.param = self.kwargs['lr_param']
        self.resolution = self.kwargs['resolution']
        self.prod_id = self.param.prod_id_str

        # ext and bsc are deepcopies from the data storage
        self.ext = self.data_storage.basic_product_common_smooth(self.param.ext_prod_id, self.resolution)
        self.bsc = self.data_storage.basic_product_common_smooth(self.param.bsc_prod_id, self.resolution)

        self.empty_lr = LidarRatios.init(self.ext, self.bsc, self.param)

    def get_non_merge_product(self):
        # create Dict with all params which are needed for the calculation
        lr_params = Dict({
            'error_method': self.param.error_method,
            'min_bsc_ratio': self.param.min_BscRatio_for_LR,
        })

        lr_routine = CalcLidarRatio()(
            prod_id=self.prod_id,
            ext=self.ext,
            bsc=self.bsc,
            lr_params=lr_params,
            empty_lr=self.empty_lr)

        lr = lr_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(lr_routine, IMonteCarlo)
            self.result.err[:] = adapter(self.param.mc_params)
        else:
            lr = lr

        del self.ext
        del self.bsc

        return lr

    def get_product(self):
        self.prepare()

        if not self.param.includes_product_merging():
            lr = self.get_non_merge_product()
        else:
            lr = None

        return lr


class LidarRatios(Products):
    """
    time series of lidar ratio profiles
    """
    @classmethod
    def init(cls, ext, bsc, p_params, **kwargs):
        """calculates LidarRatios from a backscatter and an extinction profile.

        Args:
            bsc (Backscatters): time series of backscatter coefficient profiles
            ext (Extinctions): time series of extinction coefficient profiles
            p_params (LidarRatioParams)
        """
        result = super(LidarRatios, cls).from_signal(ext, p_params, **kwargs)

        return result

    def to_meta_ds_dict(self, meta_data):
        # the parent method creates the Dict({'attrs': Dict(), 'data_vars': Dict()})
        # and attributes it with key self.mwl_meta_id to meta_data
        super(LidarRatios, self).to_meta_ds_dict(meta_data)
        dct = meta_data[self.mwl_meta_id]
        self.params.to_meta_ds_dict(dct)


class CalcLidarRatio(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
   lidar ratio from extinction and backscatter. In this case, it
    will be always an instance of SlopeToExtinctionDefault().
    """

    name = 'CalcLidarRatio'
    prod_id = NC_FILL_STR  # Todo Ina into Base class???

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        assert 'ext' in kwargs
        assert 'bsc' in kwargs
        assert 'lr_params' in kwargs
        assert 'empty_lr' in kwargs

        self.prod_id = kwargs['prod_id']
        res = super(CalcLidarRatio, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcLidarRatioDefault' .
        """
        return 'CalcLidarRatioDefault'


class CalcLidarRatioDefault(BaseOperation):
    """
    Calculates particle lidar ratio from extinction and backscatter.

    Keyword Args:
        ext (xarray.DataSet):
            profiles of particle extincion coefficient with \
            variables 'data', 'error', 'qf',
            'binres'
        bsc (xarray.DataSet):
            profiles of particle backscatter coefficient with \
            variables 'data', 'error', 'qf',
            'binres'
        lr_params (addict.Dict):
            with keys 'min_bsc_ratio' (lidar ratios are not calculated for data points with
                                        backscatter ratios smaller than this value)

    Returns:
        particle lidar ratio profiles (xarray.Dataset) with \
            variables 'data', 'error', 'qf',
            'binres',
    """

    name = 'CalcLidarRatioDefault'

    ext = None
    bsc = None
    result = None

    def __init__(self, **kwargs):
        self.ext = kwargs['ext']
        self.bsc = kwargs['bsc']
        self.result = deepcopy(kwargs['empty_lr'])

    def run(self, ext=None, bsc=None):
        if ext is None:
            ext = self.ext
        if bsc is None:
            bsc = self.bsc

        self.result.ds['data'] = ext.data / bsc.data
        self.result.ds['err'] = self.result.data * np.sqrt(
            np.power(ext.err / ext.err, 2) +
            np.power(bsc.err / bsc.err, 2))
        self.result.ds['qf'] = ext.qf | bsc.qf

        return self.result


registry.register_class(CalcLidarRatio,
                        CalcLidarRatioDefault.__name__,
                        CalcLidarRatioDefault)

registry.register_class(LidarRatioFactory,
                        LidarRatioFactoryDefault.__name__,
                        LidarRatioFactoryDefault)
