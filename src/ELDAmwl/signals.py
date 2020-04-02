# -*- coding: utf-8 -*-
"""Classes for signals"""

from addict import Dict
from ELDAmwl.columns import Columns
from ELDAmwl.constants import ANALOG
from ELDAmwl.constants import CROSS
from ELDAmwl.constants import FAR_RANGE
from ELDAmwl.constants import NEAR_RANGE
from ELDAmwl.constants import PARALLEL
from ELDAmwl.constants import PARTICLE
from ELDAmwl.constants import REFLECTED
from ELDAmwl.constants import TOTAL
from ELDAmwl.constants import TRANSMITTED
from ELDAmwl.constants import WATER_VAPOR
from ELDAmwl.factory import BaseOperation, BaseOperationFactory
from ELDAmwl.registry import registry

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
        self._signals = None
        self._cloud_mask = None
        self._header = None

    def read_nc_file(self, data_storage, p_param):
        """ reading an ELPP file

        Signals, cloud mask, and the header are read
        from an ELPP file and put into the data_storage

        Args:
            data_storage (:obj:`DataStorage`): global data storage instance
            p_param:

        """
        # todo: check if scc version in query = current version

        nc_ds = xr.open_dataset(os.path.join(cfg.SIGNAL_PATH,
                                             p_param.general_params.elpp_file))

        self._cloud_mask = nc_ds.cloud_mask.astype(int)
        data_storage.cloud_mask = self._cloud_mask

        self._header = Header.from_nc_file(nc_ds)
        data_storage.header = self._header

        for idx in range(nc_ds.dims['channel']):
            sig = Signals.from_nc_file(nc_ds, idx)
            sig.register(data_storage, p_param)

        nc_ds.close()

class DepolarizationCalibration(object):
    data = Dict({'gain_factor': np.nan,
            'gain_factor_stat_err': np.nan,
            'gain_factor_sys_err': np.nan,
            'gain_factor_correction': np.nan,
            'gain_factor_correction_stat_err': np.nan,
            'gain_factor_correction_sys_err': np.nan,
            })

    @classmethod
    def from_nc_file(cls, nc_ds, pol_cal_idx):
        result = cls
        result.data.gain_factor = \
            nc_ds.polarization_gain_factor[pol_cal_idx]
        result.data.gain_factor_stat_err = \
            nc_ds.polarization_gain_factor_statistical_error[pol_cal_idx]
        result.data.gain_factor_sys_err = \
            nc_ds.polarization_gain_factor_systematic_error[pol_cal_idx]

        result.data.gain_factor_correction = \
            nc_ds.polarization_gain_factor_correction[pol_cal_idx]
        result.data.gain_factor_correction_stat_err = \
            nc_ds.polarization_gain_factor_correction_statistical_error[pol_cal_idx]
        result.data.gain_factor_correction_sys_err = \
            nc_ds.polarization_gain_factor_correction_systematic_error[pol_cal_idx]

        #polarization_gain_factor_measurementid
        #polarization_gain_factor_correction_start_datetime
        #seconds since 1970-01-01T00:00:00Z
        #polarization_gain_factor_correction_stop_datetime
        #polarization_gain_factor_correction_start_datetime
        #polarization_gain_factor_correction_stop_datetime
        return result


class Header(object):
    station_latitude = np.nan
    station_longitude = np.nan
    station_altitude = np.nan

    @classmethod
    def from_nc_file(cls, nc_ds):
        """reads header information from an ELPP file

        Args:
            nc_ds (xarray.Dataset): content of the ELPP file.
        """
        result = cls()
        result.station_latitude = nc_ds.latitude
        result.station_longitude = nc_ds.longitude
        result.station_altitude = nc_ds.station_altitude

        return result

    def __eq__(self, other):
        result = True
        for a in self.__dict__.keys():
            if getattr(self, a) != getattr(other, a):
                result = False
        return result

    @property
    def latitude(self):
        """measurement site latitude in degrees_north"""
        return self.station_latitude

    @property
    def longitude(self):
        """measurement site longitude in degrees_east"""
        return self.station_longitude

    @property
    def altitude(self):
        """measurement site altitude in m a.s.l."""
        return self.station_altitude


class Signals(Columns):
    """two-dimensional (time, level) signal data

    """

#    def __init__(self):
#        super(Signals, self).__init__()
    emission_wavelength = np.nan
    detection_wavelength = np.nan
    channel_id = np.nan
    channel_id_str = ''
    detection_type = np.nan
    channel_idx_in_ncfile = np.nan
    scatterer = np.nan
    alt_range = np.nan
    pol_channel_conf = np.nan
    scale_factor_shots = None
    pol_calibr = None

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

        result.ds = nc_ds.range_corrected_signal[idx_in_file].to_dataset(name='data')  # noqa E501
        result.ds['err'] = nc_ds.range_corrected_signal_statistical_error[idx_in_file]  # noqa E501

        result.station_altitude = nc_ds.station_altitude
        result.ds['altitude'] = nc_ds.altitude

        result.ds['time_bounds'] = nc_ds.time_bounds

        laser_pointing_angle_of_profiles = nc_ds.laser_pointing_angle_of_profiles  # noqa E501

        laser_pointing_angle = nc_ds.laser_pointing_angle
        result.ds['laser_pointing_angle'] = result.angle_to_time_dependent_var(
            laser_pointing_angle_of_profiles,
            laser_pointing_angle)

        atmospheric_molecular_extinction = nc_ds.atmospheric_molecular_extinction[idx_in_file]  # noqa E501
        result.ds['mol_extinction'] = result.angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                  atmospheric_molecular_extinction)  # noqa E501

        result.ds['mol_lidar_ratio'] = nc_ds.atmospheric_molecular_lidar_ratio[idx_in_file]  # noqa E501

        mol_trasm_at_detection_wl = nc_ds.atmospheric_molecular_trasmissivity_at_detection_wavelength[idx_in_file]  # noqa E501
        result.ds['mol_trasm_at_detection_wl'] = result.angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                             mol_trasm_at_detection_wl)  # noqa E501

        mol_trasm_at_emission_wl = nc_ds.atmospheric_molecular_trasmissivity_at_emission_wavelength[idx_in_file]  # noqa E501
        result.ds['mol_trasm_at_emission_wl'] = result.angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                            mol_trasm_at_emission_wl)  # noqa E501

        result.channel_id = nc_ds.range_corrected_signal_channel_id[idx_in_file].astype(int)  # noqa E501
        result.detection_type = nc_ds.range_corrected_signal_detection_mode[idx_in_file].astype(int)  # noqa E501
        result.detection_wavelength = nc_ds.range_corrected_signal_detection_wavelength[idx_in_file]  # noqa E501
        result.emission_wavelength = nc_ds.range_corrected_signal_emission_wavelength[idx_in_file]  # noqa E501
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

        result.g = nc_ds.polarization_crosstalk_parameter_g[idx_in_file]
        result.g_stat_err = nc_ds.polarization_crosstalk_parameter_g_statistical_error[idx_in_file]  # noqa E501
        result.g_sys_err = nc_ds.polarization_crosstalk_parameter_g_systematic_error[idx_in_file]  # noqa E501

        result.h = nc_ds.polarization_crosstalk_parameter_h[idx_in_file]
        result.h_stat_err = nc_ds.polarization_crosstalk_parameter_h_statistical_error[idx_in_file]  # noqa E501
        result.h_sys_err = nc_ds.polarization_crosstalk_parameter_h_systematic_error[idx_in_file]  # noqa E501

        result.channel_id_str = str(result.channel_id.values)

        if 'depolarization_calibration_index' in nc_ds:
            pol_calibr_idx = nc_ds.depolarization_calibration_index[idx_in_file]
            pol_calibr = DepolarizationCalibration.from_nc_file(nc_ds, pol_calibr_idx)

        return result

    @classmethod
    def from_depol_components(cls, transm_sig, refl_sig):
        """Creates a total signal from two depolarization components.

        A Signals instance (which represents a total signal)
        is created from the combination of
        a reflected and a transmitted signal component using the equation
        Sig_total = etaS/K*HR*sig_transm - HT*Sig_refl/(HR*GT - HT*GR)

        Args:
            transm_sig (Signals):   the transmitted signal component
            refl_sig (Signals):     the reflected signal component

        Returns: Signals
        """
        result = cls()

        result = transm_sig.deepcopy()  # see also weakref

        depol_params = {'HR': refl_sig.h.values,
                        'GR': refl_sig.g.values,
                        'HT': transm_sig.h.values,
                        'GT': transm_sig.values,
                        'pol_calibr': refl_sig.pol_calibr,
                        }
        comb_depol_signals = CombineDepolComponents()(
            transm_sig=transm_sig.data,
            refl_sig=refl_sig.data,
            depol_params=depol_params
            )
        result.data = comb_depol_signals.run()


        result.channel_id.values.append(refl_sig.channel_id.values)
        result.pol_channel_conf.values[:] = TOTAL


        return result

    def register(self, storage, p_params):
        storage.add_elpp_signal(p_params.prod_id_str, self)  # noqa E501
        p_params.general_params.signals.append(self.channel_id_str)
        p_params.add_signal_role(self)

    def normalize_by_shots(self):
        self.ds['err'] = self.ds['err'] * self.scale_factor_shots
        self.ds['data'] = self.ds['data'] * self.scale_factor_shots

    @property
    def range(self):
        """xarray.DataArray(dimensions = time,level): range axis in m
                                                    = distance from lidar"""
        return self.height * xr.ufuncs.cos(xr.ufuncs.radians(self.ds.laser_pointing_angle))  # noqa E501

    @property
    def is_WV_sig(self):
        return (self.scatterer == WATER_VAPOR).values

    @property
    def is_elast_sig(self):
        return ((self.scatterer & PARTICLE) == PARTICLE).values

    @property
    def is_Raman_sig(self):
        return (not self.is_WV_sig) & (not self.is_elast_sig)

    @property
    def is_nr_signal(self):
        return (self.alt_range == NEAR_RANGE).values

    @property
    def is_fr_signal(self):
        return (self.alt_range == FAR_RANGE).values

    @property
    def is_total_sig(self):
        return (self.pol_channel_conf == TOTAL).values

    @property
    def is_cross_sig(self):
        return (self.pol_channel_conf == CROSS).values

    @property
    def is_parallel_sig(self):
        return (self.pol_channel_conf == PARALLEL).values

    @property
    def is_transm_sig(self):
        return (self.pol_channel_geometry == TRANSMITTED).values

    @property
    def is_refl_sig(self):
        return (self.pol_channel_geometry == REFLECTED).values


class GetCombinedSignal(BaseOperation):
    """
    Calculates a combined signal from depol components

    params : Dict...
    """

    def run(self):
        """
        is created from the combination of
        a reflected and a transmitted signal component using the equation
        Sig_total = etaS/K*HR*sig_transm - HT*Sig_refl/(HR*GT - HT*GR)
        """
        calibr_params = self.kwargs['depol_params']
        etaS = calibr_params.gain_factor
        K = calibr_params.gain_factor_corr
        #factor = etaS / K * HR
        #denom = (HR*GT - HT*GR)

        #result.data.values = (factor * transm_sig.data.values -
        #                      HT * refl_sig.data.values / denom)
        # result.err.values =

        pass


class CombineDepolComponents(BaseOperationFactory):
    """
    Returns an instance of BaseOperation which
    calculates a total signal from two signals with
    depolarization components. In this case, it will be
    always an instance of GetCombinedSignal().

    Args:
        refl_sig (xarray.DataArray,
                    (dimensions=time,level),
                    variables=data,err,):
            data of the reflected signal
        transm_sig (xarray.DataArray, (dimensions=time,level)):
            data of the transmitted signal
        depol_params (Dict): all parameters needed for the
            calculation of depolarization and signal combination

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
        return GetCombinedSignal.__class__.__name__


registry.register_class(CombineDepolComponents,
                        GetCombinedSignal.__class__.__name__,
                        GetCombinedSignal)

