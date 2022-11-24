# -*- coding: utf-8 -*-
"""Classes for elastic backscatter calculation"""
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import NoValidDataPointsForCalibration, IntegrationFailed
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.numerical import closest_bin
from ELDAmwl.utils.numerical import integral_profile

import numpy as np
import xarray as xr


class CalcBscProfileKF(BaseOperation):
    """
    calculates elast backscatter profile with Klett-Fernald method

    uses equations and symbols from Althausen et al. JOTECH 2000
    (https://journals.ametsoc.org/view/journals/atot/17/11/1520-0426_2000_017_1469_swcal_2_0_co_2.xml)

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
                    variables 'data', 'error', 'qf', 'altitude',
                    'binres', 'mol_extinction', 'mol_bckscatter', 'assumed_particle_lidar_ratio'
                range_axis (xarray.DataArray): range axis of the elast_signal with variable 'data'
                error_params (addict.Dict):
                    with keys 'lowrange' and 'highrange' =
                        maximum allowable relative statistical error
                calibration (addict.Dict):
                    with keys 'cal_first_lev',
                    'cal_last_lev', and 'calibr_value'.
                    calibr_value is the assumed backscatter ratio at calibration level
            Returns:
                bsc (xarray.DataSet) with variables
                    'data' (particle backscatter coefficient),
                    'error' (the uncertainty contains only the uncertainty of the calibration,
                            not the uncertainty of signal noise nor uncertainty of lidar ratio estimation),
                    'qf' (same as in elast_sig),
                    'binres' (same as in elast_sig),
                    'calibration_bin' (altitude bin where the KF integration starts.
                                        backward integration below, forward integration above)

        """
        assert 'elast_sig' in kwargs
        assert 'error_params' in kwargs
        assert 'calibration' in kwargs

        # prepare
        elast_sig = kwargs['elast_sig']
        calibration = kwargs['calibration']
        error_params = kwargs['error_params']

        rayl_lr = RayleighLidarRatio()(wavelength=elast_sig.emission_wavelength).run()
        rayl_bsc = elast_sig.mol_backscatter

        if 'range_axis' in kwargs:
            range_axis = kwargs['range_axis']
        else:
            range_axis = elast_sig.altitude

        num_times = elast_sig.dims['time']

        # calculate difference profile between particle and Rayleigh lidar ratio
        lidar_ratio = elast_sig.assumed_particle_lidar_ratio
        lr_diff = lidar_ratio - rayl_lr

        # prepare empty arrays
        calibr_factor = np.ones(num_times) * np.nan
        calibr_bin = np.ones(num_times, dtype=int) * NC_FILL_INT
        calibr_factor_err = np.ones(num_times) * np.nan
        # sqr_rel_calibr_err = np.ones(times) * np.nan
        M = np.full(rayl_bsc.shape, np.nan)
        A = np.full(rayl_bsc.shape, np.nan)
        A_int = np.full(rayl_bsc.shape, np.nan)
        B = np.full(rayl_bsc.shape, np.nan)
        B_err = np.full(rayl_bsc.shape, np.nan)

        # 1) calculate calibration factor
        for t in range(num_times):
            # convert elast_sig.ds (xr.Dataset) into pd.Dataframe for easier selection of calibration window
            df_sig = elast_sig.data.isel(
                {'level': range(calibration['cal_first_lev'][t],
                                calibration['cal_last_lev'][t] + 1),
                 'time': t})\
                .to_dataframe()
            mean_sig = df_sig.data.mean()
            sem_sig = df_sig.data.sem()
            rel_sem_sig = sem_sig / mean_sig

            df_rayl = rayl_bsc.isel({'level':
                                    range(calibration['cal_first_lev'][t],
                                          calibration['cal_last_lev'][t] + 1),
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

        # 2) find signal bin which has the value closest to the mean of the calibration window
            cb = closest_bin(
                elast_sig.data[t].values,
                elast_sig.err[t].values,
                first_bin=calibration['cal_first_lev'][t],
                last_bin=calibration['cal_last_lev'][t],
                search_value=mean_sig)
            if cb is None:
                self.logger.error('cannot find altitude bin close enough to mean signal within calibration window')
                return None
            else:
                calibr_bin[t] = cb

        # 3) calculate M, A, A_int, B, and B_err
            try:
                M[t, calibr_bin[t]:] = integral_profile(rayl_bsc[t].values,
                                                        range_axis=range_axis[t].values,
                                                        first_bin=calibr_bin[t])
                M[t, :calibr_bin[t] + 1] = integral_profile(rayl_bsc[t].values,
                                                            range_axis=range_axis[t].values,
                                                            first_bin=calibr_bin[t],
                                                            last_bin=0)

                M[t, calibr_bin[t]] = 0

                A[t] = elast_sig.data[t] * np.exp(-2 * lr_diff[t] * M[t])
                A_int[t, calibr_bin[t]:] = integral_profile(A[t],
                                                            range_axis=range_axis[t].values,
                                                            first_bin=calibr_bin[t])
                A_int[t, :calibr_bin[t] + 1] = integral_profile(A[t],
                                                                range_axis=range_axis[t].values,
                                                                extrapolate_ovl_factor=1,
                                                                first_bin=calibr_bin[t],
                                                                last_bin=0)

                A_int[t, calibr_bin[t]] = 0

                B[t, :] = calibr_factor[t]
                B_err[t, :] = calibr_factor_err[t]
            except IntegrationFailed:
                return None

        # 4) calculate backscatter coefficient
        denominator = B - 2 * lidar_ratio * A_int
        bsc = xr.Dataset()
        bsc['data'] = A / denominator - rayl_bsc
        # the uncertainty contains only the uncertainty of the calibration,
        # not the uncertainty of signal noise nor uncertainty of lidar ratio estimation
        bsc['err'] = np.abs(
            (A * denominator - np.square(A)) / np.power(denominator, 3) * B_err)
        bsc['qf'] = elast_sig.qf
        bsc['binres'] = elast_sig.binres
        bsc['calibration_bin'] = xr.DataArray(calibr_bin,
                                              coords=[bsc.time],
                                              dims=['time'])
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
