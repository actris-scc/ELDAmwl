# -*- coding: utf-8 -*-
"""Classes for signals"""

from ELDAmwl.columns import Columns
from ELDAmwl.constants import CROSS
from ELDAmwl.constants import FAR_RANGE
from ELDAmwl.constants import NEAR_RANGE
from ELDAmwl.constants import PARALLEL
from ELDAmwl.constants import PARTICLE
from ELDAmwl.constants import TOTAL
from ELDAmwl.constants import WATER_VAPOR

import numpy as np
import xarray as xr


class Signals(Columns):

    def __init__(self):
        super(Signals, self).__init__()
        self.emission_wavelength = np.nan
        self.detection_wavelength = np.nan
        self.channel_id = np.nan
        self.channel_id_str = ''
        self.detection_type = np.nan
        self.channel_idx_in_ncfile = np.nan
        self.scatterer = np.nan
        self.alt_range = np.nan
        self.pol_channel_conf = np.nan

    @classmethod
    def from_nc_file(cls, nc_ds, idx_in_file):
        """

        :param nc_ds: netcdf dataset = content of the netcdf file
                                        as Xarray dataset
        :param idx_in_file:
        :return:
        """
        result = cls()

        def angle_to_time_dependent_var(angle_var, data_var):
            # angle var is the time dependent laser_pointing_angle_of_profiles
            # data_var is the angle dependent variable
            dict = {}
            dict['dims'] = ('time',)
            dict['coords'] = {'time': {'dims': angle_var.coords['time'].dims,
                                       'data': angle_var.coords['time'].data}}

            if 'level' in data_var.dims:
                dict['dims'] = ('time', 'level')
                dict['coords']['level'] = {'dims': data_var.coords['level'].dims,  # noqa E501
                                           'data': data_var.coords['level'].data}  # noqa E501

            dict['attrs'] = data_var.attrs
            dict['data'] = data_var[angle_var.values.astype(int)].values

            da = xr.DataArray.from_dict(dict)
            return da

        result.channel_idx_in_ncfile = idx_in_file

        result.ds = nc_ds.range_corrected_signal[idx_in_file].to_dataset(name='data')  # noqa E501
        result.ds['err'] = nc_ds.range_corrected_signal_statistical_error[idx_in_file]  # noqa E501
        result.ds['cf'] = nc_ds.cloud_mask.astype(int)

        result.station_latitude = nc_ds.latitude
        result.station_longitude = nc_ds.longitude
        result.station_altitude = nc_ds.station_altitude
        result.ds['altitude'] = nc_ds.altitude

        result.ds['time_bounds'] = nc_ds.time_bounds

        laser_pointing_angle_of_profiles = nc_ds.laser_pointing_angle_of_profiles  # noqa E501

        laser_pointing_angle = nc_ds.laser_pointing_angle
        result.ds['laser_pointing_angle'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                        laser_pointing_angle)  # noqa E501

        atmospheric_molecular_extinction = nc_ds.atmospheric_molecular_extinction[idx_in_file]  # noqa E501
        result.ds['mol_extinction'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                  atmospheric_molecular_extinction)  # noqa E501

        result.ds['mol_lidar_ratio'] = nc_ds.atmospheric_molecular_lidar_ratio[idx_in_file]  # noqa E501

        mol_trasm_at_detection_wl = nc_ds.atmospheric_molecular_trasmissivity_at_detection_wavelength[idx_in_file]  # noqa E501
        result.ds['mol_trasm_at_detection_wl'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                             mol_trasm_at_detection_wl)  # noqa E501

        mol_trasm_at_emission_wl = nc_ds.atmospheric_molecular_trasmissivity_at_detection_wavelength[idx_in_file]  # noqa E501
        result.ds['mol_trasm_at_emission_wl'] = angle_to_time_dependent_var(laser_pointing_angle_of_profiles,  # noqa E501
                                                                            mol_trasm_at_emission_wl)  # noqa E501

        result.channel_id = nc_ds.range_corrected_signal_channel_id[idx_in_file].astype(int)  # noqa E501
        result.detection_type = nc_ds.range_corrected_signal_detection_mode[idx_in_file].astype(int)  # noqa E501
        result.detection_wavelength = nc_ds.range_corrected_signal_detection_wavelength[idx_in_file]  # noqa E501
        result.emission_wavelength = nc_ds.range_corrected_signal_emission_wavelength[idx_in_file]  # noqa E501
        result.scatterer = nc_ds.range_corrected_signal_scatterers[idx_in_file].astype(int)  # noqa E501
        result.alt_range = nc_ds.range_corrected_signal_range[idx_in_file].astype(int)  # noqa E501
        result.pol_channel_conf = nc_ds.polarization_channel_configuration[idx_in_file].astype(int)  # noqa E501
        result.pol_channel_geometry = nc_ds.polarization_channel_geometry[idx_in_file].astype(int)  # noqa E501

        result.g = nc_ds.polarization_crosstalk_parameter_g[idx_in_file]
        result.g_stat_err = nc_ds.polarization_crosstalk_parameter_g_statistical_error[idx_in_file]  # noqa E501
        result.g_sys_err = nc_ds.polarization_crosstalk_parameter_g_systematic_error[idx_in_file]  # noqa E501

        result.h = nc_ds.polarization_crosstalk_parameter_h[idx_in_file]
        result.h_stat_err = nc_ds.polarization_crosstalk_parameter_h_statistical_error[idx_in_file]  # noqa E501
        result.h_sys_err = nc_ds.polarization_crosstalk_parameter_h_systematic_error[idx_in_file]  # noqa E501

        result.channel_id_str = str(result.channel_id.values)


        return result

    @classmethod
    def from_depol_components(cls, transm_sig, refl_sig, dp_cal_params):
        result = cls()

        result = transm_sig.deepcopy()  # see also weakref

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

        result.data.values = (factor * transm_sig.data.values -
                              HT * refl_sig.data.values / denom)
        # result.err.values =

        return result


    def register(self, storage, p_params):
        storage.products()[p_params.prod_id_str].signals[self.channel_id_str] = self
        p_params.general_params.signals.append(self.channel_id_str)

    def assign_to_signal_list(self, sig_list, fquery):
        """

        Args:
            sig_list: pd.Dataframe with a list of signals and header information
            fquery:

        Returns:

        """
        sig_list.loc[len(sig_list.index)] = {'id': str(self.channel_id.values),
             'em_wl': float(self.emission_wavelength.values),
             'det_wl': float(self.detection_wavelength.values),
             'det_type': int(self.detection_type.values),
             'scatterer': int(self.scatterer.values),
             'alt_range': int(self.alt_range.values),
             'elast': self.is_elast_sig,
             'Raman': self.is_Raman_sig,
             'wv': self.is_WV_sig,
             'nr': self.is_nr_signal,
             'fr': self.is_fr_signal,
             'total': self.is_total_sig,
             'cross': self.is_cross_sig,
             'parallel': self.is_parallel_sig,
             }

    @property
    def range(self):
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

