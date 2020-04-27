# -*- coding: utf-8 -*-
"""Classes for Rayleigh calculations"""
from ELDAmwl.constants import RAYL_LR
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.registry import registry


class RayleighLidarRatio(BaseOperationFactory):
    """
    Creates class for calculation of Rayleigh lidar ratio

    Keyword Args:
        wavelength (float): emission wavelength of the signal
    """

    name = 'RayleighLidarRatio'

    def __call__(self, **kwargs):
        assert 'wavelength' in kwargs

        res = super(RayleighLidarRatio, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ class name for the calculation of Rayleigh lidar ratio.

        returns always 'RayleighLidarRatioFromConst'
        """
        return RayleighLidarRatioFromConst.__name__


class RayleighLidarRatioFromConst(BaseOperation):

    name = 'RayleighLidarRatioFromConst'
    def run(self):
        return RAYL_LR


registry.register_class(RayleighLidarRatio,
                        RayleighLidarRatioFromConst.__name__,
                        RayleighLidarRatioFromConst)
