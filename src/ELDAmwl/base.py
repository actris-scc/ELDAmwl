# -*- coding: utf-8 -*-
"""Base classes of the Operator and the Operator factory

.. moduleauthor:: Volker Jaenisch <volker.jaenisch@inqbus.de>

"""


class Params(object):
    """
    Base Params
    """
    sub_params = None

    def __init__(self):
        self.sub_params = []

    def __getattribute__(self, item):
        try:
            return object.__getattribute__(self, item)
        except AttributeError:
            for sp_name in object.__getattribute__(self, 'sub_params'):
                sp = object.__getattribute__(self, sp_name)
                try:
                    return object.__getattribute__(sp, item)
                except AttributeError:
                    continue

            class_name = object.__getattribute__(sp, '__class__').__name__
            raise(AttributeError('class {0} has no attribute {1}'.format(class_name, item)))  # noqa E501


