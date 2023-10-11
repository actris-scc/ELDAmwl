# -*- coding: utf-8 -*-
"""Classes for signals"""

from copy import deepcopy
from ELDAmwl.bases.base import DataPoint
from ELDAmwl.bases.columns import Columns
from ELDAmwl.bases.factory import BaseOperation
from ELDAmwl.bases.factory import BaseOperationFactory
from ELDAmwl.component.interface import ICfg, ILogger
from ELDAmwl.component.interface import IDataStorage
from ELDAmwl.component.registry import registry
from ELDAmwl.errors.exceptions import CannotOpenELLPFile
from ELDAmwl.errors.exceptions import ELPPFileNotFound
from ELDAmwl.errors.exceptions import RepeatedCorrectMolTransm
from ELDAmwl.errors.exceptions import RepeatedNormalizeByshots
from ELDAmwl.header import Header
from ELDAmwl.rayleigh import RayleighLidarRatio
from ELDAmwl.utils.constants import ABOVE_MAX_ALT
from ELDAmwl.utils.constants import ALL_OK, P_ALL_OK
from ELDAmwl.utils.constants import ALL_RANGE
from ELDAmwl.utils.constants import ANALOG
from ELDAmwl.utils.constants import BELOW_OVL
from ELDAmwl.utils.constants import CROSS
from ELDAmwl.utils.constants import FAR_RANGE
from ELDAmwl.utils.constants import NC_FILL_BYTE
from ELDAmwl.utils.constants import NC_FILL_INT
from ELDAmwl.utils.constants import NEAR_RANGE
from ELDAmwl.utils.constants import PARALLEL
from ELDAmwl.utils.constants import PARTICLE
from ELDAmwl.utils.constants import REFLECTED
from ELDAmwl.utils.constants import RESOLUTION_STR
from ELDAmwl.utils.constants import TOTAL
from ELDAmwl.utils.constants import TRANSMITTED
from ELDAmwl.utils.constants import WATER_VAPOR
from ELDAmwl.utils.path_utils import abs_file_path
from zope import component

import numpy as np
import os
import xarray as xr


class ElppData(object):
    r"""Representation of one ELPP file.

    An ELPP file contains a cloud mask and one or several range-corrected,
    background-subtracted signals which were prepared by the SCC module ELPP.

    Each ELPP file contains all the signals that are needed to calculate one basic optical product
    (particle extinction coefficient, particle backscatter coefficient, volume linear depolarization ratio).

    Those signals are described by the lidar equation:

    .. math::
        P_{\lambda}(t,z) &= C_{\lambda}(t)\:
                        \bigl( \beta_{\lambda}^{par}(t,z) +
                        \beta_{\lambda}^{mol}(t,z)\bigr)\:
                        T_{\lambda}(t,z) \\
        T_{\lambda}(t,z) &= T_{\lambda_{up}}^{mol}(t,z)\: T_{\lambda_{up}}^{par}(t,z) \:
                          T_{\lambda_{down}}^{mol}(t,z)\: T_{\lambda_{down}}^{par}(t,z) \\
        T_{\lambda}^{scat}(t,z) &= \Bigl( \exp \bigl( \tau_{\lambda}^{scat}(t,z)\bigr)\Bigr)^{-1} \\
        \tau_{\lambda}^{scat}(t,z) &= \int_{z=0}^{z} \alpha_{\lambda}^{scat}(t,\zeta) d\zeta \\
        \alpha_{\lambda}^{scat}(t,z) &= \beta_{\lambda}^{scat}(t,z) \: S_{\lambda}^{scat}(t,z)

    with

    :math:`P_{\lambda}(t,z)`: prepared signal at wavelength :math:`\lambda`

    :math:`C_{\lambda}(t)`: the lidar constant

    :math:`z`: the height above the lidar

    :math:`t`: time of the measurement

    :math:`\beta(t,z)`: the backscatter coefficient from scattering at
    molecules (:math:`scat = mol`) and particles (:math:`scat = par`)

    :math:`T_{\lambda}(t,z)`: the 2-way (up and down) atmospheric transmission

    :math:`\tau_{\lambda}^{scat}(t,z)`: the optical depth

    :math:`\alpha_{\lambda}^{scat}(t,z)`: the extinction coefficient

    :math:`S_{\lambda}^{scat}(t,z)`: the lidar ratio
    """

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    def __init__(self):
        self.signals = None
        self.cloud_mask = None
        self.header = None
        self.data_storage = component.queryUtility(IDataStorage)
        self.logger = component.queryUtility(ILogger)

    def read_nc_file(self, p_param):
        """ reading an ELPP file

        Signals, cloud mask, and the header are read
        from an ELPP file and put into the data_storage

        Args:
            p_param:

        """
        # todo: check if scc version in query = current version

        filename = p_param.general_params.elpp_file
        elpp_file = abs_file_path(self.cfg.SIGNAL_PATH, filename)
        self.logger.debug('read file {0}'.format(filename))

        if not os.path.exists(elpp_file):
            self.logger.error('ELPP file {0} does not exist.'.format(elpp_file))
            raise(ELPPFileNotFound(elpp_file))
        try:
            nc_ds = xr.open_dataset(elpp_file)
        except Exception as e:   # ToDo Ina : which exception exactly?
            self.logger.error('cannot read ELPP file {0}.'.format(elpp_file))
            print(e)  # noqa T001
            raise(CannotOpenELLPFile(elpp_file))

        self.cloud_mask = nc_ds.cloud_mask.astype(int)
        self.data_storage.cloud_mask = self.cloud_mask

        self.header = Header.from_nc_file(elpp_file, nc_ds)
        self.data_storage.header = self.header

        for idx in range(nc_ds.dims['channel']):
            sig = Signals.from_nc_file(nc_ds, idx)
            sig.ds.load()
            self.data_storage.set_elpp_signal(p_param.prod_id_str, sig)  # noqa E501
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

    emission_wavelength = None
    detection_wavelength = None
    channel_id = None
    detection_type = None
    channel_idx_in_ncfile = None
    scatterer = None
    alt_range = None
    pol_channel_conf = None
    scale_factor_shots = None
    pol_calibr = None
    raw_heightres = None
    station_altitude = None
    is_from_depol_components = None

    calc_eff_bin_res_routine = None
    calc_used_bin_res_routine = None

    h = None
    g = None
    pol_channel_geometry = None

    def __init__(self):
        super(Signals, self).__init__()
        self.normalized_by_shots = False
        self.corrected_for_mol_transmission = False
        self.is_from_depol_components = False

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    @property
    def data_storage(self):
        return component.queryUtility(IDataStorage)

    @property
    def name(self):
        return hex(id(self))

    @classmethod
    def as_sig_ratio(cls, enumerator, denominator):
        """creates a Signals instance from the ratio of two Signals

        Args:
            enumerator (`.Signals`): nominator
            denominator (`.Signals`): denominator

        Returns: Signals

        """
        result = deepcopy(enumerator)

        result.ds['data'] = enumerator.ds.data / denominator.ds.data
        result.ds['err'] = np.absolute(
            result.ds.data
            * np.sqrt(np.square(enumerator.rel_err)
                      + np.square(denominator.rel_err)))
        result.ds['qf'] = enumerator.ds.qf | denominator.ds.qf

        result.channel_id = xr.concat([enumerator.channel_id,
                                       denominator.channel_id],
                                      dim='nc')
        result.ds['mol_backscatter'] = enumerator.ds.mol_backscatter
        result.profile_qf = enumerator.profile_qf | denominator.profile_qf

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

        # result.ds = nc_ds.range_corrected_signal[idx_in_file].to_dataset(name='data')  # noqa E501
        result.ds = xr.Dataset()
        result.ds['data'] = nc_ds.range_corrected_signal[idx_in_file]
        result.ds['err'] = nc_ds.range_corrected_signal_statistical_error[idx_in_file]  # noqa E501

        # initiate bin resolution with value 1
        result.ds['binres'] = xr.DataArray(
            np.ones((nc_ds.dims['time'],
            nc_ds.dims['level'])).astype(np.int64),  # noqa E501
            coords=[nc_ds.time, nc_ds.level],
            dims=['time', 'level'])
        result.ds['binres'].attrs = {'long_name': 'vertical resolution',
                                     'units': 'bins',
                                     }

        # initiate quality flag with values 'ALL_OK'
        qf = np.ones((nc_ds.dims['time'], nc_ds.dims['level'])).astype(np.short) * ALL_OK
        result.ds['qf'] = xr.DataArray(
            qf,
            coords=[nc_ds.time, nc_ds.level],
            dims=['time', 'level'])
        result.ds['qf'].attrs = {
            'long_name': 'quality_flag',
            'flag_meanings': 'data_ok '
            'negative_data '
            'incomplete_overlap_not_correctable '
            'above_max_altitude_range '
            # 'cloud_contamination '
            # 'above_Klett_reference_height '
            'depol_ratio_larger_100% '
            'backscatter_ratio_below_required_min_value',  # noqa E501
            # 'flag_masks': [0, 1, 2, 4, 8, 16, 32, 64],
            'flag_masks': [0, 1, 2, 4, 8, 16, 32, 64],
            'valid_range': [0, 107],
            'units': '1',
            '_FillValue': NC_FILL_INT,
        }

        # todo: make station_altitude a function of time (moving systems)
        result.station_altitude = nc_ds.station_altitude
        result.station_altitude.load()

        result.ds['altitude'] = nc_ds.altitude
        result.ds['height'] = nc_ds.altitude - nc_ds.station_altitude

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
        result.calc_mol_backscatter()
        result.profile_qf = xr.DataArray(np.ones(nc_ds.dims['time'], dtype=int) * P_ALL_OK, # noqa E501
                                         coords=[nc_ds.time],
                                         dims=['time'],
                                         )

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
        depol_params = {'HR': refl_sig.h.data,
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

        result.is_from_depol_components = True

        return result

    def heightres_to_bins(self, heightres):
        """converts a height resolution into number of vertical bins
        Args: heightres(float): height resolution in m
        Returns: bins(int): number of vertical bins corresponding to the vertical resolution
        """
        return (heightres / self.raw_heightres).round().astype(int)

    def get_raw_heightres(self):
        diff = np.diff(self.height, axis=1)

        d0 = diff[:, 0].reshape(self.num_times, 1)
        # reshape is needed to allow broadcasting of the 2 arrays

        if np.all(abs(diff[:] - d0) < 1e-10):
            self.raw_heightres = d0
        else:
            self.logger.error('height axis is not equidistant')

    def ranges_to_levels(self, ranges):
        """converts a series of range value into a series of level (dim=time)
        Args: ranges (xarray): a requested height for each time, in m
        Returns: level (xarray) closest to the requested heights
        """
        times = self.ds.dims['time']
        if ranges.shape[0] != times:
            self.logger.error('dataset and ranges have different lenghts (time dimension)')
            return None

        # closest_bin = (abs(self.range - ranges)).argmin(dim='level')

        if not np.any(np.isnan(ranges)):
            closest_bin = (abs(self.range - ranges)).argmin(dim='level')
        else:
            closest_bin = xr.ones_like(ranges, int) * NC_FILL_INT
            for t in range(times):
                if not np.isnan(ranges[t]):
                    closest_bin[t] = (abs(self.range[t] - ranges[t])).argmin(dim='level')
        return closest_bin

    def heights_to_levels(self, heights):
        """converts a series of height value into a series of level (dim=time)
        Args: heights (xarray): a requested height for each time, in m
        Returns: level (xarray) closest to the requested heights
        """
        times = self.ds.dims['time']
        if heights.shape[0] != times:
            self.logger.error('dataset and heights have different lenghts (time dimension)')
            return None

        # closest_bin = (abs(self.height - heights)).argmin(dim='level')
        if not np.any(np.isnan(heights)):
            closest_bin = (abs(self.height - heights)).argmin(dim='level')
        else:
            closest_bin = xr.ones_like(heights, int) * NC_FILL_INT
            for t in range(times):
                if not np.isnan(heights[t]):
                    closest_bin[t] = (abs(self.height[t] - heights[t])).argmin(dim='level')

        return closest_bin

    def height_to_levels(self, height):
        """converts a height value into a series of level (dim=time)
        Args: height (float): one requested height for all times, in m
        Returns: level (xarray) closest to the requested height
        """
        # todo: try also scipy bisect
        closest_bin = (abs(self.height - height)).argmin(dim='level')
        return closest_bin

    def data_in_vertical_range(self, v_range, boundaries=None):
        """ returns subset of data within vertical range

        Args:
            v_range(addict.Dict): with keys 'min_height' and 'max_height' (which are heights in m)
            boundaries (str): 'extend_with_binres' or 'clip_with_binres' or None. default = None

        Returns:
            subset of the dataset in the vertical range.

            *   if boundaries == None (default)
                    =>returns range between
                    (begin of vertical range) and (end of vertical range)
            *   if boundaries == 'extend_with_binres'
                    => returns range between
                    (begin of vertical range - half binres at this height)
                    and
                    (end of vertical range + half binres at this height)
            *   if boundaries == 'clip_with_binres'
                    => returns range between
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
            result = self.ds.where((self.height > min_h) & (self.height < max_h), drop=True)
            result['range'] = self.range.where((self.height > min_h) & (self.height < max_h), drop=True)
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

            result = self.ds.isel({'level': range(fvl, lvl)})
            result['range'] = self.range.isel({'level': range(fvl, lvl)})

        return result

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
        r"""normalizes the signal by the number of laser shots

        .. math::
            \widetilde{P_{\lambda}(t,z)}
                &= \widetilde {C_{\lambda}(t)} \:
                   \bigl( \beta_{\lambda}^{par}(t,z) +
                          \beta_{\lambda}^{mol}(t,z)\bigr)\:
                   T_{\lambda}(t,z)\\
                &= \frac {P_{\lambda}(t,z)}
                         {n_{shots}(t)} \\
            \widetilde {C_{\lambda}(t)}
                &= \frac {C_{\lambda}(t)}
                         {n_{shots}(t)} \\

        With

        :math:`P_{\lambda}(t,z)` and :math:`\widetilde{P_{\lambda}(t,z)}`
        being the original and corrected signal,

        :math:`C_{\lambda}(t)` and :math:`\widetilde{C_{\lambda}(t)}`
        being the original and corrected lidar constant, and

        :math:`n_{shots}(t)` the number of laser shots accumulated in the time slice.

        Raises:
            RepeatedNormalizeByshots: on attempt to normalize a signal by number of laser shots if it was already normalized before

        .. note::
            This procedure affects only signals which were detected in
            photon-counting mode or glued signals. Analog signals remain unchanged.

        """
        if self.normalized_by_shots:
            raise RepeatedNormalizeByshots(self.channel_id)
        self.ds['err'] = self.ds['err'] * self.scale_factor_shots
        self.ds['data'] = self.ds['data'] * self.scale_factor_shots
        self.normalized_by_shots = True

    def set_valid_height_range(self, v_range):
        """ set data levels below and above v_range as invalid

        levels below v_range are labeled with self.qf = BELOW_OVL
        levels above v_range are labeled as self.qf = ABOVE_MAX_ALT

        Args:
            v_range(addict.Dict): with keys 'min_height' and \
                    'max_height' which are heights in m a.g.)
        Returns:
            None
        """

        min_h = v_range.min_height
        max_h = v_range.max_height

        # first valid level
        fvl = self.height_to_levels(min_h).data
        # last valid level
        lvl = self.height_to_levels(max_h).data

        for t in range(self.num_times):
            for level in range(fvl[t]):
                self.set_invalid_point(t, level, BELOW_OVL)
            for level in range(lvl[t] + 1, self.num_levels):
                self.set_invalid_point(t, level, ABOVE_MAX_ALT)

    def correct_for_mol_transmission(self):
        r"""the signal data are corrected for molecular atmospheric transmission

        The following equations are applied with :math:`P_{\lambda}(t,z)`
        being the signal as described in `.ELPPData`

        .. math::
            \widetilde{P_{\lambda}(t,z)}
                &= C_{\lambda}(t)\:
                   \bigl( \beta_{\lambda}^{par}(t,z) +
                          \beta_{\lambda}^{mol}(t,z)\bigr)\:
                   T_{\lambda_{up}}^{par}(t,z) \: T_{\lambda_{down}}^{par}(t,z)\\
                &= \frac {P_{\lambda}(t,z)}
                         {T_{\lambda_{up}}^{mol}(t,z)\: T_{\lambda_{down}}^{mol}(t,z)} \\

            \Delta \widetilde{P_{\lambda}(t,z)}
                &= \frac {\Delta P_{\lambda}(t,z)}
                         {T_{\lambda_{up}}^{mol}(t,z)\: T_{\lambda_{down}}^{mol}(t,z)}

        With

        :math:`P_{\lambda}(t,z)` and :math:`\Delta P_{\lambda}(t,z)`
        being the original signal and its statistical uncertainty and

        :math:`\widetilde{P_{\lambda}(t,z)}` and :math:`\Delta \widetilde{P_{\lambda}(t,z)}`
        being the corrected signal and its statistical uncertainty.

        Raises:
            RepeatedCorrectMolTransm: on attempt to correct a signal for molecular transmission if it was already corrected before

        """
        if self.corrected_for_mol_transmission:
            raise RepeatedCorrectMolTransm

        self.ds['data'] = self.ds['data'] / \
            self.ds.mol_trasm_at_emission_wl /\
            self.ds.mol_trasm_at_detection_wl

        self.ds['err'] = self.ds['err'] / \
            self.ds.mol_trasm_at_emission_wl / \
            self.ds.mol_trasm_at_detection_wl

        self.corrected_for_mol_transmission = True

    def prepare_for_extinction(self):
        r"""
        .. math::
            sig &= ln(Sig_o / Rayl) = ln(b)\\

            \Delta_{sig} &= err\_sig_o * dSig/ dSig_o\\
                    &= err\_sig_o * (dSig/db * db/dSig_o)\\
                    &= err\_sig_o * ( 1/b * 1/Rayl )\\
                    &= err\_sig_o *  (Rayl/Sig_o * 1/Rayl)\\
            err\_sig &= err\_sig_o / Sig_o

        with :math:`sig`: prepared signal
        """

        self.ds['err'] = self.rel_err
        self.ds['data'] = np.log(self.ds.data / self.ds.mol_extinction)

    def calc_mol_backscatter(self):
        rayl_lr = RayleighLidarRatio()(wavelength=self.emission_wavelength).run()
        mol_bsc = self.ds.mol_extinction / rayl_lr
        self.ds['mol_backscatter'] = mol_bsc.assign_attrs(
            {'units': 'm-1 sr-1',
             'long_name': 'calculated molecular backscatter coefficient at emission wavelength'})

    @property
    def range(self):
        """xarray.DataArray(dimensions = time, level): range axis in m
                                                    = distance from lidar"""
        return self.height / xr.ufuncs.cos(xr.ufuncs.radians(self.ds.laser_pointing_angle))  # noqa E501

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
        Sig_total = (etaS/K*HR*sig_transm - HT*Sig_refl)/(HR*GT - HT*GR)
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
        denom = (HR * GT - HT * GR)

        result = deepcopy(transm_sig)  # todo ina: is this copy necessary?
        result['data'] = (factor * transm_sig.data - HT * refl_sig.data) / denom
        result['err'] = np.sqrt(
            np.square(HT * refl_sig.err) +   # noqa W504
            np.square(factor * transm_sig.err) +    # noqa W504
            np.square(HR / K * transm_sig.data * err_etaS) +    # noqa W504
            np.square(HR / K / K * transm_sig.data * err_K)) / denom    # noqa W504

        result['qf'] = transm_sig.qf | refl_sig.qf

        return result


class CombineDepolComponents(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which
    calculates a total signal from two signals with
    depolarization component. In this case, it will be
    always an instance of GetCombinedSignal().

    Args:
        refl_sig (xarray.DataSet, (dimensions=time,level), variables=data,err,):  data of the reflected signal
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
