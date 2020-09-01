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

#UPDATE `_ext_methods` set `python_classname` = 'WeightedLinearFit' where ID=0;
#UPDATE `_ext_methods` set `python_classname` = 'NonWeightedLinearFit' where ID=1;

#-------------------------

#ALTER TABLE `_ram_bsc_methods` 
#ADD COLUMN `python_classname` varchar(100) NOT NULL DEFAULT '' COMMENT 'the name of the python class in ELDAmwl which performs the calculation';

#UPDATE `_ram_bsc_methods` set `python_classname` = 'CalcRamanBscProfileAsAnsmann' where ID=0;
#UPDATE `_ram_bsc_methods` set `python_classname` = 'CalcRamanBscProfileViaBR' where ID=1;

#-------------------------

