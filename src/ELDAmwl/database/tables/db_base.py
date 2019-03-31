# # -*- coding: utf-8 -*-
from sqlalchemy import Column, INTEGER, CHAR, DECIMAL, BIGINT, DateTime, text, Text, VARCHAR
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#
# class CalRangeSearchMethod(Base):
#     __tablename__ = '_cal_range_search_methods'
#
#     Id = Column(INTEGER, primary_key=True)
#     method = Column(String(100), nullable=False)
#
#
class ElastBscMethod(Base):
    __tablename__ = '_elast_bsc_methods'

    ID = Column(INTEGER, primary_key=True)
    method = Column(String(100), nullable=False)


class ErrorMethod(Base):
    __tablename__ = '_error_method'

    id = Column(INTEGER, primary_key=True)
    method = Column(String(100), nullable=False)


# class ExtMethod(Base):
#     __tablename__ = '_ext_methods'
#
#     ID = Column(INTEGER, primary_key=True)
#     method = Column(String(100), nullable=False)
#
#
# class ErrorThresholds(Base):
#     __tablename__ = '_error_thresholds'
#     Id = Column(INTEGER, nullable=False),
#     value = Column(Float, nullable=False),
#     name = Column(String(100), nullable=False)
#
#
# class LrInputMethod(Base):
#     __tablename__ = '_lr_input_method'
#
#     id = Column(INTEGER, primary_key=True)
#     method = Column(String(100), nullable=False)
#
#
# class ProductType(Base):
#     __tablename__ = '_product_types'
#
#     ID = Column(INTEGER, primary_key=True)
#     product_type = Column(String(100), nullable=False)
#     nc_file_id = Column(CHAR(1), nullable=False)
#     processor_ID = Column(INTEGER, nullable=False)
#
#
# class RamBscMethod(Base):
#     __tablename__ = '_ram_bsc_methods'
#
#     ID = Column(INTEGER, primary_key=True)
#     method = Column(String(100), nullable=False)
#
#
# class ScatMechanisms(Base):
#     __tablename__ = '_scat_mechanisms'
#
#     ID = Column(String(10), nullable=False),
#     ScatType = Column(String(100), nullable=False)
#
#
# class SignalType(Base):
#     __tablename__ = '_signal_types'
#
#     ID = Column(INTEGER, primary_key=True)
#     signal_types = Column(String(100), nullable=False)
#
#
# class Usecase(Base):
#     __tablename__ = '_usecases'
#
#     ID_count = Column(INTEGER, primary_key=True)
#     ID = Column(INTEGER, nullable=False)
#     usecase = Column(String(100), nullable=False)
#     _prod_type_ID = Column(INTEGER, nullable=False, index=True)
#
#
# class BscCalibrOption(Base):
#     __tablename__ = 'bsc_calibr_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     LowestHeight = Column(DECIMAL(10, 4), nullable=False)
#     TopHeight = Column(DECIMAL(10, 4), nullable=False)
#     WindowWidth = Column(DECIMAL(10, 4), nullable=False)
#     calValue = Column(DECIMAL(10, 4), nullable=False)
#     _calRangeSearchMethod_ID = Column(INTEGER, nullable=False)
#
#
# class DepolBscOption(Base):
#     __tablename__ = 'depol_bsc_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _backscatter_options_product_ID = Column(INTEGER, nullable=False)
#     _error_method_ID = Column(INTEGER, nullable=False)
#     min_BscRatio_for_PLDR = Column(DECIMAL(10, 4), nullable=False)
#
#
# class ElastBackscatterOption(Base):
#     __tablename__ = 'elast_backscatter_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _elast_bsc_method_ID = Column(INTEGER, nullable=False, index=True)
#     _bsc_calibr_options_ID = Column(INTEGER, nullable=False, index=True)
#     _error_method_ID = Column(INTEGER, nullable=False, index=True)
#     _lr_input_method_id = Column(INTEGER, nullable=False, index=True)
#     fixed_lr = Column(DECIMAL(10, 4), nullable=False)
#     fixed_lr_error = Column(DECIMAL(10, 4), nullable=False)
#     _iter_bsc_options_id = Column(INTEGER, nullable=False, index=True)
#
#
# class EldaProduct(Base):
#     __tablename__ = 'elda_products'
#
#     ID = Column(BIGINT, primary_key=True)
#     __measurements__ID = Column(String(15), index=True)
#     _product_ID = Column(INTEGER, nullable=False, index=True)
#     InscribedAt = Column(DateTime, nullable=False)
#     _scc_version_ID = Column(INTEGER)
#     filename = Column(String(100), nullable=False)
#
#
# class ExtBscOption(Base):
#     __tablename__ = 'ext_bsc_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _extinction_options_product_ID = Column(INTEGER, nullable=False, index=True)
#     _raman_backscatter_options_product_ID = Column(INTEGER, nullable=False, index=True)
#     _error_method_ID = Column(INTEGER, nullable=False, index=True)
#
#
# class ExtinctionOption(Base):
#     __tablename__ = 'extinction_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _ext_method_ID = Column(INTEGER, nullable=False, index=True)
#     _error_method_ID = Column(INTEGER, nullable=False, index=True)
#     _overlap_file_ID = Column(INTEGER, nullable=False, index=True)
#     angstroem = Column(DECIMAL(10, 4), nullable=False)
#
#
# class HoiChannel(Base):
#     __tablename__ = 'hoi_channels'
#
#     ID = Column(INTEGER, primary_key=True)
#     string_ID = Column(String(20), unique=True)
#     name = Column(String(100), nullable=False)
#     _telescope_ID = Column(INTEGER, nullable=False, index=True)
#     _laser_ID = Column(INTEGER, nullable=False, index=True)
#     _scat_mechanism_ID = Column(String(10), nullable=False, index=True)
#     IF_center = Column(DECIMAL(10, 4), nullable=False)
#     IF_FWHM = Column(DECIMAL(10, 4), nullable=False)
#     emission_wavelength = Column(DECIMAL(10, 4), nullable=False)
#     FOV = Column(DECIMAL(10, 4), nullable=False)
#     raw_range_resolution = Column(DECIMAL(10, 4), nullable=False)
#     _dead_time_corr_type_id = Column(INTEGER, nullable=False, index=True)
#     dead_time = Column(DECIMAL(10, 4))
#     trigger_delay = Column(DECIMAL(10, 4), nullable=False)
#     trigger_delay_interp_id = Column(INTEGER)
#     _background_mode_id = Column(INTEGER, nullable=False, index=True)
#     _signal_type_id = Column(INTEGER, nullable=False, index=True)
#     _detection_mode_ID = Column(String(5), nullable=False, index=True)
#     gluing_option_ID = Column(INTEGER, index=True)
#     beam_telescope_distance = Column(Float)
#     separation_passband_bandwidth = Column(Float)
#     separation_transmission = Column(Float)
#     separation_transm_pol_parallel = Column(Float)
#     separation_transm_pol_cross = Column(Float)
#     out_of_band_suppression = Column(String(45))
#     passband_bandwidth = Column(Float)
#     passband_transmission = Column(Float)
#     out_of_band_blocking = Column(String(45))
#     polarization_separation = Column(String(45))
#     polarization_transmission_parallel = Column(Float)
#     polarization_transmission_cross = Column(Float)
#     neutral_density_filter_OD = Column(String(45))
#     detector_type = Column(String(100))
#     detector_manufacturer = Column(String(100))
#     detector_model = Column(String(100))
#     additional_features = Column(String(100))
#     daytime_capability = Column(INTEGER)
#     transimpedance_amplifier = Column(INTEGER)
#     transimpedance_gain = Column(Float)
#     transimpedance_bandwidth = Column(Float)
#     output_impedance = Column(Float)
#     analog_sampling_rate = Column(Float)
#     bandwidth = Column(Float)
#     AD_bits = Column(INTEGER)
#     input_termination = Column(Float)
#     max_input_voltage = Column(Float)
#     photon_counting_count_rate = Column(Float)
#     data_acquisition_manufacturer = Column(String(100))
#     data_acquisition_model = Column(String(100))
#     raw_data_time_resolution = Column(Float)
#     raw_data_altitude_range = Column(Float)
#     entry_update_date = Column(DateTime)
#     exclude_from_hoi = Column(INTEGER, nullable=False)
#     description = Column(Text)
#     pre_trigger_data = Column(INTEGER)
#     wavelength_separation = Column(String(45))
#     __hoi_stations__ID = Column(CHAR(3))
#
#
# class HoiLidarVersion(Base):
#     __tablename__ = 'hoi_lidar_versions'
#
#     ID = Column(INTEGER, primary_key=True)
#     name = Column(String(20), nullable=False)
#     _hoi_lidar_ID = Column(INTEGER, nullable=False)
#     description = Column(Text)
#     exclude_from_hoi = Column(INTEGER, nullable=False)
#     enable_quicklook = Column(INTEGER, nullable=False)
#     start_date = Column(DateTime, nullable=False)
#     stop_date = Column(DateTime)
#     creation_date = Column(DateTime, nullable=False)
#     update_date = Column(DateTime, nullable=False)
#
#
# class HoiLidar(Base):
#     __tablename__ = 'hoi_lidars'
#
#     ID = Column(INTEGER, primary_key=True)
#     __hoi_stations__ID = Column(CHAR(3))
#     name = Column(String(100), nullable=False)
#     PI = Column(String(100), nullable=False)
#     quicklook_name = Column(String(10), nullable=False)
#     enable_quicklook = Column(INTEGER, nullable=False)
#
#
# class HoiStation(Base):
#     __tablename__ = 'hoi_stations'
#
#     ID = Column(CHAR(3), primary_key=True)
#     name = Column(String(100), nullable=False)
#     Latitude = Column(Float, nullable=False)
#     Longitude = Column(Float, nullable=False)
#     _height_asl = Column(Float, nullable=False)
#     PI_first_name = Column(String(100))
#     PI_last_name = Column(String(100))
#     PI_phone = Column(String(100))
#     PI_mail = Column(String(200))
#     _country_id = Column(INTEGER, nullable=False)
#     enable_quicklook = Column(INTEGER, nullable=False)
#     institute_name = Column(VARCHAR(200), nullable=False)
#     institute_name_acronym = Column(String(10))
#     description = Column(Text)
#     _actris_status_id = Column(INTEGER)
#     _lidar_network_id = Column(INTEGER, nullable=False)
#     cloudnet_station_id = Column(String(100))
#     entry_update_date = Column(DateTime)
#     exclude_from_hoi = Column(INTEGER, nullable=False)
#     PI_affiliation = Column(String(200))
#     PI_affiliation_acronym = Column(String(10))
#     PI_address = Column(String(200))
#
#
# class HoiSystem(Base):
#     __tablename__ = 'hoi_systems'
#
#     ID = Column(INTEGER, primary_key=True)
#     __hoi_stations__ID = Column(CHAR(3), index=True)
#     _hoi_lidar_version_ID = Column(INTEGER, nullable=False)
#     name = Column(String(100), nullable=False)
#     Configuration = Column(String(100), nullable=False)
#     height_asl = Column(Float, nullable=False)
#     Configuration_from = Column(DateTime)
#     Configuration_to = Column(DateTime)
#     telecover_test_passed = Column(DateTime)
#     testxy_passed_at = Column(DateTime)
#     PI = Column(String(100), nullable=False)
#     system_is_transportable = Column(INTEGER)
#     transportation_type = Column(String(100))
#     description = Column(Text)
#     sun_photometer_type = Column(String(45))
#     sun_photometer_distance = Column(Float)
#     radiosounding_location = Column(String(100))
#     radiosounding_distance = Column(Float)
#     radiosounding_frequency = Column(String(100))
#     lidar_pointing_angle = Column(Float)
#     scanning_elevation_from = Column(Float)
#     scanning_elevation_to = Column(Float)
#     scanning_azimuth_from = Column(Float)
#     scanning_azimuth_to = Column(Float)
#     unattended_operation = Column(INTEGER)
#     automated_functions = Column(String(100))
#     exclude_from_hoi = Column(INTEGER, nullable=False)
#     entry_update_date = Column(DateTime)
#     Latitude = Column(Float)
#     Longitude = Column(Float)
#     Location = Column(String(200))
#     enable_quicklook = Column(INTEGER, nullable=False)
#
#
# class IterBackscatterOption(Base):
#     __tablename__ = 'iter_backscatter_options'
#
#     id = Column(INTEGER, primary_key=True)
#     iter_conv_crit = Column(DECIMAL(10, 4), nullable=False, server_default=text("'0.0100'"))
#     _ram_bsc_method_id = Column(INTEGER, nullable=False)
#     max_iteration_count = Column(INTEGER, nullable=False, server_default=text("'10'"))
#
#
# class LidarConstant(Base):
#     __tablename__ = 'lidar_constants'
#
#     ID = Column(BIGINT, primary_key=True)
#     __measurements__ID = Column(String(15), index=True)
#     _product_ID = Column(INTEGER, nullable=False, index=True)
#     _channel_ID = Column(INTEGER, nullable=False)
#     _hoi_system_ID = Column(INTEGER, nullable=False)
#     filename = Column(String(100), nullable=False)
#     calibr_factor = Column(Float(asdecimal=True))
#     calibr_factor_sys_err = Column(Float(asdecimal=True))
#     calibr_factor_stat_err = Column(Float(asdecimal=True))
#     lidar_const = Column(Float(asdecimal=True))
#     lidar_const_sys_err = Column(Float(asdecimal=True))
#     lidar_const_stat_err = Column(Float(asdecimal=True))
#     detection_wavelength = Column(Float(asdecimal=True))
#     profile_start_time = Column(DateTime, nullable=False)
#     profile_end_time = Column(DateTime, nullable=False)
#     calibr_window_bottom = Column(Float(asdecimal=True))
#     calibr_window_top = Column(Float(asdecimal=True))
#     InscribedAt = Column(DateTime, nullable=False)
#     ELDA_version = Column(CHAR(50))
#     is_latest_value = Column(INTEGER, nullable=False)
#
#
# class LidarratioFile(Base):
#     __tablename__ = 'lidarratio_files'
#
#     ID = Column(INTEGER, primary_key=True)
#     __hoi_stations__ID = Column(CHAR(3))
#     start = Column(DateTime)
#     stop = Column(DateTime)
#     filename = Column(String(100))
#     _interpolation_id = Column(INTEGER)
#     submission_date = Column(DateTime)
#     status = Column(String(20), nullable=False)
#
#
# class McOption(Base):
#     __tablename__ = 'mc_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     iteration_count = Column(INTEGER, nullable=False)
#
#
# class MeasurementLog(Base):
#     __tablename__ = 'measurement_logs'
#
#     ID = Column(BIGINT, primary_key=True)
#     __measurements__ID = Column(String(15))
#     product_ID = Column(INTEGER)
#     level = Column(INTEGER, nullable=False)
#     module = Column(INTEGER, nullable=False)
#     module_version = Column(String(45))
#     datetime = Column(DateTime, nullable=False)
#     message = Column(String(400), nullable=False)
#
#
# class OverlapFile(Base):
#     __tablename__ = 'overlap_files'
#
#     ID = Column(INTEGER, primary_key=True)
#     __hoi_stations__ID = Column(CHAR(3))
#     start = Column(DateTime)
#     stop = Column(DateTime)
#     filename = Column(String(100), nullable=False)
#     _interpolation_id = Column(INTEGER)
#     submission_date = Column(DateTime)
#     status = Column(String(20), nullable=False)
#
#
# class PolarizationCalibrationCorrectionFactor(Base):
#     __tablename__ = 'polarization_calibration_correction_factors'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     correction = Column(Float(asdecimal=True), nullable=False)
#     correction_statistical_error = Column(Float(asdecimal=True), nullable=False)
#     correction_systematic_error = Column(Float(asdecimal=True), nullable=False)
#     wavelength = Column(Float(asdecimal=True), nullable=False)
#     _range_ID = Column(INTEGER, nullable=False)
#     correction_date = Column(DateTime, nullable=False)
#     correction_submission_date = Column(DateTime, nullable=False)
#
#
# class PolarizationCalibration(Base):
#     __tablename__ = 'polarization_calibrations'
#
#     ID = Column(INTEGER, primary_key=True)
#     __measurements__ID = Column(String(15))
#     _product_ID = Column(INTEGER, nullable=False)
#     calibration = Column(Float(asdecimal=True), nullable=False)
#     calibration_statistical_error = Column(Float(asdecimal=True), nullable=False)
#     calibration_systematic_error = Column(Float(asdecimal=True), nullable=False)
#     _calibration_type_ID = Column(INTEGER, nullable=False)
#     wavelength = Column(Float(asdecimal=True))
#     _range_ID = Column(INTEGER, nullable=False)
#     calibration_date = Column(DateTime, nullable=False)
#     calibration_submission_date = Column(DateTime, nullable=False)
#     _scc_version_ID = Column(INTEGER)
#     filename = Column(String(200), nullable=False)
#
#
# class PolarizationCalibrationsProduct(Base):
#     __tablename__ = 'polarization_calibrations_products'
#
#     ID = Column(INTEGER, primary_key=True)
#     _calibration_product_ID = Column(INTEGER, nullable=False)
#     _product_to_calibrate_ID = Column(INTEGER, nullable=False)
#
#
# class PolarizationCrosstalkParameter(Base):
#     __tablename__ = 'polarization_crosstalk_parameters'
#
#     ID = Column(INTEGER, primary_key=True)
#     G = Column(DECIMAL(10, 8), nullable=False)
#     G_statistical_error = Column(DECIMAL(10, 8), nullable=False)
#     G_systematic_error = Column(DECIMAL(10, 8), nullable=False)
#     H = Column(DECIMAL(10, 8), nullable=False)
#     H_statistical_error = Column(DECIMAL(10, 8), nullable=False)
#     H_systematic_error = Column(DECIMAL(10, 8), nullable=False)
#     measurement_date = Column(DateTime, nullable=False)
#     submission_date = Column(DateTime, nullable=False)
#     _channel_ID = Column(INTEGER, nullable=False)
#
#
# class PolarizationOption(Base):
#     __tablename__ = 'polarization_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _pol_calibration_method_ID = Column(INTEGER, nullable=False)
#     _crosstalk_parameter_method_ID = Column(INTEGER, nullable=False)
#     _correction_factor_method_ID = Column(INTEGER, nullable=False)
#
#
# class PreparedSignalFile(Base):
#     __tablename__ = 'prepared_signal_files'
#
#     ID = Column(INTEGER, primary_key=True)
#     __measurements__ID = Column(String(15), index=True)
#     _Product_ID = Column(INTEGER, nullable=False, index=True)
#     _scc_version_ID = Column(INTEGER)
#     filename = Column(String(100), nullable=False)
#
#
# class ProductChannel(Base):
#     __tablename__ = 'product_channels'
#
#     ID = Column(INTEGER, primary_key=True)
#     _prod_ID = Column(INTEGER, nullable=False, index=True)
#     _channel_ID = Column(INTEGER, nullable=False, index=True)
#
#
# class ProductOption(Base):
#     __tablename__ = 'product_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _lowrange_error_threshold_ID = Column(INTEGER, nullable=False, index=True)
#     _highrange_error_threshold_ID = Column(INTEGER, nullable=False, index=True)
#     detection_limit = Column(DECIMAL(11, 11), nullable=False)
#     min_height = Column(DECIMAL(10, 4), nullable=False)
#     max_height = Column(DECIMAL(10, 4), nullable=False)
#     preprocessing_integration_time = Column(INTEGER, nullable=False)
#     preprocessing_vertical_resolution = Column(DECIMAL(10, 4), nullable=False)
#     interpolation_id = Column(INTEGER)
#
#
# class Product(Base):
#     __tablename__ = 'products'
#
#     ID = Column(INTEGER, primary_key=True)
#     _usecase_ID = Column(INTEGER)
#     _prod_type_ID = Column(INTEGER, nullable=False, index=True)
#     __hoi_stations__ID = Column(CHAR(3))
#     _hirelpp_product_option_ID = Column(INTEGER)
#
#
# class RamanBackscatterOption(Base):
#     __tablename__ = 'raman_backscatter_options'
#
#     ID = Column(INTEGER, primary_key=True)
#     _product_ID = Column(INTEGER, nullable=False)
#     _ram_bsc_method_ID = Column(INTEGER, nullable=False, index=True)
#     _bsc_calibr_options_ID = Column(INTEGER, nullable=False, index=True)
#     _error_method_ID = Column(INTEGER, nullable=False, index=True)
#
#
# class SccVersion(Base):
#     __tablename__ = 'scc_version'
#
#     ID = Column(INTEGER, primary_key=True)
#     scc_version = Column(String(10))
#     pre_process_version = Column(String(10))
#     elda_version = Column(String(10))
#     daemon_version = Column(String(10))
#     scc_db_version = Column(String(10))
#     web_interface_version = Column(String(10))
#     release_date = Column(DateTime, nullable=False)
#     scc_calibrator_version = Column(String(10))
#     hirelpp_version = Column(String(10))
#     cloudmask_version = Column(String(10))
#     elquick_version = Column(String(10))
#     elic_version = Column(String(10))
#     is_latest = Column(INTEGER, nullable=False)
#
#
# class SoundingFile(Base):
#     __tablename__ = 'sounding_files'
#
#     ID = Column(INTEGER, primary_key=True)
#     __hoi_stations__ID = Column(CHAR(3))
#     start = Column(DateTime)
#     stop = Column(DateTime)
#     filename = Column(String(100))
#     _interpolation_id = Column(INTEGER)
#     submission_date = Column(DateTime)
#     status = Column(String(20), nullable=False)
#
#
# class SystemChannel(Base):
#     __tablename__ = 'system_channel'
#
#     Id = Column(INTEGER, primary_key=True)
#     _system_ID = Column(INTEGER, nullable=False, index=True)
#     _channel_ID = Column(INTEGER, nullable=False, index=True)
#
#
# class SystemProduct(Base):
#     __tablename__ = 'system_product'
#
#     ID = Column(INTEGER, primary_key=True)
#     _system_ID = Column(INTEGER, nullable=False, index=True)
#     _Product_ID = Column(INTEGER, nullable=False, index=True)
#
#
# class Station(Base):
#     __tablename__ = 'station'
#     id = Column(Integer, primary_key=True)
#     wmo = Column(String, nullable=False, unique=True)
#     wigos = Column(String, nullable=False, unique=True)
#     name = Column(String, nullable=False)
#     latitude = Column(Float, nullable=False)
#     longitude = Column(Float, nullable=False)
#     altitude = Column(Float, nullable=False)
#     nws = Column(String, nullable=False)
#     description = Column(String, nullable=True)
#     url = Column(String, nullable=True)
