# -*- coding: utf-8 -*-
"""Class registry"""
import sys

from addict import Dict
from ELDAmwl.exceptions import OnlyOneOverrideAllowed
from ELDAmwl.log import logger

OVERRIDE = '__OVERRIDE__'


class FactoryRegistry(object):

    def __init__(self):
        """
        Initialize the registry with a blank dict
        """
        self.registry = Dict()

    def register_class(self, factory_name,
                       klass_name, klass, override=False):
        """
        Registers a class by name

        Args:
            factory_name: Name of the factory to register for
            klass_name: The name under which the class is registered in the db
            klass: The class to register
        """
        self.registry[klass_name] = klass
        if override:
            if OVERRIDE in self.registry:
                raise OnlyOneOverrideAllowed(factory_name)
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
        self.factory_registry = Dict()

    def get_factory_registration(self, factory):
        """
        Retrieve or create new factory entry in the registry

        Args:
            factory: The factory which is looked for

        Returns:

        """
        if factory.name not in self.factory_registry:
            self.factory_registry[factory.name] = FactoryRegistry()
        return self.factory_registry[factory.name]

    def register_class(self, factory, klass_name, klass, override=False):
        """
        Registers a class by name to the given factory

        Args:
            factory: The factory to register for
            klass_name: The name under which the class is registered in the db
            klass: The class to register

        Returns:

        """
        factory_registration = self.get_factory_registration(factory)
        factory_registration.register_class(factory.name,
                                        klass_name, klass,
                                        override=override)

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
        if factory.name in self.factory_registry:
            factory_registration = self.get_factory_registration(factory)
        else:
            return None
        return factory_registration.find_class_by_name(klass_name)

    def status(self):
        """
        Dumps the status of the registry
        Returns:

        """
        res = []
        for factory_name, reg in self.factory_registry.items():
            res.append(factory_name)
            for name, klass in reg.registry.items():
                res.append(' ' * 4 + name + ' => ' + str(klass))

        return '\n'.join(res)

registry = Registry()
