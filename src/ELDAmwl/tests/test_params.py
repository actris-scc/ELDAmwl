# -*- coding: utf-8 -*-
"""Tests for Signals"""


from ELDAmwl.base import Params


class ParamsA(Params):

    def __init__(self):
        super(ParamsA, self).__init__()

        self.a = 12
        self.b = 14

        self.sub_params = ['measurement_params']
        self.measurement_params = Params()
        self.measurement_params.c = 15
        self.measurement_params.d = 16

    def funcaplusb(self, a, b):
        return a+b

    @property
    def aplusb(self):
        return self.a + self.getb

    @property
    def getb(self):
        return self.b


def test_params():

    paramsA = ParamsA()

    assert paramsA.aplusb == paramsA.a + paramsA.b
    assert paramsA.funcaplusb(1, 2) == 3
    assert paramsA.measurement_params.c == 15
    assert paramsA.measurement_params.d == 16
