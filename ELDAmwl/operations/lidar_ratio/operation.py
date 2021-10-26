# -*- coding: utf-8 -*-
"""Classes for lidar ratio calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.operations.lidar_ratio.product import LidarRatios
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import NC_FILL_STR

import numpy as np
import zope


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
            np.power(ext.err / ext.err, 2) + np.power(bsc.err / bsc.err, 2))
        self.result.ds['qf'] = ext.qf | bsc.qf

        return self.result


registry.register_class(CalcLidarRatio,
                        CalcLidarRatioDefault.__name__,
                        CalcLidarRatioDefault)

registry.register_class(LidarRatioFactory,
                        LidarRatioFactoryDefault.__name__,
                        LidarRatioFactoryDefault)
