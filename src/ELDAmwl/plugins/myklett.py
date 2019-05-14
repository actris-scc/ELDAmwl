from ELDAmwl.factory import Extetinction
from ELDAmwl.registry import registry

class MyKlett(object):

    def __init__(self, str):
        print('MyKlett sagt ', str)

registry.register_class(Extetinction, 'Klett algorithmus', MyKlett)
