# -*- coding: utf-8 -*-
"""Classes for lidar ratio calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.lidar_ratio.product import LidarRatios
from ELDAmwl.utils.constants import MC
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import NC_FILL_STR

import numpy as np
import zope


class LidarRatioFactory(BaseOperationFactory):
    """
    """

    name = 'LidarRatioFactory'

    def __call__(self, **kwargs):
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
    prod_id = None
    resolution = None

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
    creates a Class for the calculation of a lidar ratio

    Returns an instance of BaseOperation which calculates the particle
    lidar ratio from extinction and backscatter. In this case, it
    will be always an instance of CalcLidarRatioDefault().

    Keyword Args:
        lr_params (:class:`ELDAmwl.lidar_ratio.params.LidarRatioParams`): \
                retrieval parameter of the lidar ratio product
        ext (:class:`ELDAmwl.extinction.product.Extinctions`): particle extinction profiles
        bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter (Raman) profiles
        empty_lr (:class:`ELDAmwl.lidar_ratio.product.LidarRatios`): \
                instance of LidarRatios which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    name = 'CalcLidarRatio'

    def __call__(self, **kwargs):
        assert 'lr_params' in kwargs
        assert 'ext' in kwargs
        assert 'bsc' in kwargs
        assert 'empty_lr' in kwargs

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

    The result is a copy of empty_lr, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        lr_params (:class:`ELDAmwl.lidar_ratio.params.LidarRatioParams`): \
                retrieval parameter of the lidar ratio product
        ext (:class:`ELDAmwl.extinction.product.Extinctions`): particle extinction profiles
        bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter (Raman) profiles
        empty_lr (:class:`ELDAmwl.lidar_ratio.product.LidarRatios`): \
                instance of LidarRatios which has all meta data but profile data are empty arrays

    Returns:
        particle lidar ratio profiles (:class:`ELDAmwl.lidar_ratio.product.LidarRatios`)

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
        """
        run the lidar ratio calculation

        The the optional keyword args 'ext' and 'bsc' allow to feed new input data into
        an existing instance of CalcLidarRatioDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals

        Keyword Args:
            ext (:class:`ELDAmwl.extinction.product.Extinctions`): extinction profiles, default=None
            bsc (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): Raman backscatter profiles, default=None

        Returns:
            profiles of particle lidar ratio (:class:`ELDAmwl.lidar_ratio.product.LidarRatios`)

        """
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
