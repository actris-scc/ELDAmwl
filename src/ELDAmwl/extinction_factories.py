from ELDAmwl.base import Params
from ELDAmwl.registry import registry
from ELDAmwl.factory import BaseOperationFactory, BaseOperation
from ELDAmwl.products import Products
from ELDAmwl.log import logger
from ELDAmwl.database.db_functions import read_extinction_algorithm


class ExtinctionParams(Params):

    def __init__(self):
        self.sub_params = ['general_params',
                            'extinction_params']
        self.general_params = None
        self.extinction_params = None

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
    Calculates particle extinction coefficient from signal slope.
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

    # WFA := 1.0 + power((DetectionWL / EmissionWL),( Params as TExtParams).WL_Dep);
    # WFAinv := 1/WFA;
    #
    # for bin := firstBin to lastBin do
    # if valid[bin] then
    #   begin
    #   Data[bin] := Data[bin] * WFAinv ;
    #   Err[bin] := Err[bin] * WFAinv ;
    #   end;

registry.register_class(SlopeToExtinction, 'getSlopeToExtinction', getSlopeToExtinction)


class Extinction(BaseOperationFactory):
    """

    """

    name = 'Extinction'

class getExtinction(BaseOperation):
    """
    derives particle extinction coefficient.
    """

    def __init__(self):
        pass

    def get_product(self):
        slope = SignalSlope()
        ext = SlopeToExtinction(slope)
        result = ext

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
        print('calculate fit with weight', weight)


class WeightedLinFit(BaseOperation):
    """

    """
    def __init__(self, str):
        print('WeightedLinFit sagt ', str)
        LinFit(True)


registry.register_class(SignalSlope, 'WeightedLinearFit', WeightedLinFit)


class NonWeightedLinFit(BaseOperation):
    """

    """

    def __init__(self, str):
        print('NonWeightedLinFit sagt ', str)
        LinFit(False)


registry.register_class(SignalSlope, 'NonWeightedLinearFit', NonWeightedLinFit)
