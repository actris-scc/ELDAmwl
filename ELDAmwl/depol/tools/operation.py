from copy import deepcopy

import numpy as np

from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from numpy import square as sqr


class CalcVldrVFreudenthaler22(BaseOperation):
    """calculates VLDR profiles with the algorithm described by Volker Freudenthaler 2022"""

    name = 'CalcVldrVFreudenthaler22'
    sigratio = None
    depol_params = None

    def run(self, **kwargs):
        """calculates VLDR profile from reflected and transmitted signals.

            Keyword Args:
                sigratio (xarray.DataSet):
                    already smoothed signal ratio with \
                    variables 'data', 'error', 'qf',
                    'binres', 'molecular_depolarization_ratio', and others
                depol_params (addict.Dict):
                    with keys 'gain_ratio', 'gain_ratio_correction', 'HT', 'HR', 'GT', 'GR',
                        'sys_err_lower_bound_a', 'sys_err_lower_bound_b', 'sys_err_lower_bound_c',
                        'sys_err_upper_bound_a', 'sys_err_upper_bound_b', 'sys_err_upper_bound_c'


            Returns:
                VLDR profile (xarray.DataSet) with calculated variables
                'data' and 'error', 'sys_err_neg', 'sys_err_pos'.
                all other variables and attibutes are copied from from sigratio
        """
        assert 'sigratio' in kwargs
        assert 'depol_params' in kwargs

        sigratio = kwargs['sigratio']
        depol_params = kwargs['depol_params']

        # 1) calculate calibrated signal ratio

        calibr_factor = depol_params.gain_ratio_correction / depol_params.gain_ratio

        calibrated_sigratio = sigratio.data * calibr_factor
        calibrated_sigratio_err = sigratio.err * calibr_factor

        # 2) calculate volume depolarization ratio
        a = depol_params.GT + depol_params.HT
        b = depol_params.GR + depol_params.HR
        c = depol_params.GR - depol_params.HR
        d = depol_params.GT - depol_params.HT

        vldr_data = (calibrated_sigratio * a - b) / (c - calibrated_sigratio * d)

        vldr_data_sqr = sqr(vldr_data)

        vldr = deepcopy(sigratio)
        vldr['data'] = vldr_data

        vldr['err'] = np.absolute(
            (calibrated_sigratio * a * (1 - d) - b * d + a * c) / sqr(c - d * calibrated_sigratio)
            * calibrated_sigratio_err)

        # 3) calculate systematic errors
        vldr['sys_err_neg'] = depol_params.sys_err_lower_bound_a \
                              + depol_params.sys_err_lower_bound_b * vldr_data \
                              + depol_params.sys_err_lower_bound_c * vldr_data_sqr
        vldr['sys_err_pos'] = depol_params.sys_err_upper_bound_a \
                              + depol_params.sys_err_upper_bound_b * vldr_data \
                              + depol_params.sys_err_upper_bound_c * vldr_data_sqr

        return vldr

class CalcVLDRProfile(BaseOperationFactory):
    """calculates volume linear depolarization ratio profile
    from reflected and transmitted signal

        Keyword Args:
            prod_id (str): id of the product
    """

    name = 'CalcVLDRProfile'
    prod_id = None

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(CalcVLDRProfile, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for Raman bsc calculation

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_vldr_algorithm(self.prod_id)


registry.register_class(CalcVLDRProfile,
                        CalcVldrVFreudenthaler22.__name__,
                        CalcVldrVFreudenthaler22)
