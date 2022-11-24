# -*- coding: utf-8 -*-
"""Classes for angstroem exponent calculation"""
from addict import Dict
from copy import deepcopy
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import IMonteCarlo
from ELDAmwl.component.registry import registry
from ELDAmwl.angstroem_exponent.product import AngstroemExps
from ELDAmwl.utils.constants import MC  # ToDo needed?
from ELDAmwl.utils.constants import NC_FILL_INT # ToDo needed?
from ELDAmwl.utils.constants import NC_FILL_STR # ToDo needed?

import numpy as np
import zope


class AngstroemExpFactory(BaseOperationFactory):
    """
    """

    name = 'LidarRatioFactory'

    def __call__(self, **kwargs):
        assert 'lr_param' in kwargs
        assert 'resolution' in kwargs
        res = super(AngstroemExpFactory, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'lidarRatioFactoryDefault' .
        """
        return AngstroemExpFactoryDefault.__name__


class AngstroemExpFactoryDefault(BaseOperation):
    """
    derives a single instance of :class:`AngstroemExps`.
    """

    name = 'angstroemExpFactoryDefault'

    param = None
    resolution = None
    ext = None
    bsc = None
    empty_lr = None
    result = None
    prod_id = NC_FILL_STR
    resolution = NC_FILL_INT

    def prepare(self):
        self.param = self.kwargs['ae_param']
        self.resolution = self.kwargs['resolution']
        self.prod_id = self.param.prod_id_str

        # ext and bsc are deepcopies from the data storage
        self.ext = self.data_storage.basic_product_common_smooth(self.param.lwvl_prod_id, self.resolution)
        self.bsc = self.data_storage.basic_product_common_smooth(self.param.hwvl_prod_id, self.resolution)

        self.empty_ae = AngstroemExps.init(self.lwvl, self.hwvl, self.param)

    def get_non_merge_product(self):
        # create Dict with all params which are needed for the calculation
        ae_params = Dict({
            'error_method': self.param.error_method,
            # 'min_bsc_ratio': self.param.min_BscRatio_for_LR,
        })

        ae_routine = CalcAngstroemExp()(
            prod_id=self.prod_id,
            lwvl=self.lwvl,
            hwvl=self.hvwl,
            ae_params=ae_params,
            empty_ae=self.empty_ae)

        ae = ae_routine.run()

        if self.param.error_method == MC:
            adapter = zope.component.getAdapter(ae_routine, IMonteCarlo)
            self.result.err[:] = adapter(self.param.mc_params)
        else:
            ae = ae

        del self.lwvl
        del self.hwvl

        return ae

    def get_product(self):
        self.prepare()

        if not self.param.includes_product_merging():
            lr = self.get_non_merge_product()
        else:
            lr = None

        return lr


class CalcAngstroemExp(BaseOperationFactory):
    """
    creates a Class for the calculation of an Angstroem Exponent

    Returns an instance of BaseOperation which calculates the angstroem exponent
    from backscatter or extinction at two different wavelengths.
    In this case, it will be always an instance of CalcAngstroemExpDefault().

    Keyword Args:
        ae_params (:class:`ELDAmwl.angstroem_exponent.params.AngstroemExpParams`): \
                retrieval parameter of the angstroem exponent product
        lwvl (:class:`ELDAmwl.extinction.product.Extinctions`): particle extinction profiles
        hwvl (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter (Raman) profiles
        empty_ae (:class:`ELDAmwl.angstroem_exponent.product.AngstroemExps`): \
                instance of AngstroemExps which has all meta data but profile data are empty arrays

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """

    name = 'CalcAngstroemExp'

    def __call__(self, **kwargs):
        assert 'ae_params' in kwargs
        assert 'lwvl' in kwargs
        assert 'hwvl' in kwargs
        assert 'empty_ae' in kwargs

        res = super(CalcAngstroemExp, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CalcAngstroemExpDefault' .
        """
        return 'CalcAngstroemExpDefault'


class CalcAngstroemExpDefault(BaseOperation):
    """
    Calculates angstroem exponent from backscatter or extinction at two different wavelengths.

    The result is a copy of empty_ae, but its dataset (data, err, qf) is filled with the calculated values

    Keyword Args:
        ae_params (:class:`ELDAmwl.angstroem_exponent.params.AngstroemExpParams`): \
                retrieval parameter of the angstroem exponent product
        lwvl (:class:`ELDAmwl.extinction.product.Extinctions`): particle extinction profiles    # ToDo change
        hwvl (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): particle backscatter (Raman) profiles  # ToDo change
        empty_ae (:class:`ELDAmwl.angstroem_exponents.product.AngstroemExps`): \
                instance of AngstroemExp which has all meta data but profile data are empty arrays

    Returns:
        particle lidar ratio profiles (:class:`ELDAmwl.lidar_ratio.product.LidarRatios`)

    """

    name = 'CalcAngstroemExpDefault'

    lwvl = None
    hwvl = None
    result = None

    def __init__(self, **kwargs):
        self.lwvl = kwargs['lwvl']
        self.hwvl = kwargs['hwvl']
        self.result = deepcopy(kwargs['empty_ae'])

    def run(self, lwvl=None, hwvl=None):
        """
        run the angstrom exponent calculation

        The optional keyword args 'lwvl' and 'hwvl' allow to feed new input data into
        an existing instance of CalcAngstroemExtDefault and run a new calculation.
        This feature is used e.g., for Monte-Carlo error retrievals # ToDo needed?

        Keyword Args:
            lwvl (:class:`ELDAmwl.extinction.product.Extinctions`): extinction profiles, default=None   # ToDo change
            hwvl (:class:`ELDAmwl.backscatter.raman.product.RamanBackscatters`): Raman backscatter profiles, default=None   # ToDo change

        Returns:
            profiles of angstroem exponents (:class:`ELDAmwl.angstroem_exponent.product.AngstroemExps`)

        """
        if lwvl is None:
            lwvl = self.lwvl
        if hwvl is None:
            hwvl = self.hwvl

        self.result.ds['data'] = hwvl.data / lwvl.data
        self.result.ds['err'] = self.result.data * np.sqrt(
            np.power(hwvl.err / hwvl.err, 2) + np.power(lwvl.err / lwvl.err, 2))
        self.result.ds['qf'] = hwvl.qf | lwvl.qf

        return self.result


registry.register_class(CalcAngstroemExp,
                        CalcAngstroemExpDefault.__name__,
                        CalcAngstroemExpDefault)

registry.register_class(AngstroemExpFactory,
                        AngstroemExpFactoryDefault.__name__,
                        AngstroemExpFactoryDefault)
