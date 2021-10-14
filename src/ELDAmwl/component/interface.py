"""Interfaces for the components"""

from zope import interface


class IDBFunc(interface.Interface):
    """
    Marker Interface for DBFunc utility
    """


class ILogger(interface.Interface):
    """
    Marker Interface for logger utility
    """


class IDataStorage(interface.Interface):
    """
    Marker Interface for global data storage
    """
