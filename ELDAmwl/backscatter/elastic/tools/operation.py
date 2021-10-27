# -*- coding: utf-8 -*-
"""Classes for elastic backscatter calculation"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory


class CalcBscProfileKF(BaseOperation):
    """calculates bsc profiles with Klett-Fernal method"""
    pass


class CalcBscProfileIter(BaseOperation):
    """calculates bsc profiles with iterative method"""
    pass


class CalcElastBscProfile(BaseOperationFactory):
    """calculates bsc profiles from signal and calibration window"""
    pass
