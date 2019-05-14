from ELDAmwl.registry import registry

try:
    import configs.config as cfg
except ModuleNotFoundError:
    import configs.config_default as cfg

class BaseOperationFactory(object):
    """
    Base class of factories
    """
    name = 'BaseFactory'


    def __init__(self, *args, **kwargs):
        klass = self.get_class()
        klass(*args, **kwargs)

    def get_classname_from_db(self):
        return 'test'

    def get_class(self):
        klass_name = self.get_classname_from_db()
        klass = registry.find_class_byname(self.__class__, klass_name)
        return klass

class Extetinction(BaseOperationFactory):

    name = 'Extinction'


class BaseOperation(object):
    """
    Base class of operations
    """

class Klett(BaseOperation):
    """

    """
registry.register_class(Extetinction, 'Klett algorithmus', Klett)


class Iteration(BaseOperation):
    """

    """
registry.register_class(Extetinction, 'Iterativer algorithmus', Iteration)
