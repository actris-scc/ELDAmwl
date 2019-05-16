from ELDAmwl.extinction_factories import SignalSlope
from ELDAmwl.registry import registry

class SavGolaySlope(object):

    def __init__(self, str):
        print('SavGolaySlope ', str)

#registry.register_class(Extetinction, 'Klett algorithmus', MyKlett)
registry.register_class(SignalSlope, 'SavitzkyGolay', SavGolaySlope)
