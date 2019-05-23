import numpy as np
import xarray as xr

from ELDAmwl.columns import Columns
from ELDAmwl.constants import WATER_VAPOR, PARTICLE, NEAR_RANGE, FAR_RANGE, TOTAL, CROSS, PARALLEL


class Signals(Columns):

    def __init__(self):
        self.emission_wavelength = np.nan
        self.detection_wavelength = np.nan
        self.channel_id = np.nan
        self.detection_type = np.nan
        self.channel_idx_in_ncfile = np.nan
        self.scatterer = np.nan
        self.alt_range = np.nan
        self.pol_channel_conf = np.nan

    @classmethod
    def from_nc_file(cls, nc_file, idx_in_file):
        result = cls()

        def angle_to_time_dependent_var(angle_var, data_var):
            # angle var is the time dependent laser_pointing_angle_of_profiles
            # data_var is the angle dependent variable
            dict = {}
            dict['dims'] = ('time',)
            dict['coords'] = {'time':{'dims': angle_var.coords['time'].dims,
                                      'data': angle_var.coords['time'].data}}

            if 'level' in data_var.dims:
                dict['dims'] = ('time', 'level')
                dict['coords']['level'] = {'dims': data_var.coords['level'].dims,
                                           'data': data_var.coords['level'].data}

            dict['attrs'] = data_var.attrs
            dict['data'] = data_var[angle_var.values.astype(int)].values

            da = xr.DataArray.from_dict(dict)
            return da

        ds = xr.open_dataset(nc_file)

        result.channel_idx_in_ncfile = idx_in_file

        result.ds = ds.range_corrected_signal[idx_in_file].to_dataset(name = 'data')
        result.ds['err'] = ds.range_corrected_signal_statistical_error[idx_in_file]
        #result.data.sel(time='2018-10-17T21:00:00').shape
        result.ds['cf'] = ds.cloud_mask

        result.station_latitude = ds.latitude
        result.station_longitude = ds.longitude
        result.station_altitude = ds.station_altitude
        result.ds['altitude'] = ds.altitude

        result.ds['time_bounds'] = ds.time_bounds

        laser_pointing_angle_of_profiles = ds.laser_pointing_angle_of_profiles

        laser_pointing_angle = ds.laser_pointing_angle
        result.ds['laser_pointing_angle'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,
                                                                        laser_pointing_angle)

        atmospheric_molecular_extinction = ds.atmospheric_molecular_extinction[idx_in_file]
        result.ds['mol_extinction'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,
                                                                  atmospheric_molecular_extinction)

        result.ds['mol_lidar_ratio'] = ds.atmospheric_molecular_lidar_ratio[idx_in_file]

        mol_trasm_at_detection_wl = ds.atmospheric_molecular_trasmissivity_at_detection_wavelength[idx_in_file]
        result.ds['mol_trasm_at_detection_wl'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,
                                                                             mol_trasm_at_detection_wl)

        mol_trasm_at_emission_wl = ds.atmospheric_molecular_trasmissivity_at_detection_wavelength[idx_in_file]
        result.ds['mol_trasm_at_emission_wl'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,
                                                                             mol_trasm_at_emission_wl)

        result.channel_id = ds.range_corrected_signal_channel_id[idx_in_file]
        result.detection_type = ds.range_corrected_signal_detection_mode[idx_in_file]
        result.detection_wavelength = ds.range_corrected_signal_detection_wavelength[idx_in_file]
        result.emission_wavelength = ds.range_corrected_signal_emission_wavelength[idx_in_file]
        result.scatterer = ds.range_corrected_signal_scatterers[idx_in_file]
        result.alt_range = ds.range_corrected_signal_range[idx_in_file]
        result.pol_channel_conf = ds.polarization_channel_configuration[idx_in_file]
        result.pol_channel_geometry = ds.polarization_channel_geometry[idx_in_file]

        result.g = ds.polarization_crosstalk_parameter_g[idx_in_file]
        result.g_stat_err = ds.polarization_crosstalk_parameter_g_statistical_error[idx_in_file]
        result.g_sys_err = ds.polarization_crosstalk_parameter_g_systematic_error[idx_in_file]

        result.h = ds.polarization_crosstalk_parameter_h[idx_in_file]
        result.h_stat_err = ds.polarization_crosstalk_parameter_h_statistical_error[idx_in_file]
        result.h_sys_err = ds.polarization_crosstalk_parameter_h_systematic_error[idx_in_file]


        return result


    @classmethod
    def from_depol_components(cls, transm_sig, refl_sig, dp_cal_params):
        result = cls()

        result = transm_sig.deepcopy() # see also weakref

        HR = refl_sig.h.values
        GR = refl_sig.g.values
        HT = transm_sig.h.values
        GT = transm_sig.values

        K = dp_cal_params.K
        etaS = dp_cal_params.etaS

        result.channel_id.values.append(refl_sig.channel_id.values)
        result.pol_channel_conf.values[:] = TOTAL

        factor = etaS / K * HR
        denom = (HR*GT - HT*GR)

        result.data.values = (factor * transm_sig.data.values - HT * refl_sig.data.values / denom)
        #result.err.values =

        return result

    @property
    def is_WV_sig(self):
        return self.scatterer == WATER_VAPOR

    @property
    def is_elast_sig(self):
        return (self.scatterer & PARTICLE) == PARTICLE

    @property
    def is_Raman_sig(self):
        return (not self.is_WV_sig) & (not self.is_elast_sig)

    @property
    def is_nr_signal(self):
        return self.alt_range == NEAR_RANGE

    @property
    def is_fr_signal(self):
        return self.alt_range == FAR_RANGE

    @property
    def is_total_sig(self):
        return self.pol_channel_conf == TOTAL

    @property
    def is_cross_sig(self):
        return self.pol_channel_conf == CROSS

    @property
    def is_parallel_sig(self):
        return self.pol_channel_conf == PARALLEL


