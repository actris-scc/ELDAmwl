# -*- coding: utf-8 -*-
"""Classes for signals"""

from copy import deepcopy
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.bases.columns import Columns
from ELDAmwl.utils.constants import ALL_OK, RESOLUTION_STR, ALL_RANGE
from ELDAmwl.utils.constants import ANALOG
from ELDAmwl.utils.constants import CROSS
from ELDAmwl.utils.constants import FAR_RANGE
from ELDAmwl.utils.constants import NC_FILL_BYTE
from ELDAmwl.utils.constants import NEAR_RANGE
from ELDAmwl.utils.constants import PARALLEL
from ELDAmwl.utils.constants import PARTICLE
from ELDAmwl.utils.constants import REFLECTED
from ELDAmwl.utils.constants import TOTAL
from ELDAmwl.utils.constants import TRANSMITTED
from ELDAmwl.utils.constants import WATER_VAPOR
from ELDAmwl.errors.exceptions import ELPPFileNotFound, CannotOpenELLPFile
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.header import Header
from ELDAmwl.component.registry import registry

import numpy as np
import os
import xarray as xr


try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg


class ElppData(object):
    """Representation of one ELPP file.

    """

    def __init__(self):
        self.signals = None
        self.cloud_mask = None
        self.header = None

    def read_nc_file(self, data_storage, p_param):
        """ reading an ELPP file

        Signals, cloud mask, and the header are read
        from an ELPP file and put into the data_storage

        Args:
            data_storage (:obj:`DataStorage`): global data storage instance
            p_param:

        """
        # todo: check if scc version in query = current version

        elpp_file = os.path.join(cfg.SIGNAL_PATH,
                                 p_param.general_params.elpp_file)
        if not os.path.exists(elpp_file):
            raise(ELPPFileNotFound(elpp_file))

        try:
            nc_ds = xr.open_dataset(elpp_file)
        except Exception as e:   # ToDo Ina debug
            print(e)
            raise(CannotOpenELLPFile(elpp_file))

        self.cloud_mask = nc_ds.cloud_mask.astype(int)
        data_storage.cloud_mask = self.cloud_mask

        self.header = Header.from_nc_file(elpp_file, nc_ds)
        data_storage.header = self.header

        for idx in range(nc_ds.dims['channel']):
            sig = Signals.from_nc_file(nc_ds, idx)
            sig.ds.load()
            data_storage.set_elpp_signal(p_param.prod_id_str, sig)  # noqa E501
            sig.register(p_param)

        nc_ds.close()


class DepolarizationCalibration(object):
    gain_factor = None
    gain_factor_correction = None

    @classmethod
    def from_nc_file(cls, nc_ds, pol_cal_idx):
        result = cls
        result.gain_factor = \
            DataPoint.from_nc_file(nc_ds,
                                   'polarization_gain_factor',
                                   pol_cal_idx)

        result.gain_factor_correction = \
            DataPoint.from_nc_file(nc_ds,
                                   'polarization_gain_factor_correction',
                                   pol_cal_idx)
        # todo: how to handle the following info? are they needed?
        # polarization_gain_factor_measurementid
        # polarization_gain_factor_correction_start_datetime
        # seconds since 1970-01-01T00:00:00Z
        # polarization_gain_factor_correction_stop_datetime
        # polarization_gain_factor_correction_start_datetime
        # polarization_gain_factor_correction_stop_datetime
        return result


class Signals(Columns):
    """two-dimensional (time, level) signal data

    """

    emission_wavelength = np.nan
    detection_wavelength = np.nan
    channel_id = None
    detection_type = np.nan
    channel_idx_in_ncfile = np.nan
    scatterer = None
    alt_range = None
    pol_channel_conf = None
    scale_factor_shots = None
    pol_calibr = None
    raw_heightres = np.nan
    station_altitude = None

    calc_eff_bin_res_routine = None
    calc_used_bin_res_routine = None

    h = None
    g = None
    pol_channel_geometry = None

    @property
    def name(self):
        return hex(id(self))

    @classmethod
    def as_sig_ratio(cls, enumerator, denominator):
        """creates a Signals instance from the ratio of two Signals

        Args:
            enumerator (:class:`Signals`): nominator
            denominator (:class:`Signals`): denominator

        Returns: Signals

        """
        result = deepcopy(enumerator)

        result.ds['data'] = enumerator.ds.data / denominator.ds.data
        result.ds['err'] = result.ds.data * \
            np.sqrt(np.square(enumerator.rel_err) +
                    np.square(denominator.rel_err))
        result.ds['qf'] = enumerator.ds.qf | denominator.ds.qf

        result.channel_id = xr.concat([enumerator.channel_id,
                                       denominator.channel_id],
                                      dim='nc')

        # todo: combine other attributes, e.g. detection type etc.

        return result

    @classmethod
    def from_nc_file(cls, nc_ds, idx_in_file):
        """creates a Signals instance from the content of a NetCDF file

        Args:
            nc_ds (xarray.Dataset): content of the NetCDF file.
            idx_in_file (int):      index of the signal within the
                                    channel dimension of the file.

        Returns: Signals

        """
        result = cls()

        result.channel_idx_in_ncfile = idx_in_file
        result.num_scan_angles = nc_ds.dims['angle']

        result.ds = nc_ds.range_corrected_signal[idx_in_file].to_dataset(name='data')  # noqa E501
        result.ds['err'] = nc_ds.range_corrected_signal_statistical_error[idx_in_file]  # noqa E501

        # initiate bin resolution with value 1
        result.ds['binres'] = xr.DataArray(np.ones((nc_ds.dims['time'],
                                                 nc_ds.dims['level'])).astype(np.int),  # noqa E501
                                       coords=[nc_ds.time, nc_ds.level],
                                       dims=['time', 'level'])
        result.ds['binres'].attrs = {'long_name': 'vertical resolution',
                                     'units': 'bins',
                                     }

        # initiate quality flag with values 'ALL_OK'
        result.ds['qf'] = xr.DataArray(np.ones((nc_ds.dims['time'],
                                                 nc_ds.dims['level'])).astype(np.int8)  # noqa E501
                                       * ALL_OK,
                                       coords=[nc_ds.time, nc_ds.level],
                                       dims=['time', 'level'])
        result.ds['qf'].attrs = {'long_name': 'quality_flag',
                                 'flag_meanings': 'data_ok '
                                        'negative_data '
                                        'incomplete_overlap_not_correctable '
                                        'above_max_altitude_range '
                                        'cloud_contamination '
                                        'above_Klett_reference_height '
                                        'depol_ratio_larger_100% '
                                        'backscatter_ratio_below_required_min_value',  # noqa E501
                                 'flag_masks': [0, 1, 2, 4, 8, 16, 32, 64],
                                 'valid_range': [0, 107],
                                 'units': '1',
                                 '_FillValue': NC_FILL_BYTE,
                                 }

        result.station_altitude = nc_ds.station_altitude
        result.station_altitude.load()

        result.ds['altitude'] = nc_ds.altitude

        result.ds['time_bounds'] = nc_ds.time_bounds

        laser_pointing_angle_of_profiles = nc_ds.laser_pointing_angle_of_profiles  # noqa E501

        laser_pointing_angle = nc_ds.laser_pointing_angle
        result.ds['laser_pointing_angle'] = result.angle_to_time_dependent_var(
            laser_pointing_angle_of_profiles,
            laser_pointing_angle)

        result.ds['mol_extinction'] = nc_ds.molecular_extinction[idx_in_file]  # noqa E501
#        atmospheric_molecular_extinction = nc_ds.atmospheric_molecular_extinction[idx_in_file]  # noqa E501
#        result.ds['mol_extinction'] = result.angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
#                                                                         atmospheric_molecular_extinction)  # noqa E501

        result.ds['mol_lidar_ratio'] = nc_ds.molecular_lidar_ratio[idx_in_file]  # noqa E501
#        result.ds['mol_lidar_ratio'] = nc_ds.atmospheric_molecular_lidar_ratio[idx_in_file]  # noqa E501

        result.ds['mol_trasm_at_detection_wl'] = nc_ds.molecular_transmissivity_at_detection_wavelength[idx_in_file]  # noqa E501
#        mol_trasm_at_detection_wl = nc_ds.atmospheric_molecular_trasmissivity_at_detection_wavelength[idx_in_file]  # noqa E501
#        result.ds['mol_trasm_at_detection_wl'] = result.angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
#                                                                                    mol_trasm_at_detection_wl)  # noqa E501

        result.ds['mol_trasm_at_emission_wl'] = nc_ds.molecular_transmissivity_at_emission_wavelength[idx_in_file]  # noqa E501
#        mol_trasm_at_emission_wl = nc_ds.atmospheric_molecular_trasmissivity_at_emission_wavelength[idx_in_file]  # noqa E501
#        result.ds['mol_trasm_at_emission_wl'] = result.angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
#                                                                                   mol_trasm_at_emission_wl)  # noqa E501

        result.channel_id = nc_ds.range_corrected_signal_channel_id[idx_in_file].astype(int)  # noqa E501
        result.detection_type = nc_ds.range_corrected_signal_detection_mode[idx_in_file].astype(int)  # noqa E501
        result.detection_wavelength = nc_ds.range_corrected_signal_detection_wavelength[idx_in_file]  # noqa E501
        result.detection_wavelength.load()
        result.emission_wavelength = nc_ds.range_corrected_signal_emission_wavelength[idx_in_file]  # noqa E501
        result.emission_wavelength.load()
        result.scatterer = nc_ds.range_corrected_signal_scatterers[idx_in_file].astype(int)  # noqa E501
        result.alt_range = nc_ds.range_corrected_signal_range[idx_in_file].astype(int)  # noqa E501

        if result.detection_type != ANALOG:
            # if the detection mode is PH_CNT or GLUED
            result.scale_factor_shots = 1 / nc_ds.shots
        else:
            # if the detection mode is ANALOG
            result.scale_factor_shots = xr.DataArray(np.ones(nc_ds.dims['time']), # noqa E501
                                                     coords=[nc_ds.time],
                                                     dims=['time'])
        result.scale_factor_shots.name = 'scale_factor_shots'

        result.pol_channel_conf = nc_ds.polarization_channel_configuration[idx_in_file].astype(int)  # noqa E501
        result.pol_channel_geometry = nc_ds.polarization_channel_geometry[idx_in_file].astype(int)  # noqa E501

        result.g = DataPoint.from_nc_file(nc_ds,
                                          'polarization_crosstalk_parameter_g',
                                          idx_in_file)
        result.h = DataPoint.from_nc_file(nc_ds,
                                          'polarization_crosstalk_parameter_h',
                                          idx_in_file)

        if 'depolarization_calibration_index' in nc_ds:
            if not nc_ds.depolarization_calibration_index[idx_in_file].isnull():  # noqa E501
                pol_calibr_idx = int(nc_ds.depolarization_calibration_index[idx_in_file])  # noqa E501
                result.pol_calibr = DepolarizationCalibration.from_nc_file(nc_ds,  # noqa E501
                                                                           pol_calibr_idx)  # noqa E501

        if 'assumed_particle_lidar_ratio' in nc_ds:
            lidar_ratio = nc_ds.assumed_particle_lidar_ratio
            lidar_ratio_err = nc_ds.assumed_particle_lidar_ratio_error
            result.ds['assumed_particle_lidar_ratio'] = \
                result.angle_to_time_dependent_var(
                    laser_pointing_angle_of_profiles,
                    lidar_ratio)
            result.ds['assumed_particle_lidar_ratio_error'] = \
                result.angle_to_time_dependent_var(
                    laser_pointing_angle_of_profiles,
                    lidar_ratio_err)

        result.get_raw_heightres()

        return result

    @classmethod
    def from_depol_components(cls, transm_sig, refl_sig):
        """Creates a total signal from two depolarization component.

        A Signals instance (which represents a total signal)
        is created from the combination of
        a reflected and a transmitted signal component using the equation
        Sig_total = etaS/K*HR*sig_transm - HT*Sig_refl/(HR*GT - HT*GR)

        Args:
            transm_sig (:class:`Signals`):   the transmitted signal component
            refl_sig (:class:`Signals`):     the reflected signal component

        Returns: Signals
        """

        result = deepcopy(transm_sig)  # see also weakref
        depol_params = {'HR': refl_sig.h.data,   # ToDo Ina debug
                        'GR': refl_sig.g.data,
                        'HT': transm_sig.h.data,
                        'GT': transm_sig.g.data,
                        'gain_factor': refl_sig.pol_calibr.gain_factor.data,  # noqa E501
                        'gain_factor_correction': refl_sig.pol_calibr.gain_factor_correction.data,  # noqa E501
                        }

        result.ds = CombineDepolComponents()(
            transm_sig=transm_sig.ds,
            refl_sig=refl_sig.ds,
            depol_params=depol_params,
        ).run()

        result.channel_id = xr.concat([transm_sig.channel_id,
                                       refl_sig.channel_id],
                                      dim='nc')
        result.pol_channel_conf.values = TOTAL
        result.pol_channel_geometry.values = TRANSMITTED + REFLECTED  # ToDo Ina debug

        return result

    def heightres_to_bins(self, heightres):
        """converts a height resolution into number of vertical bins
        Args: heightres(float): height resolution in m
        Returns: bins(int): number of vertical bins corresponding to the vertical resolution
        """
        return (heightres / self.raw_heightres).round().astype(int)

    def get_raw_heightres(self):
        diff = np.diff(self.height, axis=1)

        d0 = diff[:, 0].reshape(2, 1)
        # reshape is needed to allow broadcasting of the 2 arrays

        if np.all(abs(diff[:] - d0) < 1e-10):
            self.raw_heightres = d0
        else:
            self.logger.error('height axis is not equidistant')

    def heights_to_levels(self, heights):
        """converts a series of height value into a series of level (dim=time)
        Args: heights (xarray): a requested height for each time, in m
        Returns: level (xarray) closest to the requested heights
        """
        times = self.ds.dims['time']
        if heights.shape[0] != times:
            self.logger.error(
                'dataset and heights have different lenghts (time dimension)'
            )
            return None

        closest_bin = (abs(self.height - heights)).argmin(dim='level')
        return closest_bin
#        result = []
#        for t in range(times):
#            result.append(np.where(self.height[t] > heights[t])[0][0])
#        return np.array(result)
#        return closest_bin

    def height_to_levels(self, height):
        """converts a height value into a series of level (dim=time)
        Args: height (float): one requested height for all times, in m
        Returns: level (xarray) closest to the requested height
        """
        # todo: try also scipy bisect
        closest_bin = (abs(self.height - height)).argmin(dim='level')
        return closest_bin

    def data_in_vertical_range(self, v_range, boundaries=None):
        """data in vertical range

        Args:
            v_range(addict.Dict): with keys 'min_height' and \
                    'max_height' which are heights in m)
            boundaries (str): 'extend_with_binres' or
            'clip_with_binres' or None. default = None
        Returns:
            subset of the dataset in the vertical range.
            *   if boundaries == None (default) => returns range between
                    (begin of vertical range) and (end of vertical range)
            *   if boundaries == 'extend_with_binres' => returns range \
                    between \
                    (begin of vertical range - half binres at this height) \
                    and \
                    (end of vertical range + half binres at this height)
            *   if boundaries == 'clip_with_binres' => returns range between \
                    (begin of vertical range + half binres at this height)
                    and
                    (end of vertical range - half binres at this height)
        """
        assert (boundaries is None) or \
               (boundaries == 'extend_with_binres') or \
               (boundaries == 'clip_with_binres')

        min_h = v_range.min_height
        max_h = v_range.max_height

        if boundaries is None:
            min_alt = min_h + self.station_altitude.values
            max_alt = max_h + self.station_altitude.values

            return self.ds.where((self.ds.altitude > min_alt) &
                                 (self.ds.altitude < max_alt),
                                 drop=True)
        else:
            # first valid level
            fvl = self.height_to_levels(min_h)
            # last valid level
            lvl = self.height_to_levels(max_h)

            if boundaries == 'extend_with_binres':
                fvl = max(fvl - self.ds.binres[fvl] // 2, 0)
                lvl = min(lvl + self.ds.binres[lvl] // 2, self.ds.dims.level)
            else:  # boundaries == 'clip_with_binres'
                fvl = max(fvl + self.ds.binres[fvl] // 2, 0)
                lvl = min(lvl - self.ds.binres[lvl] // 2, self.ds.dims.level)

            return self.ds.isel({'level': range(fvl, lvl)})

    @property
    def channel_id_str(self):
        if self.channel_id is not None:
            return str(self.channel_id.values)
        else:
            return None

    def register(self, p_params):
        p_params.general_params.signals.append(self.channel_id_str)
        p_params.add_signal_role(self)

    def normalize_by_shots(self):
        self.ds['err'] = self.ds['err'] * self.scale_factor_shots
        self.ds['data'] = self.ds['data'] * self.scale_factor_shots

    def correct_for_mol_transmission(self):
        self.ds['data'] = self.ds['data'] / \
            self.ds.mol_trasm_at_emission_wl /\
            self.ds.mol_trasm_at_detection_wl

        self.ds['err'] = self.ds['err'] / \
            self.ds.mol_trasm_at_emission_wl / \
            self.ds.mol_trasm_at_detection_wl

    def prepare_for_extinction(self):
        r"""
        .. math::
            sig &= ln(Sig_o / Rayl) = ln(b)\\

            err\_sig &= err\_sig_o * dSig/ dSig_o\\
                    &= err\_sig_o * (dSig/db * db/dSig_o)\\
                    &= err\_sig_o * ( 1/b * 1/rayl )\\
                    &= err\_sig_o *  (Rayl/Sig_o * 1/Rayl)\\
            err\_sig &= err\_sig_o / Sig_o
        """

        self.ds['err'] = self.rel_err
        self.ds['data'] = np.log(self.ds.data / self.ds.mol_extinction)

    @property
    def range(self):
        """xarray.DataArray(dimensions = time, level): range axis in m
                                                    = distance from lidar"""
        return self.height * xr.ufuncs.cos(xr.ufuncs.radians(self.ds.laser_pointing_angle))  # noqa E501

    @property
    def is_WV_sig(self):
        if self.scatterer is not None:
            return bool(self.scatterer == WATER_VAPOR)
        else:
            return False

    @property
    def is_elast_sig(self):
        if self.scatterer is not None:
            return bool((self.scatterer & PARTICLE) == PARTICLE)
        else:
            return False

    @property
    def is_Raman_sig(self):
        if self.scatterer is not None:
            return (not self.is_WV_sig) & (not self.is_elast_sig)
        else:
            return False

    @property
    def is_nr_signal(self):
        if self.alt_range is not None:
            return bool(self.alt_range == NEAR_RANGE)
        else:
            return False

    @property
    def is_fr_signal(self):
        if self.alt_range is not None:
            return bool(self.alt_range == FAR_RANGE)
        else:
            return False

    @property
    def is_all_range_signal(self):
        if self.alt_range is not None:
            return bool(self.alt_range == ALL_RANGE)
        else:
            return False

    @property
    def is_total_sig(self):
        if self.pol_channel_conf is not None:
            return bool(self.pol_channel_conf == TOTAL)
        else:
            return False

    @property
    def is_cross_sig(self):
        if self.pol_channel_conf is not None:
            return bool(self.pol_channel_conf == CROSS)
        else:
            return False

    @property
    def is_parallel_sig(self):
        if self.pol_channel_conf is not None:
            return bool(self.pol_channel_conf == PARALLEL)
        else:
            return False

    @property
    def is_transm_sig(self):
        if self.pol_channel_geometry is not None:
            return bool(self.pol_channel_geometry == TRANSMITTED)
        else:
            return False

    @property
    def is_refl_sig(self):
        if self.pol_channel_geometry is not None:
            return bool(self.pol_channel_geometry == REFLECTED)
        else:
            return False

    def eff_to_used_binres(self, an_eff_binres):
        """
        how many bins are used to calculate a product with the given effective bin resolution

        Args:
            an_eff_binres (float): effective bin resolution

        Returns:
            number of used bins (int)
        """
        if self.calc_used_bin_res_routine:
            return self.calc_used_bin_res_routine.run(eff_binres=an_eff_binres)
        else:
            self.logger.warning('no method implemented for effective-to-used bin resolution')
            return an_eff_binres

    def get_binres_from_fixed_smooth(self, smooth_params, res, used_binres_routine=None):
        if used_binres_routine:
            self.calc_used_bin_res_routine = used_binres_routine

        # get params for the lower part of the profile (below transition zone)
        tz_bottom = smooth_params.transition_zone.bottom
        tz_bottom_bin = self.height_to_levels(tz_bottom)
        vert_res_low = smooth_params.vert_res[RESOLUTION_STR[res]]['lowrange']
        binres_low = self.heightres_to_bins(vert_res_low)
        used_binres_low = self.eff_to_used_binres(binres_low)

        # get params for the upper part of the profile (above transition zone)
        tz_top = smooth_params.transition_zone.top
        tz_top_bin = self.height_to_levels(tz_top)
        vert_res_high = smooth_params.vert_res[RESOLUTION_STR[res]]['highrange']
        binres_high = self.heightres_to_bins(vert_res_high)
        used_binres_high = self.eff_to_used_binres(binres_high)

        delta_res = (vert_res_high - vert_res_low) / (tz_top_bin - tz_bottom_bin)

        # ! reversed logic! because
        # where(condition, fillvalue where condition is not true)
        result = self.binres.where(self.binres.level > tz_bottom_bin, used_binres_low)
        result = result.where(result.level < tz_top_bin, used_binres_high)

        for t in range(tz_bottom_bin.shape[0]):
            for idx in range(int(tz_bottom_bin[t]), int(tz_top_bin[t])):
                vert_res = float(vert_res_low + delta_res[t] * (idx - tz_bottom_bin[t]))
                a_binres = int(self.heightres_to_bins(vert_res)[t])
                a_used_binres = self.eff_to_used_binres(a_binres)
                result[t, idx] = a_used_binres

        return result


class CombineDepolComponentsDefault(BaseOperation):
    """
    Calculates a combined signal from depol component

    params : Dict...
    """

    def run(self):
        """
        is created from the combination of
        a reflected and a transmitted signal component using the equation
        Sig_total = etaS/K*HR*sig_transm - HT*Sig_refl/(HR*GT - HT*GR)
        """
        transm_sig = self.kwargs['transm_sig']
        refl_sig = self.kwargs['refl_sig']
        calibr_params = self.kwargs['depol_params']

        etaS = float(calibr_params['gain_factor'].value)
        err_etaS = float(calibr_params['gain_factor'].statistical_error)
        if np.isnan(err_etaS):
            err_etaS = 0

        K = float(calibr_params['gain_factor_correction'].value)
        err_K = float(calibr_params['gain_factor_correction'].statistical_error)  # noqa E501
        if np.isnan(err_K):
            err_K = 0

        HR = float(calibr_params['HR'].value)
        GR = float(calibr_params['GR'].value)
        HT = float(calibr_params['HT'].value)
        GT = float(calibr_params['GT'].value)

        factor = etaS / K * HR
        denom = (HR*GT - HT*GR)

        result = deepcopy(transm_sig)
        result['data'] = (factor * transm_sig.data -
                          HT * refl_sig.data) / denom
        result['err'] = np.sqrt(np.square(HT * refl_sig.err) +
                                np.square(factor * transm_sig.err) +
                                np.square(HR / K * transm_sig.data * err_etaS) +  # noqa E501
                                np.square(HR / K / K * transm_sig.data * err_K)) / denom  # noqa E501

        result['qf'] = transm_sig.qf | refl_sig.qf

        return result


class CombineDepolComponents(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which
    calculates a total signal from two signals with
    depolarization component. In this case, it will be
    always an instance of GetCombinedSignal().

    Args:
        refl_sig (xarray.DataSet,
                    (dimensions=time,level),
                    variables=data,err,):
            data of the reflected signal
        transm_sig (xarray.DataSet, (dimensions=time,level)):
            data of the transmitted signal
        depol_params (Dict): all parameters needed for the
            calculation of depolarization and signal combination
            (HR, HT, GR, GT, gain factor, and gain factor correction).
            The parameter are xarray.Datasets with the variables
            'value', 'statistical_error', and 'systematic_error'.

    """

    name = 'CombineDepolComponents'

    def __call__(self, **kwargs):
        assert 'refl_sig' in kwargs
        assert 'transm_sig' in kwargs
        assert 'depol_params' in kwargs
        res = super(CombineDepolComponents, self).__call__(**kwargs)
        return res

    def get_classname_from_db(self):
        """

        return: always 'CombineDepolComponents' .
        """
        return CombineDepolComponentsDefault.__name__


registry.register_class(CombineDepolComponents,
                        CombineDepolComponentsDefault.__name__,
                        CombineDepolComponentsDefault)
