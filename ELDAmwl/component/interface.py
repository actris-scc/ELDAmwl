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


class IDBConstructor(interface.Interface):
    """
    Marker Interface for global test DB creator
    """


class IMonteCarlo(interface.Interface):
    """
    Marker Interface for Monte Carlo operation
    """
    def get_data(self):
        """
        Returns the data monte carlo has to operate on.
        Usually this is a list of columns
        """
    def run(self, data):
        """
        sets the shuffled data on the operation and runs the operation
        Returns the operation result on the shuffeled data
        """

class IBscOp(interface.Interface):
    """
    Marker Interface for Backscatter operation
    """


class IExtOp(interface.Interface):
    """
    Marker Interface for Extinction operation
    """
