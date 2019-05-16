from ELDAmwl.registry import registry

try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg

class BaseOperationFactory(object):
    """
    Base class of factories.

    Base class of factories, returns an instance of a BaseOperation.
    If several alternative BaseOperation classes are available, this factory decides, which one to provide.
    This decision is based on options in the database or whether user defined plugins are available.

    If arguments or keywords are provided, they are automatically passed to the BaseOperation instance.
    """
    name = 'BaseFactory'

    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        klass = self.get_class()
        klass(*args, **kwargs)
        return klass

    def get_classname_from_db(self):
        pass

    def get_class(self):
        klass_name = self.get_classname_from_db()
        klass = registry.find_class_by_name(self.__class__, klass_name)
        return klass

class BaseOperation(object):
    """
    Base class of operations
    """

