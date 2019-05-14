from attrdict import AttrDict


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
            self.factory_registry[factory.name] = AttrDict()
        return self.factory_registry[factory.name]

    def register_class(self, factory, klass_name, klass):
        """
        Registers a class by name to the given factory

        Args:
            factory: The factory to register for
            klass_name: The name under which the class is registered
            klass: The class to register

        Returns:

        """
        factory_registration = self.get_factory_registration(factory)
        factory_registration[klass_name] = klass

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
        if hasattr(factory_registration, klass_name):
            return factory_registration[klass_name]
        else:
            return None

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
