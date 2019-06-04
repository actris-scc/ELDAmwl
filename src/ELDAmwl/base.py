"""Base classes of the Operator and the Operator factory

.. moduleauthor:: Volker Jaenisch <volker.jaenisch@inqbus.de>

"""

class Params(object):
    """
    Base Params
    """
    sub_params = None

    def __init__(self):
        sub_params = []

    def __getattribute__(self, item):
        for sp_name in self.sub_params:
            sp = getattr(self, sp_name)
            try:
                return getattr(sp, item)
            except AttributeError:
                continue

        raise(AttributeError('class %s has no attribute %s' % (self.__class__.__name__, item)))


# class _Operator(object):
#     """
#     Base Operator
#     """
#
#     def __init__(self):
#         """
#         Initialize the params, input and result storage
#         """
#         self._params = None
#         self._input = None
#         self._result = {}
#         """
#         The input data
#
#         :getter: Returns input data
#         :setter: Sets input data
#         """
#
#     @property
#     def input(self):
#         """
#
#         Returns:
#
#         """
#         return self._input
#
#     @input.setter
#     def input(self, value):
#         """
#         :param value: Input data. Usually a dictionary
#         """
#         self._input = value
#
#     @property
#     def params(self):
#         """
#         Return the params
#         :returns: The params
#         """
#         return self._params
#
#     @params.setter
#     def params(self, value):
#         """
#         Set the params
#         :param value: The params. Usually a dict
#         """
#         self._params = value
#
#     @property
#     def result(self):
#         """
#         Return the result
#         :returns: The result
#         """
#         return self._result
#
#     def run(self):
#         """
#         Start the processing of the Operator
#         :return: Error code of the Operator
#         """
#         return self.operate()
#
#     def operate(self):
#         """
#         The operation that is performed
#         :return: THe error code of the operation
#         """
#         return None
#
#
# class Operator(object):
#     """
#     Factory for Operators
#     """
#
#     # The dummy class of the produced instances. In this case an _Operator
#     # instance
#     _class = _Operator
#
#     def __init__(self, params, input):
#         """
#         Construct a factory
#
#         Args:
#             params: The params
#             input:  The input data
#         """
#         self.input = input
#         self.params = params
#
#     def get_class(self):
#         """
#         Find the class to use for object creation
#         :return: The desired class. To be overwritten
#         """
#         return self._class
#
#     def __call__(self):
#         """
#         Construct the object instance
#
#         returns:
#             The object
#         """
#         op = self.get_class()()
#         op.input = self.input
#         op.params = self.params
#         return op
