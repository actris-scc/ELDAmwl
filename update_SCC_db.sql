--/*
--* =============================================
--* create a new product and add it to system 182
--* =============================================
--*/
--
--INSERT INTO `products` (`_usecase_ID`, `_prod_type_ID`, `__hoi_stations__ID`, `_hirelpp_product_option_ID`, `_ltool_product_option_ID`) VALUES
--	(-1, 12, 'hpb', NULL, NULL);
--select max(ID) into @mwlid from products;
--INSERT INTO `system_product` (`_system_ID`, `_Product_ID`) VALUES
--	(182, @mwlid);
--
--/*
--* ===========================================
--* add columns to _product_types and fill them
--* ===========================================
--*/
--
--ALTER TABLE `_product_types`
--ADD COLUMN description VARCHAR(100) NOT NULL DEFAULT '',
--ADD COLUMN is_mwl_only_product INT(1) NOT NULL DEFAULT '0' COMMENT 'True for products, which are derived by ELDAmwl only. Can be used by user-interface',
--ADD COLUMN is_in_mwl_products INT(1) NOT NULL DEFAULT '0' COMMENT 'True for all products which can be derived by ELDAmwl (basic and derived ones)',
--ADD COLUMN is_basic_product INT(1) NOT NULL DEFAULT '0' COMMENT 'True for all products, which are not calculated from other products (e.g., VLDR, extinction, backscatter). Lidar ratio, PLDR, Angstroem exponents etc. are NOT basic products.';
--
--UPDATE `_product_types`
--set description = 'particle extinction coefficient (Raman)', is_in_mwl_products = 1, is_basic_product=1 where ID=1;
--UPDATE `_product_types`
--set description = 'particle lidar ratio (Raman)', is_in_mwl_products = 1 where ID=2;
--UPDATE `_product_types`
--set description = 'particle backscatter coefficient (Raman)', is_in_mwl_products = 1, is_basic_product=1 where ID=0;
--UPDATE `_product_types`
--set description = 'particle backscatter coefficient (elast.)', is_in_mwl_products = 1, is_basic_product=1 where ID=3;
--UPDATE `_product_types`
--set description = 'particle backscatter coefficient (elast.)', is_in_mwl_products = 1, is_basic_product=1 where ID=3;
--
--INSERT INTO `_product_types` (`ID`, `product_type`, `description`, `nc_file_id`, `processor_ID`, `is_mwl_only_product`, `is_in_mwl_products`, `is_basic_product`) VALUES
--(12, 'multi-wavelength product', 'multi-wavelength product', '', 0, 0, 0, 0),
--(13, 'Angstroem exponent', 'Angstroem exponent', '', 0, 1, 1, 0),
--(14, 'color ratio', 'color ratio', '', 0, 1, 1, 0),
--(15, 'vol depol ratio', 'volume linear depolarization ratio', '', 0, 1, 1, 1),
--(16, 'part depol ratio', 'particle linear depolarization ratio', '', 0, 1, 1, 0);
--
--/*
--* ===================================================================
--* create a new table connecting the mwl products with single products
--* and fill the table with example data for system 182
--* ===================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `mwlproduct_product` (
--  `ID` int(11) NOT NULL AUTO_INCREMENT,
--  `_mwl_product_ID` int(11) NOT NULL DEFAULT '0',
--  `_Product_ID` int(11) NOT NULL DEFAULT '0',
--  `create_with_hr` int(1) NOT NULL DEFAULT '0',
--  `create_with_lr` int(1) NOT NULL DEFAULT '1',
--  PRIMARY KEY (`ID`)
--);
--
--INSERT INTO `mwlproduct_product` (`_mwl_product_ID`, `_Product_ID`, `create_with_hr`, `create_with_lr`) VALUES
--	(@mwlid, 378, 1, 0),
--	(@mwlid, 379, 0, 1),
--	(@mwlid, 324, 1, 1),
--	(@mwlid, 330, 1, 1),
--	(@mwlid, 377, 0, 1);
--
--/*
--* ===================================================================================
--* create a new table with options of angstroem exponent products
--* create 2 new angstroem exponent products in table products
--* fill the table angstroem_exp_options with data of these 2 examples (for system 182)
--* ===================================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `angstroem_exp_options` (
--  `ID` int(11) NOT NULL AUTO_INCREMENT,
--  `_product_ID` int(11) NOT NULL DEFAULT '-1',
--  `_lambda1_product_ID` int(11) NOT NULL DEFAULT '-1',
--  `_lambda2_product_ID` int(11) NOT NULL DEFAULT '-1',
--  `_error_method_ID` int(11) NOT NULL DEFAULT '-1',
--  `min_BscRatio_for_AE` decimal(10,4) NOT NULL DEFAULT '1.0000',
--  PRIMARY KEY (`ID`)
--);
--INSERT INTO `products` (`_usecase_ID`, `_prod_type_ID`, `__hoi_stations__ID`, `_hirelpp_product_option_ID`, `_ltool_product_option_ID`) VALUES
--	(-1, 13, 'hpb', NULL, NULL);
--select max(ID) into @ae1_id from products;
--INSERT INTO `products` (`_usecase_ID`, `_prod_type_ID`, `__hoi_stations__ID`, `_hirelpp_product_option_ID`, `_ltool_product_option_ID`) VALUES
--	(-1, 13, 'hpb', NULL, NULL);
--select max(ID) into @ae2_id from products;
--
--INSERT INTO `angstroem_exp_options` (`_product_ID`, `_lambda1_product_ID`, `_lambda2_product_ID`, `_error_method_ID`, `min_BscRatio_for_AE`) VALUES
--	(@ae1_id, 378, 324, 1, 1.0000);
--
--INSERT INTO `angstroem_exp_options` (`_product_ID`, `_lambda1_product_ID`, `_lambda2_product_ID`, `_error_method_ID`, `min_BscRatio_for_AE`) VALUES
--	(@ae2_id, 377, 380, 1, 1.0000);
--
--/*
--* ===================================================================================
--* create a new table with options of color ratio products
--* create a new color ratio product in table products
--* fill the table color_ratio_options with data of this example (for system 182)
--* ===================================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `color_ratio_options` (
--  `ID` int(11) NOT NULL AUTO_INCREMENT,
--  `_product_ID` int(11) NOT NULL DEFAULT '-1',
--  `_nominator_product_ID` int(11) NOT NULL DEFAULT '-1',
--  `_denominator_product_ID` int(11) NOT NULL DEFAULT '-1',
--  `_error_method_ID` int(11) NOT NULL DEFAULT '-1',
--  `min_BscRatio_for_CR` decimal(10,4) NOT NULL DEFAULT '1.0000',
--  PRIMARY KEY (`ID`)
--);
--
--INSERT INTO `products` (`_usecase_ID`, `_prod_type_ID`, `__hoi_stations__ID`, `_hirelpp_product_option_ID`, `_ltool_product_option_ID`) VALUES
--	(-1, 14, 'hpb', NULL, NULL);
--select max(ID) into @cr_id from products;
--
--INSERT INTO `color_ratio_options` (`_product_ID`, `_nominator_product_ID`, `_denominator_product_ID`, `_error_method_ID`, `min_BscRatio_for_CR`) VALUES
--	(@cr_id, 379, 381, 1, 1.0000);
--
--/*
--* ===================================================================================
--* add a column with a numeric id to the measurements table
--* ===================================================================================
--*/
--
--ALTER TABLE `measurements`
--ADD COLUMN `num_id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT first;
--ALTER TABLE `measurements` DROP PRIMARY KEY, ADD PRIMARY KEY (num_id);
--
--/*
--* ===================================================================================
--* NEW:
--* create a table which makes the connection between method names and python classnames in ELDAmwl
--* and fill this table
--* ===================================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `eldamwl_class_names` (
--  `ID` int(11) NOT NULL AUTO_INCREMENT,
--  `method` varchar(100) NOT NULL COMMENT 'link to the "*method" columns in various method tables',
--  `classname` varchar(100) NOT NULL COMMENT 'the name of the python class in ELDAmwl which performs the calculation',
--  PRIMARY KEY (`id`) )
--  COMMENT 'This table provides the names of python classes in ELDAmwl where the different methods are implemented. The column method is a link to the columns "method", "method_for_getting_used_binres", and "method_for_getting_effective_binres" in tables "_ext_methods", "_elast_bsc_methods", "_cal_range_search_methods", "_ram_bsc_methods", "_smooth_methods"';
--
--INSERT INTO `eldamwl_class_names` (`id`, `method`, `classname`) VALUES
--    (1, 'weighted linear fit', 'WeightedLinearFit'),
--    (2, 'non-weighted linear fit', 'NonWeightedLinearFit'),
--    (3, 'used_bin_resolution_of_linear_fit', 'LinFitUsedBinRes'),
--    (4, 'effective_bin_resolution_of_linear_fit', 'LinFitEffBinRes'),
--    (5, 'Savitzky-Golay', 'SmoothSavGolay'),
--    (6, 'sliding average', 'SmoothSlidingAverage'),
--    (7, 'used_bin_resolution_of_savitzky_golay_smoothing', 'SavGolayUsedBinRes'),
--    (8, 'used_bin_resolution_of_sliding_average', 'SlidAvrgUsedBinRes'),
--    (9, 'used_bin_resolution_of_savitzky_golay_smoothing', 'SavGolayEffBinRes'),
--    (10, 'used_bin_resolution_of_sliding_average', 'SlidAvrgEffBinRes'),
--    (11, 'Ansmann method', 'CalcRamanBscProfileAsAnsmann'),
--    (12, 'via backscatter ratio', 'CalcRamanBscProfileViaBR'),
--    (13, 'minimum', 'FindCalibrWindowMinimum'),
--    (14, 'fit-slope', 'FindCalibrationWindowFitSlope'),
--    (15, 'Klett', 'CalcBscProfileKF'),
--    (16, 'iter', 'CalcBscProfileIter');
--
--/*
--* ===================================================================================
--* table _ext_methods:
--* add comments to the table and the existing method column
--* add two additional columns describing the methods for handling effective vertical resolution
--* fill the new columns
--* ===================================================================================
--*/
--
--ALTER TABLE `_ext_methods`
--COMMENT 'columns "method", "method_for_getting_used_binres", and "method_for_getting_effective_binres" are linked to eldamwl_class_names.method. The table eldamwl_class_names provides the names of python classes in ELDAmwl where the method is implemented';
--ALTER TABLE `_ext_methods`
--MODIFY COLUMN `method` varchar(100) NOT NULL DEFAULT '' COMMENT 'method for calculating the derivative';
--ALTER TABLE `_ext_methods`
--ADD COLUMN `method_for_getting_used_binres` varchar(100) NOT NULL DEFAULT '' COMMENT 'method for calculating how many bins needs to be used in the calculation of the derivative in order to achieve a given effective vertical resolution.';
--ALTER TABLE `_ext_methods`
--ADD COLUMN `method_for_getting_effective_binres` varchar(100) NOT NULL DEFAULT '' COMMENT 'method for calculating the effective vertical resolution from the number of bins which are used in the calculation of the derivative.';
--
--UPDATE `_ext_methods` set `method_for_getting_used_binres` = 'used_bin_resolution_of_linear_fit';
--UPDATE `_ext_methods` set `method_for_getting_effective_binres` = 'effective_bin_resolution_of_linear_fit';
--
--/*
--* ===================================================================================
--* create a table with different options for smoothing and fillt it
--* ===================================================================================
--*/
--
--CREATE TABLE `_smooth_types` (
--	`ID` INT(11) NOT NULL,
--	`smooth_type` VARCHAR(50) NOT NULL,
--	UNIQUE INDEX `ID` (`ID`) COMMENT 'general handling of smoothing and temporal averaging in ELDA. all products could be derived with individually optimized smoothing (auto) or on a common grid (fixed)'
--);
--
--INSERT INTO `_smooth_types` (`ID`, `smooth_type`) VALUES
--	(0, 'auto'),
--	(1, 'fixed');
--
--/*
--* ===================================================================================
--* create a table with different algorithms for smoothing of individual profiles
--* ===================================================================================
--*/
--
--CREATE TABLE `_smooth_methods` (
--  `ID` int(11) NOT NULL,
--  `method` varchar(100) NOT NULL DEFAULT '',
--  `method_for_getting_used_binres` varchar(100) NOT NULL COMMENT 'method for calculating how many bins needs to be used for vertical smoothing in order to achieve a given effective vertical resolution.',
--  `method_for_getting_effective_binres` varchar(100) NOT NULL COMMENT 'method for calculating the effective vertical resolution from the number of bins which are used for vertical smoothing',
--  PRIMARY KEY (`ID`) COMMENT 'different algorithms to smooth individual profiles'
--);
--
--INSERT INTO `_smooth_methods` (`ID`, `method`, `method_for_getting_used_binres`, `method_for_getting_effective_binres`) VALUES
--    (0, 'Savitzky-Golay', 'used_bin_resolution_of_savitzky_golay_smoothing', 'used_bin_resolution_of_savitzky_golay_smoothing'),
--    (1, 'sliding average', 'used_bin_resolution_of_sliding_average', 'used_bin_resolution_of_sliding_average');
--
--/*
--* ===================================================================================
--* !!! CAUTION !!!
--* create a table with smooth options of individual products
--* copy ALL smooth related entries from product_options into this new table
--* ===================================================================================
--*/
--
--CREATE TABLE `smooth_options` (
--	`id` INT(11) NOT NULL AUTO_INCREMENT,
--	`_product_ID` INT(11) NOT NULL DEFAULT '-1',
--	`_lowrange_error_threshold_ID` INT(11) NOT NULL DEFAULT '1',
--	`_highrange_error_threshold_ID` INT(11) NOT NULL DEFAULT '1',
--	`detection_limit` DECIMAL(11,11) NOT NULL DEFAULT '0',
--	`transition_zone_from` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
--	`transition_zone_to` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
--    `lowres_lowrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
--    `lowres_highrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
--    `highres_lowrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
--    `highres_highrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
--    `lowres_lowrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
--    `lowres_highrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
--    `highres_lowrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL,
--    `highres_highrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL,
--    `_smooth_type` INT(11) NOT NULL DEFAULT '0',
--	PRIMARY KEY (`id`),
--	INDEX `FK_smooth_options_smooth_types` (`_smooth_type`),
--	INDEX `FK_smooth_options_products` (`_product_ID`),
--	CONSTRAINT `FK_smooth_options_products` FOREIGN KEY (`_product_ID`) REFERENCES `products` (`ID`),
--	CONSTRAINT `FK_smooth_options_smooth_types` FOREIGN KEY (`_smooth_type`) REFERENCES `_smooth_types` (`ID`)
--);
--
--insert
--into smooth_options
--    (_product_ID,
--    _lowrange_error_threshold_ID,
--    _highrange_error_threshold_ID,
--    detection_limit)
--select
--    _product_ID,
--    _lowrange_error_threshold_ID,
--    _highrange_error_threshold_ID,
--    detection_limit
--from product_options;
--
--INSERT INTO `smooth_options` (`_product_ID`, `_lowrange_error_threshold_ID`, `_highrange_error_threshold_ID`, `detection_limit`, `transition_zone_from`, `transition_zone_to`, `lowres_lowrange_integration_time`, `lowres_highrange_integration_time`, `highres_lowrange_integration_time`, `highres_highrange_integration_time`, `lowres_lowrange_vertical_resolution`, `lowres_highrange_vertical_resolution`, `highres_lowrange_vertical_resolution`, `highres_highrange_vertical_resolution`, `_smooth_type`) VALUES
--	(@mwlid, 1, 1, 0, 2000.0000, 3000.0000, 3600, 7200, 1800, 1800, 300.0000, 900.0000, 150.0000, 300.0000, 1);
--
--/*
--* ===================================================================================
--* !!! CAUTION !!!
--* remove smoothing related columns from product_options (because they are now in the new table smooth_options)
--* the remaining columns describe parameter of preprocessing -> rename the table to preproc_options
--* ===================================================================================
--*/
--
--alter table product_options
--drop column _lowrange_error_threshold_ID,
--drop column _highrange_error_threshold_ID,
--drop column detection_limit;
--
--RENAME TABLE product_options TO preproc_options;
--
--INSERT INTO `preproc_options` (`_product_ID`, `min_height`, `max_height`, `preprocessing_integration_time`, `preprocessing_vertical_resolution`, `interpolation_id`) VALUES
--	(@mwlid, 0.0, 0.0, 3600, 7.5, 1);
--
--/*
--* ===================================================================================
--* !!! CAUTION !!!
--* create a view which combines tables smooth_options and preproc_options
--* the new view product_options emulates the former table product_options
--* ===================================================================================
--*/
--
--create view product_options
--as select
--po.ID,
--po._product_ID,
--po.min_height,
--po.max_height,
--po.preprocessing_integration_time,
--po.preprocessing_vertical_resolution,
--po.interpolation_id,
--so._lowrange_error_threshold_ID,
--so._highrange_error_threshold_ID,
--so.detection_limit
--from preproc_options as po,
--smooth_options as so
--where so._product_ID = po._product_ID;
--
--/*
--* ===================================================================================
--* add a column with minimum backscatter ratio to table ext_bsc_options
--* which can be used for quality control of final products
--* ===================================================================================
--*/
--
--ALTER TABLE `ext_bsc_options`
--ADD COLUMN `min_BscRatio_for_LR` DECIMAL(10,4) NOT NULL DEFAULT '1.0000';
--
--UPDATE `ext_bsc_options` set `min_BscRatio_for_LR` = '1.1' where _product_ID=379;
--
--/*
--* ===================================================================================
--* add a column to tables elast_backscatter_options and raman_backscatter_options
--* which contains a link to the smoothing algorithm to be used with this bsc method
--* ===================================================================================
--*/
--
--ALTER TABLE `elast_backscatter_options`
--	ADD COLUMN `_smooth_method_ID` INT(11) NOT NULL DEFAULT '0'
--	COMMENT 'link to _smooth_methods.ID' AFTER `_iter_bsc_options_id`,
--	ADD INDEX `_smooth_method_ID` (`_smooth_method_ID`);
--
--ALTER TABLE `raman_backscatter_options`
--	ADD COLUMN `_smooth_method_ID` INT(11) NOT NULL DEFAULT '0'
--	COMMENT 'link to _smooth_methods.ID' AFTER `_error_method_ID`,
--	ADD INDEX `_smooth_method_ID` (`_smooth_method_ID`);
--
--/*
--* ===================================================================================
--* create a new table which contains backscatter evaluation methods (Klett or Raman)
--* this table is used to fill netcdf attributes ‚flag_values‘ and ‚flag_meanings‘ of the
--* variable backscatter_evaluation_method. analog to how the attributes of
--* variables like ‚extinction_evaluation_algorithm‘ etc. are automatically filled by ELDAmwl
--* ===================================================================================
--*/
--
--CREATE TABLE `_bsc_methods` (
--  `id` int(11) NOT NULL DEFAULT '0',
--  `method` varchar(100) NOT NULL DEFAULT '',
--  PRIMARY KEY (`id`)
--);
--
--INSERT INTO `_bsc_methods` (`id`, `method`) VALUES
--	(0, 'Raman'),
--	(1, 'elastic_backscatter');
--
--/*
--* ===================================================================================
--* NEW
--* create a new table with ELDAmwl exit codes and fill it
--* ===================================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `eldamwl_exitcodes` (
--  `exit_code` int(11) NOT NULL,
--  `description`varchar(200) NOT NULL DEFAULT ''
--)
--
--INSERT INTO `eldamwl_exitcodes` (`exit_code`, `description`) VALUES
--	(0, 'Finished without errors'),
--	(1, 'Configuration file not found'),
--	(2, 'Lidar ratio file not found'),
--	(3, 'Intermediate signal file not found'),
--	(4, 'File with Savitzky-Golay coefficients not found'),
--	(5, 'Invalid measurement ID\r\n'),
--	(6, 'Directory for log file not found'),
--	(7, 'Use case not yet implemented'),
--	(8, 'Product not yet implemented\r\n '),
--	(9, 'Cannot connect to db'),
--	(10, 'Cannot read ncfile'),
--	(11, 'Calibration range higher than valid data range'),
--	(12, 'Cannot find variable Lidar_Ratio in lr file'),
--	(13, 'No valid data points for calibration'),
--	(14, 'Cannot create merged signal'),
--	(15, 'Cannot average products: profiles have different height axis or vertical resolutions'),
--	(16, 'Noise of far-range profile too large for merging'),
--	(17, 'Some of the needed options for product calculation were not found in the db. Please check in the products page (e.g. product options, monte carlo options, ...).'),
--	(18, 'Cannot average signals with different scan angles'),
--	(19, 'Cannot create near range or far range extinction profile'),
--	(20, 'Iterative bsc calculation does not converge'),
--	(21, 'Not enough pre-calculated Savitzky-Golay coefficients'),
--	(22, 'Unknown runtime exception'),
--	(255, 'Timeout'),
--	(23, 'Number of MonteCarlo iterations must be larger than 1'),
--	(24, 'Klett bsc retrieval requires Error method = Monte-Carlo; no MC options are provided for the retrieval of Klett bsc'),
--	(25, 'no mathematically stable solution of Klett retrieval'),
--	(254, 'General error (most probably segmentation fault)'),
--	(26, 'no channel_id in nc file -> rerun ELPP'),
--	(27, 'negative calibration value, signal might be negative'),
--	(28, 'This version of ELDA requires pre-processed files generated with ELPP version 7.00 or larger'),
--	(29, 'more than 1 depolarization per product not yet implemented'),
--	(30, 'cannot find correct channel idx in pre-processed file'),
--	(31, 'detection limit of products must be larger than 0.'),
--	(32, 'Wrong SCC version. "re-run ELDA" is not possible because pre-processed files have been generated with a previous SCC version. You need to apply "reprocess all"'),
--	(33, 'no dimension "depolarization" in pre-processed file'),
--	(34, 'cannot find positive values in profile'),
--	(41, 'wrong command line parameter'),
--	(42, 'different cloud masks exist for measurement'),
--	(43, 'different header information in ELPP files of measurement'),
--	(44, 'calibration params of backscatter products of the measurement are not equal'),
--	(45, 'No MonteCarlo Options for product'),
--	(46, 'No backscatter calibration options for product'),
--	(47, 'could not find overlap file in database'),
--	(48, 'could not find calibration window for backscatter retrieval'),
--	(100, 'internal error: cannot fnd requested information in data storage'),
--	(101, 'internal error: more than 1 override to class registry');
--
--
--/*
--* ===================================================================================
--* NEW
--* create a new table with ELDAmwl products
--* ===================================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `eldamwl_products` (
--  `ID` bigint(20) NOT NULL AUTO_INCREMENT,
--  `measurements_id` varchar(15) NOT NULL DEFAULT '',
--  `product_id` int(11) NOT NULL DEFAULT '0',
--  `InscribedAt` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
--  `scc_version_id` int(11) DEFAULT NULL,
--  `filename` varchar(100) NOT NULL DEFAULT '',
--  PRIMARY KEY (`ID`)
--) ;
--
--/*
--* ===================================================================================
--* NEW
--* create a new table with ELDAmwl log output
--* ===================================================================================
--*/
--
--CREATE TABLE IF NOT EXISTS `eldamwl_logs` (
--  `ID` bigint(12) NOT NULL AUTO_INCREMENT,
--  `measurements_id` varchar(15) DEFAULT '',
--  `product_id` int(11) DEFAULT '-1',
--  `level` int(1) NOT NULL COMMENT 'According to syslog-defined levels. 3=Error, 4=Warning, 6=Informational, 7=Debug',
--  `module_version` varchar(15) ,
--  `datetime` datetime NOT NULL DEFAULT '1970-01-01 00:00:00',
--  `message` varchar(400) NOT NULL DEFAULT '',
--  PRIMARY KEY (`ID`)
--) ;
--
--
--
/*
* ===================================================================================
* repair duplicate entries in table `eldamwl_class_names`
* ===================================================================================
*/

UPDATE `eldamwl_class_names` SET `method` = 'eff_bin_resolution_of_savitzky_golay_smoothing' WHERE `classname` = 'SavGolayEffBinRes';
UPDATE `eldamwl_class_names` SET `method` = 'eff_bin_resolution_of_sliding_average' WHERE `classname` = 'SlidAvrgEffBinRes';

/*
* ===================================================================================
* repair duplicate entries in table `_smooth_methods`
* ===================================================================================
*/
UPDATE `_smooth_methods` set `method_for_getting_effective_binres` = 'eff_bin_resolution_of_savitzky_golay_smoothing' WHERE ID = 0;
UPDATE `_smooth_methods` set `method_for_getting_effective_binres` = 'eff_bin_resolution_of_sliding_average' WHERE ID = 1;

/*
* ===================================================================================
* change system of test measurement
* ===================================================================================
*/
UPDATE `measurements` SET `_hoi_system_ID` = 193 where `ID` = '20181017oh00';

/*
* ===================================================================================
* create a table for VLDR options (vldr_options)
* fill vldr_options with data of this example (for system 192)
* 1) add new entry to table polarization_options
* 2) add new entry to table vldr_options
* 3) add preproc options for new product
* 4) add smooth options for new product
* ===================================================================================
*/

CREATE TABLE IF NOT EXISTS `vldr_options` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `_product_ID` int(11) NOT NULL DEFAULT '-1',
  `_error_method_ID` int(11) NOT NULL DEFAULT '-1',
  PRIMARY KEY (`ID`)
);

INSERT INTO `vldr_options` (`_product_ID`, `_error_method_ID`) VALUES
	(637, 0);

INSERT INTO `polarization_options` (
    `_product_ID`,
    `_pol_calibration_method_ID`,
    `_crosstalk_parameter_method_ID`,
    `_correction_factor_method_ID`) VALUES
	(637, 2, 2, 3);

INSERT INTO `preproc_options` (`_product_ID`, `min_height`, `max_height`, `preprocessing_integration_time`, `preprocessing_vertical_resolution`, `interpolation_id`) VALUES
	(637, 100, 15000, 3600, 15, 1);

INSERT INTO `smooth_options` (`_product_ID`,
                              `_lowrange_error_threshold_ID`,
                              `_highrange_error_threshold_ID`,
                              `detection_limit`,
                               `_smooth_type`) VALUES
	(637, 5, 7, 0.001, 0);

/*
* ===================================================================================
* create a table for PLDR options (pldr_options)
* fill pldr_options with data of this example (for system 182)
* 1) add 2 new pldr products to table products
* 2) add 2 new entries to table pldr_options (1 for Raman bsc, 1 for elast bsc)
* ===================================================================================
*/

CREATE TABLE IF NOT EXISTS `pldr_options` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `_product_ID` int(11) NOT NULL DEFAULT '-1',
  `_vldr_product_ID` int(11) NOT NULL DEFAULT '-1',
  `_bsc_product_ID` int(11) NOT NULL DEFAULT '-1',
  `_error_method_ID` int(11) NOT NULL DEFAULT '-1',
  `min_BscRatio_for_PLDR` decimal(10,4) NOT NULL DEFAULT '1.0000',
  PRIMARY KEY (`ID`)
);

INSERT INTO `pldr_options` (
    `_product_ID`,
    `_vldr_product_ID`,
    `_bsc_product_ID`,
    `_error_method_ID`,
    `min_BscRatio_for_PLDR`) VALUES
	(638, 637, 324, 0, 1.01),
	(639, 637, 332, 0, 1.01);

/*
* ===================================================================================
* insert single products into mwlproduct_product (interface does not work yet)
* ===================================================================================
*/

INSERT INTO `mwlproduct_product` (`ID`, `_mwl_product_ID`, `_Product_ID`, `create_with_hr`, `create_with_lr`) VALUES
	(NULL, 627, 378, 1, 1),
	(NULL, 627, 377, 0, 1),
	(NULL, 627, 324, 1, 1),
	(NULL, 627, 380, 0, 1),
	(NULL, 627, 381, 0, 1),
	(NULL, 627, 330, 1, 1);

/*
* ===================================================================================
* insert prepared signal files into prepared_signal_files (interface / ELPP do not work yet)
* ===================================================================================
*/
UPDATE prepared_signal_files SET `_Product_ID` = 380 where (`_Product_ID` = 381) and (`__measurements__ID` = '20181017oh00');

/*
* ===================================================================================
* add new error codes
* ===================================================================================
*/
INSERT INTO `eldamwl_exitcodes` (`exit_code`, `description`) VALUES
	(49, 'backscatter and extinction products for a lidar ratio retrieval have different wavelengths'),
	(50, 'integration during retrieval of product failed'),
	(51, 'the MC error retrieval could not obtain enough samples'),
	(52, 'no individual products were generated for mwl product'),
	(53, 'cannot calculate lidar constant from negative backscatter value -> check backscatter calibration settings and telescope overlap settings'),
	(54, 'the temporal and/or vertical resolutions are '
               'not consistent for all the products attributed to one mwl product'),
	(55, 'No temporal and/or vertical resolutions are available for mwl_product');
