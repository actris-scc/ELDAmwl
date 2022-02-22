from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoValidDataPointsForCalibration
from ELDAmwl.utils.constants import NC_FILL_STR
from ELDAmwl.utils.constants import RAYL_LR

from copy import deepcopy
import numpy as np
import xarray as xr


class CalcRamanBscProfileViaBR(BaseOperation):
    """calculates Raman backscatter profile via BR"""

    name = 'CalcRamanBscProfileViaBR'
    sigratio = None
    error_params = None
    calibration = None

    def run(self, **kwargs):
        """calculates Raman bsc profile from elast and Raman signals
        and calibration window.

            Keyword Args:
                sigratio (xarray.DataSet):
                    already smoothed signal ratio with \
                    variables 'data', 'error', 'qf',
                    'binres', 'mol_extinction'
                error_params (addict.Dict):
                    with keys 'lowrange' and 'highrange' =
                        maximum allowable relative statistical error
                calibration (addict.Dict):
                    with keys 'cal_first_lev',
                    'cal_last_lev', and 'calibr_value'

            Returns:
                Raman backscatter profile (xarray.DataSet) with calculated variables
                'data' and 'error'. all other variables and attibutes are copied from from sigratio
        """
        assert 'sigratio' in kwargs
        assert 'error_params' in kwargs
        assert 'calibration' in kwargs

        sigratio = kwargs['sigratio']
        calibration = kwargs['calibration']
        error_params = kwargs['error_params']
        rayl_bsc = sigratio.mol_extinction / RAYL_LR
        # todo: make BaseOperation for RAYL_LR

        # 1) calculate calibration factor

        times = sigratio.dims['time']
        calibr_factor = np.ones(times) * np.nan
        calibr_factor_err = np.ones(times) * np.nan
        sqr_rel_calibr_err = np.ones(times) * np.nan

        for t in range(times):
            df = sigratio.data.isel({'level':
                                    range(calibration['cal_first_lev'][t],
                                          calibration['cal_last_lev'][t]),
                                     'time': t})\
                .to_dataframe()
            mean = df.data.mean()
            sem = df.data.sem()
            rel_sem = sem / mean

            if rel_sem > error_params.err_threshold.highrange:
                raise NoValidDataPointsForCalibration

            else:
                calibr_factor[t] = calibration.calibr_value.value / mean
                calibr_factor_err[t] = calibr_factor[t] * \
                    np.sqrt(np.square(rel_sem) + np.square(calibration.calibr_value.rel_error))
                sqr_rel_calibr_err[t] = np.square(calibr_factor_err[t] / calibr_factor[t])

        cf = xr.DataArray(calibr_factor,
                          dims=['time'],
                          coords=[sigratio.time])
        sqr_cf_err = xr.DataArray(sqr_rel_calibr_err,
                                  dims=['time'],
                                  coords=[sigratio.time])

        # 2) calculate backscatter ratio
        bsc = deepcopy(sigratio)
        bsc['data'] = sigratio.data * cf
        bsc['err'] = bsc.data * np.sqrt(np.square(sigratio.err / sigratio.data) + sqr_cf_err)

        # 3) calculate backscatter coefficient
        bsc['data'] = (bsc.data - 1.) * rayl_bsc
        bsc['err'] = abs(bsc.err * rayl_bsc)

        return bsc


class CalcRamanBscProfile(BaseOperationFactory):
    """calculates Raman bsc profile from elast
    and Raman signals and calibration window

        Keyword Args:
            prod_id (str): id of the product
    """

    name = 'CalcRamanBscProfile'
    prod_id = NC_FILL_STR

    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(CalcRamanBscProfile, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for Raman bsc calculation

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_raman_bsc_algorithm(self.prod_id)

    pass


# class CalcRamanBscProfileAsAnsmann(BaseOperation):
#     """calculates Raman backscatter profile like in ansmann et al 1992"""
#
#     name = 'CalcRamanBscProfileAsAnsmann'
#
#     def run(self, **kwargs):
#         raise UseCaseNotImplemented('CalcRamanBscProfileAsAnsmann',
#                                     'Raman Backscatter',
#                                     'viaBR (id = 1)')
#
registry.register_class(CalcRamanBscProfile,
                        CalcRamanBscProfileViaBR.__name__,
                        CalcRamanBscProfileViaBR)
