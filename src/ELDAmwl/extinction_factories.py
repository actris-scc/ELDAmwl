from ELDAmwl.registry import registry
from ELDAmwl.database.db_functions import read_extinction_algorithm
from ELDAmwl.factory import BaseOperationFactory, BaseOperation


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
