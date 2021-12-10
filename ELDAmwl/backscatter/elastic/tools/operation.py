# -*- coding: utf-8 -*-
"""Classes for elastic backscatter calculation"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.errors.exceptions import NoValidDataPointsForCalibration
from ELDAmwl.utils.constants import RAYL_LR, NC_FILL_INT
from ELDAmwl.component.registry import registry

import numpy as np
import xarray as xr

from ELDAmwl.utils.numerical import closest_bin, integral_profile


class CalcBscProfileKF(BaseOperation):
    """calculates elast backscatter profile with Klett-Fernald method

    uses equations and symbols from Althausen et al. JOTECH 2000
    (https://doi.org/10.1175/1520-0426(2000)017<1469:SWCAL>2.0.CO;2)

    bsc_part(r) = A(r) / [B - 2S * A_int ] - bsc_mol(r)

    M(r) = Int_Rref^r{bsc_mol(R)dR}
    A(r) = sig(r) * exp{-2(S_par-S_mol) * M(r)}
    A_int(r) = Int_Rref^r{A(R)dR}
    B = sig(r_ref) / [bsc_part(r_ref) + bsc_mol(r_ref)]

    S: lidar ratio
    sig: range corrected signal
    r_ref / Rref: calibration altitude
    r / R: range

    """

    name = 'CalcBscProfileKF'
    elast_sig = None
    rayl_scat = None
    range_axis = None
    error_params = None
    calibration = None

    def run(self, **kwargs):
        """calculates elast backscatter profile with Klett-Fernald method

            Keyword Args:
                elast_sig (xarray.DataSet):
                    already smoothed elastic signal with \
                    variables 'data', 'error', 'qf',
                    'binres', 'mol_extinction', 'assumed_particle_lidar_ratio'
                error_params (addict.Dict):
                    with keys 'lowrange' and 'highrange' =
                        maximum allowable relative statistical error
                calibration (addict.Dict):
                    with keys 'cal_first_lev',
                    'cal_last_lev', and 'calibr_value'. calibr_value is the assumed backscatter ratio at calibration level
        """
        assert 'elast_sig' in kwargs
        assert 'error_params' in kwargs
        assert 'calibration' in kwargs

        # prepare
        elast_sig = kwargs['elast_sig']
        calibration = kwargs['calibration']
        error_params = kwargs['error_params']

        if 'range_axis' in kwargs:
            range_axis = kwargs['range_axis']
        else:
            range_axis = elast_sig.altitude

        rayl_bsc = elast_sig.mol_extinction / RAYL_LR
        rayl_bsc.name = 'mol_backscatter'
        lidar_ratio = elast_sig.assumed_particle_lidar_ratio

        times = elast_sig.dims['time']
        calibr_factor = np.ones(times) * np.nan
        # calibr_bin = np.ones(times, dtype=int) * NC_FILL_INT
        calibr_factor_err = np.ones(times) * np.nan
        # sqr_rel_calibr_err = np.ones(times) * np.nan
        M = np.full(rayl_bsc.shape, np.nan)
        A_int = np.full(rayl_bsc.shape, np.nan)
        lr_diff = lidar_ratio- RAYL_LR

        # 1) calculate calibration factor
        for t in range(times):
            # convert elast_sig.ds (xr.Dataset) into pd.Dataframe for easier selection of calibration window
            df_sig = elast_sig.data.isel({'level':
                                    range(calibration['cal_first_lev'][t],
                                          calibration['cal_last_lev'][t]),
                                     'time': t})\
                .to_dataframe()
            mean_sig = df_sig.data.mean()
            sem_sig = df_sig.data.sem()
            rel_sem_sig = sem_sig / mean_sig

            df_rayl = rayl_bsc.isel({'level':
                                    range(calibration['cal_first_lev'][t],
                                          calibration['cal_last_lev'][t]),
                                     'time': t})\
                .to_dataframe()
            mean_rayl_bsc = df_rayl.mol_backscatter.mean()
            # assume that rayleigh backscatter has no uncertainty

            if rel_sem_sig > error_params.err_threshold.highrange:
                self.logger.error('relative error of signal in calibration window is larger than error threshold')
                raise NoValidDataPointsForCalibration

            else:
                calibr_factor[t] = mean_sig / mean_rayl_bsc / calibration.calibr_value.value
                calibr_factor_err[t] = calibr_factor[t] * \
                    np.sqrt(np.square(rel_sem_sig) + np.square(calibration.calibr_value.rel_error))
                # sqr_rel_calibr_err[t] = np.square(calibr_factor_err[t] / calibr_factor[t])
        #
        # cf = xr.DataArray(calibr_factor,
        #                   dims=['time'],
        #                   coords=[sigratio.time])
        # sqr_cf_err = xr.DataArray(sqr_rel_calibr_err,
        #                           dims=['time'],
        #                           coords=[sigratio.time])
        #
        # 2) find signal bin which has the value closest to the mean of the calibration window
            calibr_bin = closest_bin(elast_sig.data[t].values,
                                     elast_sig.err[t].values,
                                     first_bin=calibration['cal_first_lev'][t],
                                     last_bin=calibration['cal_last_lev'][t],
                                     search_value=mean_sig)

            if calibr_bin is None:
                self.logger.error('cannot find altitude bin close enough to mean signal within calibration window')
                raise NoValidDataPointsForCalibration

        # 3) calculate M, A, and B

            M[t, calibr_bin:] = integral_profile(rayl_bsc[t],
                                                 range=range_axis[t],
                                                 first_bin=calibr_bin)
            M[t, :calibr_bin + 1] = integral_profile(rayl_bsc[t],
                                                     range=range_axis[t],
                                                 first_bin=calibr_bin,
                                                 last_bin=0)

            A = elast_sig.data[t] * np.exp(-2 * lr_diff[t] * M[t])
            A_int[t, calibr_bin:] = integral_profile(A,
                                                     range=range_axis[t],
                                                 # quality_flag=elast_sig.qf,
                                                 # use_flags=[],
                                                 #extrapolate_ovl_factor=1,
                                                 first_bin=calibr_bin)
            A_int[t, :calibr_bin + 1] = integral_profile(A,
                                                         range=range_axis[t],
                                                 # quality_flag=elast_sig.qf,
                                                 # use_flags=[],
                                                 extrapolate_ovl_factor=1,
                                                 first_bin=calibr_bin,
                                                 last_bin=0)

        B = elast_sig.data[t, calibr_bin] / ( + rayl_bsc[t, calibr_bin])

        # # 2) calculate backscatter ratio
        bsc = xr.Dataset()
        # bsc['data'] = sigratio.data * cf
        # bsc['err'] = bsc.data * np.sqrt(np.square(sigratio.err / sigratio.data) + sqr_cf_err)
        #
        # # 3) calculate backscatter coefficient
        # bsc['data'] = (bsc.data - 1.) * rayl_bsc
        # bsc['err'] = abs(bsc.err * rayl_bsc)
        #
        # bsc['qf'] = sigratio.qf
        # bsc['binres'] = sigratio.binres

        return bsc

class CalcBscProfileIter(BaseOperation):
    """calculates bsc profiles with iterative method"""
    pass


class CalcElastBscProfile(BaseOperationFactory):
    """
    creates a class for the calculation of an elastic backscatter coefficient profile

    Returns an instance of BaseOperation which calculates the profile of the particle
    backscatter coefficient from an elastic signal.

    Keyword Args:
        prod_id (str): id of the product

    Returns:
        instance of :class:`ELDAmwl.bases.factory.BaseOperation`

    """
    def __call__(self, **kwargs):
        assert 'prod_id' in kwargs
        self.prod_id = kwargs['prod_id']
        res = super(CalcElastBscProfile, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """ reads from SCC db which algorithm to use for elastic bsc calculation

        Returns: name of the class for the bsc calculation
        """
        return self.db_func.read_elast_bsc_algorithm(self.prod_id)

    pass


registry.register_class(CalcElastBscProfile,
                        CalcBscProfileKF.__name__,
                        CalcBscProfileKF)

registry.register_class(CalcElastBscProfile,
                        CalcBscProfileIter.__name__,
                        CalcBscProfileIter)
