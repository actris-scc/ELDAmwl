from attrdict import AttrDict

from ELDAmwl.exceptions import OnlyOneOverrideAllowed

OVERRIDE = '__OVERRIDE__'


class FactoryRegistry(object):

    def __init__(self):
        """
        Initialize the registry with a blank dict
        """
        self.registry = AttrDict()

    def register_class(self, klass_name, klass, override=False):
        """
        Registers a class by name

        Args:
            factory: The factory to register for
            klass_name: The name under which the class is registered (in the db)
            klass: The class to register
        """
        self.registry[klass_name] = klass
        if override:
            if OVERRIDE in self.registry:
                raise OnlyOneOverrideAllowed
            self.registry[OVERRIDE] = klass_name

    def find_class_by_name(self, klass_name):
        """
        Retrieve a class by class name

        Args:
            klass_name: Its klass name

        Returns:
            None : if no class is registred
            Class: The registered class
            Override class: if a override class was registered

        """

        if OVERRIDE in self.registry:
            return self.registry[self.registry[OVERRIDE]]
        else:
            if klass_name in self.registry:
                return self.registry[klass_name]
            else:
                return None

class Registry(object):
    """
    Registers classes for the class factories
    """

    def __init__(self):
        """
        Initialize the registry with a blank dict
        """
        self.factory_registry = AttrDict()

    def get_factory_registration(self, factory ):
        """
        Retireve or create new factory entry in the registry

        Args:
            factory: THe factory which is looked for

        Returns:

        """
        if not hasattr(self.factory_registry,  factory.name):
            self.factory_registry[factory.name] = FactoryRegistry()
        return self.factory_registry[factory.name]

    def register_class(self, factory, klass_name, klass, override=False):
        """
        Registers a class by name to the given factory

        Args:
            factory: The factory to register for
            klass_name: The name under which the class is registered (in the db)
            klass: The class to register

        Returns:

        """
        factory_registration = self.get_factory_registration(factory)
        factory_registration.register_class(klass_name, klass, override=override)


    def find_class_by_name(self, factory, klass_name):
        """
        Retrieve a class for a given factory and class name

        Args:
            factory: The factory the class is for
            klass_name: Its klass name

        Returns:
            None : if no class is registred
            Class: The registered class

        """
        if hasattr(self.factory_registry, factory.name):
            factory_registration = self.get_factory_registration(factory)
        else:
            return None
        return factory_registration.find_class_by_name(klass_name)

    def status(self):
        """
        Dumps the status of the registry
        Returns:

        """
        for factory_name, reg in self.factory_registry.items():
            print(factory_name)
            for name, klass in reg.items():
                print(' ' * 4, name, ' => ', klass)

    def update(self, other):
        """
        merge two registries

        Args:
            other: the other registry

        Returns:

        """
        for factory_name, reg in self.factory_registry.items():
            if not hasattr(self.factory_registry, factory_name):
                self.factory_registry[factory_name] = reg
                continue
            for klass_name, klass in reg.items():
                self.factory_registry[factory_name][klass_name] = klass

registry = Registry()
