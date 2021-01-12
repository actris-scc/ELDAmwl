#ALTER TABLE `_product_types` 
#ADD COLUMN better_name VARCHAR(100) NOT NULL DEFAULT '',
#ADD COLUMN is_mwl_only_product INT(1) NOT NULL DEFAULT '0', 
#ADD COLUMN is_in_mwl_products INT(1) NOT NULL DEFAULT '0',
#ADD COLUMN is_basic_product INT(1) NOT NULL DEFAULT '0';

#UPDATE `_product_types`
#set better_name = 'particle extinction coefficient (Raman)', is_in_mwl_products = 1, is_basic_product=1 where ID=1;
#UPDATE `_product_types`
#set better_name = 'particle lidar ratio (Raman)', is_in_mwl_products = 1 where ID=2;
#UPDATE `_product_types`
#set better_name = 'particle backscatter coefficient (Raman)', is_in_mwl_products = 1, is_basic_product=1 where ID=0;
#UPDATE `_product_types`
#set better_name = 'particle backscatter coefficient (elast.)', is_in_mwl_products = 1, is_basic_product=1 where ID=3;
#UPDATE `_product_types`
#set better_name = 'particle backscatter coefficient (elast.)', is_in_mwl_products = 1, is_basic_product=1 where ID=3;

#INSERT INTO `_product_types` (`ID`, `product_type`, `better_name`, `nc_file_id`, `processor_ID`, `is_mwl_only_product`, `is_in_mwl_products`, `is_basic_product`) VALUES
#(12, 'multi-wavelength product', 'multi-wavelength product', '', 1, 0, 0, 0),
#(13, 'Angstroem exponent', 'Angstroem exponent', '', 1, 1, 1, 0),
#(14, 'color ratio', 'color ratio', '', 1, 1, 1, 0),
#(15, 'vol depol ratio', 'volume linear depolarization ratio', '', 1, 1, 1, 1),
#(16, 'part depol ratio', 'particle linear depolarization ratio', '', 1, 1, 1, 0);

#-------------------------

#CREATE TABLE IF NOT EXISTS `mwlproduct_product` (
#  `ID` int(11) NOT NULL AUTO_INCREMENT,
#  `_mwl_product_ID` int(11) NOT NULL DEFAULT '0',
#  `_Product_ID` int(11) NOT NULL DEFAULT '0',
#  `create_with_hr` int(1) NOT NULL DEFAULT '0',
#  `create_with_lr` int(1) NOT NULL DEFAULT '1',
#  PRIMARY KEY (`ID`)
#);

#INSERT INTO `mwlproduct_product` (`ID`, `_mwl_product_ID`, `_Product_ID`, `create_with_hr`, `create_with_lr`) VALUES
#	(1, 598, 378, 1, 0),
#	(2, 598, 379, 0, 1),
#	(3, 598, 324, 1, 1),
#	(4, 598, 330, 1, 1);

#-------------------------

#CREATE TABLE IF NOT EXISTS `angstroem_exp_options` (
#  `ID` int(11) NOT NULL AUTO_INCREMENT,
#  `_product_ID` int(11) NOT NULL DEFAULT '-1',
#  `_product_1_ID` int(11) NOT NULL DEFAULT '-1',
#  `_product_2_ID` int(11) NOT NULL DEFAULT '-1',
#  `_error_method_ID` int(11) NOT NULL DEFAULT '-1',
#  `min_BscRatio_for_AE` decimal(10,4) NOT NULL DEFAULT '1.0000',
#  PRIMARY KEY (`ID`)
#);

#INSERT INTO `angstroem_exp_options` (`ID`, `_product_ID`, `_product_1_ID`, `_product_2_ID`, `_error_method_ID`, `min_BscRatio_for_AE`) VALUES
#	(1, 1, 378, 324, 1, 1.0000),
#	(2, 2, 377, 380, 1, 1.0000);

#-------------------------

#CREATE TABLE IF NOT EXISTS `color_ratio_options` (
#  `ID` int(11) NOT NULL AUTO_INCREMENT,
#  `_product_ID` int(11) NOT NULL DEFAULT '-1',
#  `_nominator_product_ID` int(11) NOT NULL DEFAULT '-1',
#  `_denominator_product_ID` int(11) NOT NULL DEFAULT '-1',
#  `_error_method_ID` int(11) NOT NULL DEFAULT '-1',
#  `min_BscRatio_for_CR` decimal(10,4) NOT NULL DEFAULT '1.0000',
#  PRIMARY KEY (`ID`)
#);

#INSERT INTO `color_ratio_options` (`ID`, `_product_ID`, `_nominator_product_ID`, `_denominator_product_ID`, `_error_method_ID`, `min_BscRatio_for_CR`) VALUES
#	(1, 1, 379, 381, 1, 1.0000);

#-------------------------

#ALTER TABLE `measurements` 
#ADD COLUMN `num_id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT first;
#ALTER TABLE `measurements` DROP PRIMARY KEY, ADD PRIMARY KEY (num_id)

#-------------------------

ALTER TABLE `_cal_range_search_methods`
ADD COLUMN `python_classname` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';

#-------------------------

#ALTER TABLE `_elast_bsc_methods`
#ADD COLUMN `python_classname` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';

#UPDATE `_elast_bsc_methods` set `python_classname` = 'CalcBscProfileKF' where ID=0;
#UPDATE `_elast_bsc_methods` set `python_classname` = 'CalcBscProfileIter' where ID=1;

#-------------------------

#ALTER TABLE `_ext_methods` 
#ADD COLUMN `python_classname` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';
#ADD COLUMN `python_classname_get_used_binres` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';
#ADD COLUMN `python_classname_get_effective_binres` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';

#UPDATE `_ext_methods` set `python_classname` = 'WeightedLinearFit' where ID=0;
#UPDATE `_ext_methods` set `python_classname_get_used_binres` = 'LinFitUsedBinRes';
#UPDATE `_ext_methods` set `python_classname_get_effective_binres` = 'LinFitEffBinRes';

#-------------------------

#ALTER TABLE `_ram_bsc_methods` 
#ADD COLUMN `python_classname` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';

#UPDATE `_ram_bsc_methods` set `python_classname` = 'CalcRamanBscProfileAsAnsmann' where ID=0;
#UPDATE `_ram_bsc_methods` set `python_classname` = 'CalcRamanBscProfileViaBR' where ID=1;

#-------------------------

ALTER TABLE `eldaexitcodes`
INSERT INTO `eldaexitcodes` (`exit_code`, `description`) VALUES
	(39, 'wrong command line parameter'),
	(40, 'different cloud masks exist for measurement'),
	(41, 'different header information in ELPP files of measurement'),
	(42, 'calibration params of backscatter products of the measurement are not equal'),
	(43, 'No MonteCarlo Options for product'),
	(44, 'No backscatter calibration options for product'),
	(100, 'internal error: cannot fnd requested information in data storage'),
	(101, 'internal error: more than 1 override to class registry');

#-------------------------

CREATE TABLE `_smooth_types` (
	`ID` INT(11) NOT NULL,
	`smooth_type` VARCHAR(50) NOT NULL,
	UNIQUE INDEX `ID` (`ID`)
);

INSERT INTO `_smooth_types` (`ID`, `smooth_type`) VALUES
	(0, 'auto'),
	(1, 'fixed');

#-------------------------

CREATE TABLE `smooth_options` (
	`id` INT(11) NOT NULL AUTO_INCREMENT,
	`_product_ID` INT(11) NOT NULL DEFAULT '-1',
	`_lowrange_error_threshold_ID` INT(11) NOT NULL DEFAULT '1',
	`_highrange_error_threshold_ID` INT(11) NOT NULL DEFAULT '1',
	`detection_limit` DECIMAL(11,11) NOT NULL DEFAULT '0.00000000000',
	`transition_zone_from` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
	`transition_zone_to` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
    `lowres_lowrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
    `lowres_highrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
    `highres_lowrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
    `highres_highrange_integration_time` INT(11) NULL DEFAULT NULL COMMENT 'in s',
    `lowres_lowrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
    `lowres_highrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL COMMENT 'in m',
    `highres_lowrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL,
    `highres_highrange_vertical_resolution` DECIMAL(10,4) NULL DEFAULT NULL,
    `_smooth_type` INT(11) NOT NULL DEFAULT '0';
	PRIMARY KEY (`id`)
);

insert
into smooth_options
    (_product_ID,
    _lowrange_error_threshold_ID,
    _highrange_error_threshold_ID,
    detection_limit)
select
    _product_ID,
    _lowrange_error_threshold_ID,
    _highrange_error_threshold_ID,
    detection_limit
from product_options;

#-------------------------

alter table product_options
drop column _lowrange_error_threshold_ID,
drop column _highrange_error_threshold_ID,
drop column detection_limit;

#-------------------------

create view product_options_v
as select
po.ID,
po._product_ID,
po.min_height,
po.max_height,
po.preprocessing_integration_time,
po.preprocessing_vertical_resolution,
po.interpolation_id,
so._lowrange_error_threshold_ID,
so._highrange_error_threshold_ID,
so.detection_limit
from product_options as po,
smooth_options as so
where so._product_ID = po._product_ID;
