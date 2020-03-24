# -*- coding: utf-8 -*-
"""Classes for extinction calculation"""

from ELDAmwl.database.db_functions import read_extinction_algorithm
from ELDAmwl.factory import BaseOperation
from ELDAmwl.factory import BaseOperationFactory
from ELDAmwl.products import ProductParams
from ELDAmwl.products import Products
from ELDAmwl.registry import registry


class ExtinctionParams(ProductParams):

    @classmethod
    def from_db(cls, general_params):
        result = cls()
        result.general_params = general_params
        # extinction_params.from_db()
        return result


class Extinctions(Products):
    """
    time series of extinction profiles
    """
    pass


class SlopeToExtinction(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which calculates the particle
    extinction coefficient from signal slope. In this case, it
    will be always an instance of getSlopeToExtinction().
    """

    name = 'SlopeToExtinction'

    def get_classname_from_db(self):
        """

        return: always 'getSlopeToExtinction' .
        """
        return 'getSlopeToExtinction'


class getSlopeToExtinction(BaseOperation):
    """
    Calculates particle extinction coefficient from signal slope.
    """
    # WFA := 1.0 + power((DetectionWL / EmissionWL),
    #                    ( Params as TExtParams).WL_Dep);
    # WFAinv := 1/WFA;
    #
    # for bin := firstBin to lastBin do
    # if valid[bin] then
    #   begin
    #   Data[bin] := Data[bin] * WFAinv ;
    #   Err[bin] := Err[bin] * WFAinv ;
    #   end;


registry.register_class(SlopeToExtinction, 'getSlopeToExtinction',
                        getSlopeToExtinction)


class Extinction(BaseOperationFactory):
    """

    """

    name = 'Extinction'


class getExtinction(BaseOperation):
    """
    derives particle extinction coefficient.
    """

    def get_product(self):
        slope = SignalSlope()
        ext = SlopeToExtinction(slope)
        result = ext
        return result


registry.register_class(Extinction, 'getExtinction', getExtinction)


class SignalSlope(BaseOperationFactory):
    """
    Calculates signal slope.
    """

    name = 'SignalSlope'

    def get_classname_from_db(self):
        return read_extinction_algorithm(281)


class LinFit(BaseOperation):
    """

    """
    name = 'LinFit'

    def __init__(self, weight):
        super(LinFit, self).__init__()
        # print('calculate linear fit with weight', weight)


class WeightedLinFit(BaseOperation):
    """

    """
    def __init__(self, str):
        super(WeightedLinFit, self).__init__()
        # print('WeightedLinFit sagt ', str)
        LinFit(True)


registry.register_class(SignalSlope, 'WeightedLinearFit', WeightedLinFit)


class NonWeightedLinFit(BaseOperation):
    """

    """

    def __init__(self, str):
        super(NonWeightedLinFit, self).__init__()
        # print('NonWeightedLinFit sagt ', str)
        LinFit(False)


registry.register_class(SignalSlope, 'NonWeightedLinearFit', NonWeightedLinFit)
