Search.setIndex({docnames:["algorithms/algorithms","algorithms/prepare_signals","api/ELDAmwl","api/ELDAmwl.configs","api/ELDAmwl.database","api/ELDAmwl.database.tables","api/ELDAmwl.tests","api/ELDAmwl.tests.database","api/modules","contributing/contributing","contributing/global_instances","contributing/modularity/add_new_baseoperation","contributing/modularity/baseoperation_basic","contributing/modularity/baseoperation_complex","contributing/modularity/baseoperation_fundamental","contributing/modularity/example_PrepareExtSignals","contributing/modularity/example_SignalSlope","contributing/modularity/examples","contributing/modularity/list_of_subsystems","contributing/modularity/modularity","contributing/modularity/overwrite_baseoperation","contributing/modularity/registry","contributing/testing","genindex","index","installing/configuring","installing/installing","installing/requirements","installing/setup","modindex"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":2,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,sphinx:56},filenames:["algorithms\\algorithms.rst","algorithms\\prepare_signals.rst","api\\ELDAmwl.rst","api\\ELDAmwl.configs.rst","api\\ELDAmwl.database.rst","api\\ELDAmwl.database.tables.rst","api\\ELDAmwl.tests.rst","api\\ELDAmwl.tests.database.rst","api\\modules.rst","contributing\\contributing.rst","contributing\\global_instances.rst","contributing\\modularity\\add_new_baseoperation.rst","contributing\\modularity\\baseoperation_basic.rst","contributing\\modularity\\baseoperation_complex.rst","contributing\\modularity\\baseoperation_fundamental.rst","contributing\\modularity\\example_PrepareExtSignals.rst","contributing\\modularity\\example_SignalSlope.rst","contributing\\modularity\\examples.rst","contributing\\modularity\\list_of_subsystems.rst","contributing\\modularity\\modularity.rst","contributing\\modularity\\overwrite_baseoperation.rst","contributing\\modularity\\registry.rst","contributing\\testing.rst","genindex.rst","index.rst","installing\\configuring.rst","installing\\installing.rst","installing\\requirements.rst","installing\\setup.rst","modindex.rst"],objects:{"":{ELDAmwl:[2,0,0,"-"]},"ELDAmwl.backscatter_factories":{BackscatterFactory:[2,1,1,""],BackscatterFactoryDefault:[2,1,1,""],BackscatterParams:[2,1,1,""],Backscatters:[2,1,1,""],BscCalibrationParams:[2,1,1,""]},"ELDAmwl.backscatter_factories.BackscatterFactory":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.backscatter_factories.BackscatterFactoryDefault":{data_storage:[2,3,1,""],elast_sig:[2,3,1,""],get_product:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.backscatter_factories.BackscatterParams":{add_signal_role:[2,2,1,""],from_db:[2,2,1,""]},"ELDAmwl.backscatter_factories.Backscatters":{from_signal:[2,2,1,""]},"ELDAmwl.backscatter_factories.BscCalibrationParams":{from_db:[2,2,1,""]},"ELDAmwl.base":{DataPoint:[2,1,1,""],Params:[2,1,1,""]},"ELDAmwl.base.DataPoint":{from_nc_file:[2,2,1,""]},"ELDAmwl.base.Params":{sub_params:[2,3,1,""]},"ELDAmwl.columns":{Columns:[2,1,1,""]},"ELDAmwl.columns.Columns":{altitude:[2,2,1,""],angle_to_time_dependent_var:[2,2,1,""],data:[2,2,1,""],err:[2,2,1,""],height:[2,2,1,""],qf:[2,2,1,""],rel_err:[2,2,1,""],set_invalid_point:[2,2,1,""]},"ELDAmwl.configs":{config:[3,0,0,"-"],config_default:[3,0,0,"-"],config_example:[3,0,0,"-"],config_example_linux:[3,0,0,"-"]},"ELDAmwl.data_storage":{DataStorage:[2,1,1,""]},"ELDAmwl.data_storage.DataStorage":{cloud_mask:[2,2,1,""],elpp_signal:[2,2,1,""],elpp_signals:[2,2,1,""],header:[2,2,1,""],prepared_signal:[2,2,1,""],prepared_signals:[2,2,1,""],set_basic_product_auto_smooth:[2,2,1,""],set_elpp_signal:[2,2,1,""],set_prepared_signal:[2,2,1,""]},"ELDAmwl.database":{db:[4,0,0,"-"],db_functions:[4,0,0,"-"],tables:[5,0,0,"-"]},"ELDAmwl.database.db":{DBUtils:[4,1,1,""]},"ELDAmwl.database.db.DBUtils":{get_connect_string:[4,2,1,""],init_engine:[4,2,1,""],read_tasks:[4,2,1,""]},"ELDAmwl.database.db_functions":{get_bsc_cal_params_query:[4,4,1,""],get_general_params_query:[4,4,1,""],get_products_query:[4,4,1,""],read_extinction_algorithm:[4,4,1,""],read_extinction_params:[4,4,1,""],read_lidar_ratio_params:[4,4,1,""],read_mwl_product_id:[4,4,1,""],read_signal_filenames:[4,4,1,""],read_system_id:[4,4,1,""]},"ELDAmwl.database.tables":{backscatter:[5,0,0,"-"],db_base:[5,0,0,"-"],extinction:[5,0,0,"-"],lidar_ratio:[5,0,0,"-"],measurements:[5,0,0,"-"],system_product:[5,0,0,"-"]},"ELDAmwl.database.tables.backscatter":{BscCalibrOption:[5,1,1,""],ElastBackscatterOption:[5,1,1,""],RamanBackscatterOption:[5,1,1,""]},"ELDAmwl.database.tables.backscatter.BscCalibrOption":{ID:[5,3,1,""],LowestHeight:[5,3,1,""],TopHeight:[5,3,1,""],WindowWidth:[5,3,1,""],calValue:[5,3,1,""]},"ELDAmwl.database.tables.backscatter.ElastBackscatterOption":{ID:[5,3,1,""],fixed_lr:[5,3,1,""],fixed_lr_error:[5,3,1,""]},"ELDAmwl.database.tables.backscatter.RamanBackscatterOption":{ID:[5,3,1,""]},"ELDAmwl.database.tables.db_base":{ElastBscMethod:[5,1,1,""],ErrorMethod:[5,1,1,""]},"ELDAmwl.database.tables.db_base.ElastBscMethod":{ID:[5,3,1,""],method:[5,3,1,""]},"ELDAmwl.database.tables.db_base.ErrorMethod":{id:[5,3,1,""],method:[5,3,1,""]},"ELDAmwl.database.tables.extinction":{ExtMethod:[5,1,1,""],ExtinctionOption:[5,1,1,""],OverlapFile:[5,1,1,""]},"ELDAmwl.database.tables.extinction.ExtMethod":{ID:[5,3,1,""],method:[5,3,1,""],python_classname:[5,3,1,""]},"ELDAmwl.database.tables.extinction.ExtinctionOption":{ID:[5,3,1,""],angstroem:[5,3,1,""]},"ELDAmwl.database.tables.extinction.OverlapFile":{ID:[5,3,1,""],filename:[5,3,1,""],start:[5,3,1,""],status:[5,3,1,""],stop:[5,3,1,""],submission_date:[5,3,1,""]},"ELDAmwl.database.tables.lidar_ratio":{ExtBscOption:[5,1,1,""]},"ELDAmwl.database.tables.lidar_ratio.ExtBscOption":{ID:[5,3,1,""],min_BscRatio_for_LR:[5,3,1,""]},"ELDAmwl.database.tables.measurements":{Measurements:[5,1,1,""]},"ELDAmwl.database.tables.measurements.Measurements":{ID:[5,3,1,""],calipso:[5,3,1,""],cirrus:[5,3,1,""],climatol:[5,3,1,""],cloudmask:[5,3,1,""],cloudmask_current_product_id:[5,3,1,""],cloudmask_return_code:[5,3,1,""],comment:[5,3,1,""],creation_auth_user_ID:[5,3,1,""],creation_date:[5,3,1,""],dicycles:[5,3,1,""],elda:[5,3,1,""],elda_current_product_id:[5,3,1,""],elda_return_code:[5,3,1,""],eldec:[5,3,1,""],eldec_current_product_id:[5,3,1,""],eldec_return_code:[5,3,1,""],elic:[5,3,1,""],elic_current_product_id:[5,3,1,""],elic_return_code:[5,3,1,""],elpp:[5,3,1,""],elpp_current_product_id:[5,3,1,""],elpp_return_code:[5,3,1,""],elquick:[5,3,1,""],elquick_current_product_id:[5,3,1,""],elquick_return_code:[5,3,1,""],etna:[5,3,1,""],forfires:[5,3,1,""],hirelpp:[5,3,1,""],hirelpp_current_product_id:[5,3,1,""],hirelpp_return_code:[5,3,1,""],interface_return_code:[5,3,1,""],lidar_ratio_file_id:[5,3,1,""],meas_id:[5,3,1,""],overlap_file_id:[5,3,1,""],photosmog:[5,3,1,""],rurban:[5,3,1,""],sahadust:[5,3,1,""],sounding_file_id:[5,3,1,""],start:[5,3,1,""],stop:[5,3,1,""],stratos:[5,3,1,""],update_auth_user_ID:[5,3,1,""],updated_date:[5,3,1,""],upload:[5,3,1,""]},"ELDAmwl.database.tables.system_product":{ErrorThresholds:[5,1,1,""],MWLproductProduct:[5,1,1,""],PreparedSignalFile:[5,1,1,""],ProductOptions:[5,1,1,""],ProductTypes:[5,1,1,""],Products:[5,1,1,""],SystemProduct:[5,1,1,""]},"ELDAmwl.database.tables.system_product.ErrorThresholds":{ID:[5,3,1,""],name:[5,3,1,""],value:[5,3,1,""]},"ELDAmwl.database.tables.system_product.MWLproductProduct":{ID:[5,3,1,""],create_with_hr:[5,3,1,""],create_with_lr:[5,3,1,""]},"ELDAmwl.database.tables.system_product.PreparedSignalFile":{ID:[5,3,1,""],filename:[5,3,1,""]},"ELDAmwl.database.tables.system_product.ProductOptions":{ID:[5,3,1,""],detection_limit:[5,3,1,""],interpolation_id:[5,3,1,""],max_height:[5,3,1,""],min_height:[5,3,1,""],preprocessing_integration_time:[5,3,1,""],preprocessing_vertical_resolution:[5,3,1,""]},"ELDAmwl.database.tables.system_product.ProductTypes":{ID:[5,3,1,""],better_name:[5,3,1,""],is_basic_product:[5,3,1,""],is_in_mwl_products:[5,3,1,""],is_mwl_only_product:[5,3,1,""],nc_file_id:[5,3,1,""],processor_ID:[5,3,1,""],product_type:[5,3,1,""]},"ELDAmwl.database.tables.system_product.Products":{ID:[5,3,1,""]},"ELDAmwl.database.tables.system_product.SystemProduct":{ID:[5,3,1,""]},"ELDAmwl.elda_mwl_factories":{MeasurementParams:[2,1,1,""],RunELDAmwl:[2,1,1,""]},"ELDAmwl.elda_mwl_factories.MeasurementParams":{all_bsc_products:[2,2,1,""],basic_products:[2,2,1,""],elast_bsc_products:[2,2,1,""],extinction_products:[2,2,1,""],filtered_list:[2,2,1,""],prod_params:[2,2,1,""],raman_bsc_products:[2,2,1,""],read_product_list:[2,2,1,""]},"ELDAmwl.elda_mwl_factories.RunELDAmwl":{data:[2,2,1,""],get_basic_products:[2,2,1,""],prepare_signals:[2,2,1,""],read_elpp_data:[2,2,1,""],read_tasks:[2,2,1,""]},"ELDAmwl.exceptions":{CsvFileNotFound:[2,5,1,""],DifferentCloudMaskExists:[2,5,1,""],DifferentHeaderExists:[2,5,1,""],FillTableFailed:[2,5,1,""],NotFoundInStorage:[2,5,1,""],OnlyOneOverrideAllowed:[2,5,1,""]},"ELDAmwl.extinction_factories":{ExtinctionAutosmooth:[2,1,1,""],ExtinctionAutosmoothDefault:[2,1,1,""],ExtinctionFactory:[2,1,1,""],ExtinctionFactoryDefault:[2,1,1,""],ExtinctionParams:[2,1,1,""],Extinctions:[2,1,1,""],LinFit:[2,1,1,""],NonWeightedLinearFit:[2,1,1,""],SignalSlope:[2,1,1,""],SlopeToExtinction:[2,1,1,""],SlopeToExtinctionDefault:[2,1,1,""],WeightedLinearFit:[2,1,1,""]},"ELDAmwl.extinction_factories.ExtinctionAutosmooth":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.extinction_factories.ExtinctionAutosmoothDefault":{max_smooth:[2,2,1,""],name:[2,3,1,""],run:[2,2,1,""],signal:[2,3,1,""],smooth_params:[2,3,1,""]},"ELDAmwl.extinction_factories.ExtinctionFactory":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.extinction_factories.ExtinctionFactoryDefault":{data_storage:[2,3,1,""],get_product:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.extinction_factories.ExtinctionParams":{add_signal_role:[2,2,1,""],ang_exp_asDataArray:[2,2,1,""],from_db:[2,2,1,""],smooth_params:[2,2,1,""]},"ELDAmwl.extinction_factories.Extinctions":{from_signal:[2,2,1,""]},"ELDAmwl.extinction_factories.LinFit":{data:[2,3,1,""],name:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.extinction_factories.NonWeightedLinearFit":{name:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.extinction_factories.SignalSlope":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""],prod_id:[2,3,1,""]},"ELDAmwl.extinction_factories.SlopeToExtinction":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.extinction_factories.SlopeToExtinctionDefault":{name:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.extinction_factories.WeightedLinearFit":{name:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.factory":{BaseOperation:[2,1,1,""],BaseOperationFactory:[2,1,1,""]},"ELDAmwl.factory.BaseOperation":{params:[2,2,1,""]},"ELDAmwl.factory.BaseOperationFactory":{get_class:[2,2,1,""],get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.get_basic_products":{GetBasicProducts:[2,1,1,""],GetBasicProductsDefault:[2,1,1,""]},"ELDAmwl.get_basic_products.GetBasicProducts":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.get_basic_products.GetBasicProductsDefault":{data_storage:[2,3,1,""],product_params:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.lidar_ratio_factories":{LidarRatioParams:[2,1,1,""]},"ELDAmwl.lidar_ratio_factories.LidarRatioParams":{assign_to_product_list:[2,2,1,""],from_db:[2,2,1,""]},"ELDAmwl.main":{main:[2,4,1,""]},"ELDAmwl.prepare_signals":{PrepareBscSignals:[2,1,1,""],PrepareBscSignalsDefault:[2,1,1,""],PrepareExtSignals:[2,1,1,""],PrepareExtSignalsDefault:[2,1,1,""],PrepareSignals:[2,1,1,""],PrepareSignalsDefault:[2,1,1,""]},"ELDAmwl.prepare_signals.PrepareBscSignals":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.prepare_signals.PrepareBscSignalsDefault":{bsc_param:[2,3,1,""],combine_depol_components:[2,2,1,""],data_storage:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.prepare_signals.PrepareExtSignals":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.prepare_signals.PrepareExtSignalsDefault":{data_storage:[2,3,1,""],ext_param:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.prepare_signals.PrepareSignals":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.prepare_signals.PrepareSignalsDefault":{data_storage:[2,3,1,""],run:[2,2,1,""]},"ELDAmwl.products":{GeneralProductParams:[2,1,1,""],ProductParams:[2,1,1,""],Products:[2,1,1,""]},"ELDAmwl.products.GeneralProductParams":{from_db:[2,2,1,""],from_id:[2,2,1,""],from_query:[2,2,1,""]},"ELDAmwl.products.ProductParams":{add_signal_role:[2,2,1,""],assign_to_product_list:[2,2,1,""],det_limit_asDataArray:[2,2,1,""],error_method:[2,2,1,""],error_threshold_high_asDataArray:[2,2,1,""],error_threshold_low_asDataArray:[2,2,1,""],includes_product_merging:[2,2,1,""],is_bsc_from_depol_components:[2,2,1,""],prod_id_str:[2,2,1,""],smooth_params:[2,2,1,""]},"ELDAmwl.products.Products":{from_signal:[2,2,1,""],save_to_netcdf:[2,2,1,""]},"ELDAmwl.registry":{FactoryRegistry:[2,1,1,""],Registry:[2,1,1,""]},"ELDAmwl.registry.FactoryRegistry":{find_class_by_name:[2,2,1,""],register_class:[2,2,1,""]},"ELDAmwl.registry.Registry":{find_class_by_name:[2,2,1,""],get_factory_registration:[2,2,1,""],register_class:[2,2,1,""],status:[2,2,1,""]},"ELDAmwl.signals":{CombineDepolComponents:[2,1,1,""],CombineDepolComponentsDefault:[2,1,1,""],DepolarizationCalibration:[2,1,1,""],ElppData:[2,1,1,""],Header:[2,1,1,""],Signals:[2,1,1,""]},"ELDAmwl.signals.CombineDepolComponents":{get_classname_from_db:[2,2,1,""],name:[2,3,1,""]},"ELDAmwl.signals.CombineDepolComponentsDefault":{run:[2,2,1,""]},"ELDAmwl.signals.DepolarizationCalibration":{from_nc_file:[2,2,1,""],gain_factor:[2,3,1,""],gain_factor_correction:[2,3,1,""]},"ELDAmwl.signals.ElppData":{read_nc_file:[2,2,1,""]},"ELDAmwl.signals.Header":{altitude:[2,2,1,""],from_nc_file:[2,2,1,""],latitude:[2,2,1,""],longitude:[2,2,1,""],station_altitude:[2,3,1,""],station_latitude:[2,3,1,""],station_longitude:[2,3,1,""]},"ELDAmwl.signals.Signals":{alt_range:[2,3,1,""],channel_id:[2,3,1,""],channel_id_str:[2,2,1,""],channel_idx_in_ncfile:[2,3,1,""],correct_for_mol_transmission:[2,2,1,""],detection_type:[2,3,1,""],detection_wavelength:[2,3,1,""],emission_wavelength:[2,3,1,""],from_depol_components:[2,2,1,""],from_nc_file:[2,2,1,""],is_Raman_sig:[2,2,1,""],is_WV_sig:[2,2,1,""],is_cross_sig:[2,2,1,""],is_elast_sig:[2,2,1,""],is_fr_signal:[2,2,1,""],is_nr_signal:[2,2,1,""],is_parallel_sig:[2,2,1,""],is_refl_sig:[2,2,1,""],is_total_sig:[2,2,1,""],is_transm_sig:[2,2,1,""],normalize_by_shots:[2,2,1,""],pol_calibr:[2,3,1,""],pol_channel_conf:[2,3,1,""],prepare_for_extinction:[2,2,1,""],range:[2,2,1,""],register:[2,2,1,""],scale_factor_shots:[2,3,1,""],scatterer:[2,3,1,""]},"ELDAmwl.tests":{database:[7,0,0,"-"],disable_test_elda_mwl_factories:[6,0,0,"-"],test_factory:[6,0,0,"-"],test_params:[6,0,0,"-"],test_registry:[6,0,0,"-"],test_signals:[6,0,0,"-"]},"ELDAmwl.tests.database":{create_test_db:[7,0,0,"-"]},"ELDAmwl.tests.database.create_test_db":{DBConstructor:[7,1,1,""]},"ELDAmwl.tests.database.create_test_db.DBConstructor":{create_tables:[7,2,1,""],csv_data:[7,2,1,""],fill_table:[7,2,1,""],fill_tables:[7,2,1,""],refine_data:[7,2,1,""],remove_db:[7,2,1,""]},"ELDAmwl.tests.disable_test_elda_mwl_factories":{test_MeasurementParams:[6,4,1,""]},"ELDAmwl.tests.test_factory":{Factory:[6,1,1,""],OperationA:[6,1,1,""],OperationB:[6,1,1,""],db:[6,4,1,""],test_factory:[6,4,1,""],test_factory_registration:[6,4,1,""]},"ELDAmwl.tests.test_params":{ParamsA:[6,1,1,""],test_params:[6,4,1,""]},"ELDAmwl.tests.test_params.ParamsA":{aplusb:[6,2,1,""],funcaplusb:[6,2,1,""],getb:[6,2,1,""]},"ELDAmwl.tests.test_registry":{Factory:[6,1,1,""],OperationA:[6,1,1,""],OperationB:[6,1,1,""],test_registry_register:[6,4,1,""]},"ELDAmwl.tests.test_registry.Factory":{name:[6,3,1,""]},"ELDAmwl.tests.test_signals":{test_Signals_from_nc_file:[6,4,1,""],test_signals_register:[6,4,1,""]},ELDAmwl:{backscatter_factories:[2,0,0,"-"],base:[2,0,0,"-"],columns:[2,0,0,"-"],configs:[3,0,0,"-"],constants:[2,0,0,"-"],data_storage:[2,0,0,"-"],database:[4,0,0,"-"],elda_mwl_factories:[2,0,0,"-"],error_codes:[2,0,0,"-"],exceptions:[2,0,0,"-"],extinction_factories:[2,0,0,"-"],factory:[2,0,0,"-"],get_basic_products:[2,0,0,"-"],lidar_ratio_factories:[2,0,0,"-"],log:[2,0,0,"-"],main:[2,0,0,"-"],prepare_signals:[2,0,0,"-"],products:[2,0,0,"-"],registry:[2,0,0,"-"],signals:[2,0,0,"-"],tests:[6,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","function","Python function"],"5":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:function","5":"py:exception"},terms:{"20181228oh00_0000379":[22,27],"case":2,"class":[2,4,5,6,7,11,15,16,19,20],"default":[15,17],"final":16,"function":[2,4,6,16],"import":[2,11,16,20,25],"int":[2,4],"new":[2,11,20],"return":[2,4,7,16,19],"super":16,"true":[16,20],"var":2,For:19,IDs:4,Its:[2,24],THe:2,The:[2,3,7,9,11,15,16,19,20,24,25,28],Their:[12,13,14],There:[11,15,19,28],These:5,__call__:16,__init__:[11,16,20],__name__:[11,16,20],_ext_method:[5,11,16],_sig:2,_sig_o:2,accept:[11,20],access:2,accord:28,actual:[4,16],add:[2,11,19,20],add_signal_rol:2,added:11,addict:[2,12,16],adding:[11,19,20],addit:[9,19,24],address:19,aerosol:24,after:28,algorithm:[2,4,9,17,19,24],all:[2,3,7,11,16,19,20,25,28],all_bsc_product:2,allow:[2,5,9,19,24,25],alreadi:[2,11],also:[25,28],alt_rang:2,altern:[2,19,20],altitud:2,alwai:[2,19],among:19,analyz:24,ang_exp_asdataarrai:2,angl:2,angle_to_time_dependent_var:2,angle_var:2,angstroem:5,ani:5,announc:[11,20],anoth:11,any_prod_id_str:16,api:[5,24],aplusb:6,appli:16,arg:16,argument:[2,11,20],arrai:[2,16],assert:16,assess:2,assign_to_product_list:2,associ:7,atmospher:2,attempt:2,attribut:[2,5,6,11,20],auto:[2,22],automat:[2,22],avail:[2,11,16,19,28],axi:2,backscatt:[2,4],backscatter_factori:[8,13],backscatterfactori:2,backscatterfactorydefault:[2,13],backscatterparam:2,bas:2,base:[4,5,6,7,8,19,24],basefactori:2,baseoper:[2,4,6,11,16,19,20,21],baseoperationfactori:[2,6,15,16,19,21],basic:[2,19],basic_product:2,better_nam:5,between:[19,21,24],bin:16,binr:2,blank:2,bring:7,bsc:4,bsc_calibr_opt:5,bsc_param:2,bsc_prod_id:4,bsc_type:4,bsccalibrationparam:2,bsccalibropt:5,cach:2,calcul:[2,4,11,14,16,19],calculu:24,calibr:4,calipso:5,call:[14,16,19],calvalu:5,can:[2,11,16,19,20],central:2,ch_id_str:2,chain:24,chang:28,channel:2,channel_id:2,channel_id_str:2,channel_idx_in_ncfil:2,chart:24,check:[19,28],choic:19,cirru:5,classmethod:2,climatol:5,cloud:2,cloud_mask:2,cloudmask:5,cloudmask_current_product_id:5,cloudmask_return_cod:5,code:[11,19,20,25],coeffici:2,column:[5,8,16],combin:2,combine_depol_compon:2,combinedepolcompon:[2,18],combinedepolcomponentsdefault:[2,12,18],comment:5,complet:[9,20],complex:19,compon:[2,9,24],config:[2,8,25],config_default:[2,8,25],config_exampl:[2,8],config_example_linux:[2,8],configur:[3,24,26],connect_str:4,constant:8,construct:[5,7],constructor:5,contain:[19,28],content:8,contribut:24,convert:2,coordin:2,core:19,correct:2,correct_for_mol_transmiss:2,correl:4,correspond:[2,4,16,19,21,25],could:5,creat:[2,7,11,16,20],create_t:7,create_test_db:[2,6,22],create_with_hr:5,create_with_lr:5,creation_auth_user_id:5,creation_d:5,credenti:[3,25],csv:[2,7],csv_data:7,csvfilenotfound:2,current:7,data:[2,7,9,22,24,27],data_storag:8,data_var:2,dataarrai:2,databas:[2,3,6,8,11,16,22,25,27],datafram:2,datapoint:2,dataset:[2,12],datastorag:2,db_base:[2,4],db_function:[2,8,16],dbconstructor:[7,22],dbutil:4,decid:2,decis:[2,16],declar:5,def:[11,16,20],defin:2,degrees_east:2,degrees_north:2,depend:2,depol:2,depol_param:2,depolar:2,depolarizationcalibr:2,deriv:[2,4,24],descend:19,describ:[0,11],design:[9,24],det_limit_asdataarrai:2,detection_limit:[2,5],detection_typ:2,detection_wavelength:2,develop:[9,11,19,20],dict:[2,7,12,16],dictionari:7,dicycl:5,differ:[2,19,24],differentcloudmaskexist:2,differentheaderexist:2,dimens:2,dimension:2,direct:20,directli:19,directori:[11,20,25],disable_test_elda_mwl_factori:[2,8],distanc:2,divid:2,doing:19,done:[11,20],dopreparebscsign:2,doprepareextsign:2,dopreparesign:2,dsig:2,dsig_o:2,due:2,dump:2,each:[2,24],earlinet:24,easili:19,elast:[2,4],elast_backscatter_opt:5,elast_bsc_product:2,elast_sig:2,elastbackscatteropt:5,elastbscmethod:5,elda:[2,5,24],elda_current_product_id:5,elda_mwl:10,elda_mwl_factori:[8,13],elda_return_cod:5,eldamwl:[9,11,12,13,14,15,16,19,20,21,22,25,27,28],eldec:5,eldec_current_product_id:5,eldec_return_cod:5,elic:5,elic_current_product_id:5,elic_return_cod:5,elpp:[2,5,15,20,27],elpp_current_product_id:5,elpp_return_cod:5,elpp_sign:2,elppdata:2,elquick:5,elquick_current_product_id:5,elquick_return_cod:5,emission_wavelength:2,entri:2,environ:28,equat:2,err:2,error_cod:8,error_method:2,error_threshold_high:2,error_threshold_high_asdataarrai:2,error_threshold_low:2,error_threshold_low_asdataarrai:2,errormethod:5,errorthreshold:5,eta:2,etc:[2,19],etna:5,exact:16,exampl:[5,11,27],except:8,exclus:2,exist:[2,19],expand:19,ext:5,ext_bsc_opt:5,ext_param:2,extbscopt:5,extern:19,extinct:[2,4,11,16,20],extinction_factori:[8,11,12,13,14,16],extinction_opt:5,extinction_product:2,extinctionautosmooth:2,extinctionautosmoothdefault:[2,12],extinctionfactori:[2,18],extinctionfactorydefault:[2,13,18],extinctionopt:5,extinctionparam:2,extmethod:5,factor:2,factori:[6,8,11,15,16,19,20,21],factoryregistri:2,fail:2,fals:[2,16],fernald:2,file:[2,7,25,27,28],filenam:5,fill:[2,7],fill_tabl:7,filltablefail:2,filter:2,filtered_id:2,filtered_list:2,find_class_by_nam:2,first:[11,16,20],fit:[2,11,16],fixed_lr:5,fixed_lr_error:5,flow:24,follow:16,foreseen:20,forfir:5,found:[2,7,19],from:[2,4,5,7,11,16,20,24,25,28],from_db:2,from_depol_compon:2,from_id:2,from_nc_fil:2,from_queri:2,from_sign:2,funcaplusb:6,fundament:19,further:24,futur:2,gain:2,gain_factor:2,gain_factor_correct:2,gener:[2,4,19,22,27],general_param:2,generalproductparam:2,get:[2,4],get_basic_product:[8,13],get_bsc_cal_params_queri:4,get_class:2,get_classname_from_db:[2,16],get_connect_str:4,get_factory_registr:2,get_general_params_queri:4,get_product:2,get_products_queri:4,getb:6,getbasicproduct:[2,18],getbasicproductsdefault:[2,13,18],getcombinedsign:2,give:7,given:2,global:[2,9,19,21,24],global_product_list:2,golai:11,handl:[3,4,19,21,25],have:[2,11,20,28],header:2,height:2,here:[11,19,22,27],high:2,hirelpp:5,hirelpp_current_product_id:5,hirelpp_return_cod:5,holder:[3,25],ids:4,idx_in_fil:2,implement:[0,2,15,16,19,22,24],improv:24,includ:[2,28],includes_product_merg:2,independ:24,index:[2,24],indic:24,individu:4,inform:[2,3,25,28],init:2,init_engin:4,initi:[2,5],input:[12,13,14,27],instal:24,instanc:[2,5,7,19,21,27],integr:2,intellig:2,interfac:16,interface_return_cod:5,intermedi:2,interpolation_id:5,introduc:19,is_basic_product:5,is_bsc_from_depol_compon:2,is_cross_sig:2,is_elast_sig:2,is_fr_sign:2,is_in_mwl_product:5,is_mwl_only_product:5,is_nr_sign:2,is_parallel_sig:2,is_raman_sig:2,is_refl_sig:2,is_total_sig:2,is_transm_sig:2,is_wv_sig:2,its:28,itself:2,just:[3,19,25],kei:[2,5,16],keyword:[2,11,16,20],klass:2,klass_nam:2,klett:2,kwarg:[2,5,6,11,16,20],laser:2,laser_pointing_angle_of_profil:2,last:[11,16,20],latitud:2,layer:19,lev:16,level:[2,16,19],lidar:[2,4,5,24],lidar_ratio:[2,4],lidar_ratio_factori:8,lidar_ratio_file_id:5,lidarratioparam:2,like:[16,19,25],linear:[2,16],linfit:[2,14,16,18],link:[19,21],list:[2,4,7,19],lock:28,log:8,log_path:25,logarithm:2,logger:10,logist:13,longitud:2,look:[2,16],low:2,lowestheight:5,mai:25,main:8,make:19,map:5,mask:2,matryoshka:19,matti:0,max_height:5,max_smooth:2,maximum:25,meas_id:5,measur:[2,4,10],measurement_id:[2,4],measurement_param:2,measurementparam:2,memori:2,method:[2,4,5,6,7,11,16,20],might:[11,20],min_bscratio_for_lr:5,min_height:5,mocker:6,modifi:[19,25],modul:[8,11,20,24,25,27],modular:[9,24],molecular:2,more:2,multiwavelength:24,must:[2,4,19],mwl:4,mwl_prod_id:4,mwlproductproduct:5,mypath:25,mysql:27,name:[2,4,5,6,11,16,20],nan:2,nc_d:2,nc_file_id:5,nc_fill_str:16,ndarrai:14,necessari:2,need:[2,3,11,16,20,25,27],netcdf:[2,27],never:19,new_product:2,new_sign:2,next:11,non:[2,16],none:[2,4,7],nonweightedlinearfit:[2,14,16,18],normal:2,normalize_by_shot:2,notfoundinstorag:2,noth:7,number:2,numer:14,numpi:14,object:[2,4,7],occur:[2,20],often:14,old:24,one:[2,15,19,24],onli:[5,15,17,19,20],onlyoneoverrideallow:2,oper:2,operationa:6,operationb:6,optic:24,optimum:2,option:[2,4,9,11,16,20,28],order:27,origin:2,other:[9,24],out:28,outer:19,output:[12,13,14],overlap_file_id:5,overlapfil:5,overrid:[2,20,25],overwrit:[19,25],p_param:2,packag:[8,11,20,24,25,28],panda:2,param:[2,4,6,7,10],paramet:[2,3,4,7,25],paramsa:6,pars:7,part:9,particl:2,pass:2,path:[3,25,28],perform:[19,22],photosmog:5,pipenv:28,pipfil:28,place:[3,25],plugin:[2,11,20],point:2,pol_cal_idx:2,pol_calibr:2,pol_channel_conf:2,pre:27,prepar:[2,15,20],prepare_for_extinct:2,prepare_sign:[8,13,15,20],preparebscsign:[2,18],preparebscsignalsdefault:[2,13,18],prepared_sign:2,preparedsignalfil:5,prepareextsign:[2,15,18,20],prepareextsignalsbett:20,prepareextsignalsdefault:[2,13,15,18],preparesign:[2,18],preparesignalsdefault:[2,13,18],preprocessing_integration_tim:5,preprocessing_vertical_resolut:5,present:5,previous:2,print:[11,20],prior:7,process:[25,27],processor_id:5,prod_id:[2,4,16],prod_id_str:2,prod_param:2,prod_typ:2,product:[4,5,8,16,24],product_id:4,product_id_str:2,product_list:2,product_param:2,product_t:2,product_typ:5,productopt:5,productparam:2,producttyp:5,profil:2,program:[9,24],project:28,properti:[2,6,24],provid:[2,3,16,22,25,27],purpos:[19,24],put:2,python:[27,28],python_classnam:[5,16],queri:2,rais:2,raman:[2,4],raman_backscatter_opt:5,raman_bsc_product:2,ramanbackscatteropt:5,rang:[2,16],ratio:[2,4,5],rayl:2,rayleigh:2,read:[2,4,7,16],read_elpp_data:2,read_extinction_algorithm:[4,16],read_extinction_param:4,read_lidar_ratio_param:4,read_mwl_product_id:4,read_nc_fil:2,read_product_list:2,read_signal_filenam:4,read_system_id:4,read_task:[2,4],recommend:28,refin:7,refine_data:7,refl_sig:2,reflect:2,regist:[2,11,16,20],register_class:[2,11,16,20],registr:2,registri:[8,10,11,16,19,20],rel_err:2,relat:[2,5],relationship:5,remov:7,remove_db:7,replac:[9,19,24],repositori:28,repres:[2,19],represent:2,request:[2,6],requir:[3,24,25,26,28],res:16,resolut:2,respons:15,restrict:2,retirev:2,retriev:[2,4,11,12,15,16,20,24],right:19,run:[2,11,16,20,27,28],runeldamwl:[2,13,18],rurban:5,sahadust:5,same:2,save_to_netcdf:2,savgolayslop:11,savitzki:11,savitzkygolayslop:11,scale_factor_shot:2,scatter:2,scc:[2,11,16,24,27,28],search:2,select:[17,19,20],self:[11,16,20],seri:2,server:[3,25],set:[2,5,25],set_basic_product_auto_smooth:2,set_elpp_sign:2,set_invalid_point:2,set_prepared_sign:2,setup:[24,28],sever:2,shall:[2,4,16],shape:[2,7],shot:2,should:20,sig:2,sig_o:2,sig_refl:2,sig_slop:16,sig_tot:2,sig_transm:2,signal:[6,8,11,12,15,16,20],signalslop:[2,11,16,18],simpl:[5,12],singl:[2,24],site:2,skip:7,slope:[2,4,11,16],slope_err:[2,16],slope_routin:16,slopetoextinct:[2,18],slopetoextinctiondefault:[2,12,18],smooth:[2,25],smooth_param:2,some:[0,3,22,25],sounding_file_id:5,specif:[3,13,25,28],sqlalchemi:5,start:[2,5,16],statement:[11,20],station_altitud:2,station_latitud:2,station_longitud:2,statistical_error:2,statu:[2,5],step:2,stop:5,storag:[2,10],store:[2,16],str:[2,4,16],strato:5,string:4,structur:[9,24],stupid:14,sub_param:2,submission_d:5,submodul:8,subpackag:8,subset:2,subsystem:19,surround:19,synergi:24,system:[4,5,19,28],system_id:4,system_product:[2,4],systematic_error:2,systemproduct:5,tabl:[2,4,7,11,16,24],tempor:2,test:[2,8,9,24,27],test_factori:[2,8],test_factory_registr:6,test_measurementparam:6,test_param:[2,8],test_registri:[2,8],test_registry_regist:6,test_sign:[2,8],test_signals_from_nc_fil:6,test_signals_regist:6,than:2,thei:[2,19],them:[2,16],thi:[2,3,4,11,16,19,20,25],third:16,those:[2,3,25],time:[2,16],topheight:5,total:2,transm_sig:2,transmiss:2,transmit:2,two:[2,11,16,19],type:[2,4,24],under:2,updat:28,update_auth_user_id:5,updated_d:5,upload:5,use:[2,19],used:[2,4,16,20,24],user:[2,17,19,20,25],using:[2,5,28],utf:[11,20,25],util:2,valu:[2,5,25],variabl:2,variable_nam:2,veri:14,version:28,vertic:2,via:2,virtual:28,virtualenv:28,volkers_db_funct:[2,4],want:[11,20],wavelength:[2,24],weight:[2,16],weightedlinearfit:[2,14,16,18],well:11,when:2,where:2,whether:2,which:[2,3,4,11,16,19,20,25,27,28],window:16,window_data:16,windowwidth:5,within:[2,28],without:19,write:2,written:2,x_data:[2,16],xarrai:[2,12],y_data:[2,16],yerr_data:[2,16],you:[3,11,20,25,27,28],your:[3,25,28]},titles:["Algorithms and Flow Charts","prepare signals","ELDAmwl package","ELDAmwl.configs package","ELDAmwl.database package","ELDAmwl.database.tables package","ELDAmwl.tests package","ELDAmwl.tests.database package","ELDAmwl","Contributing","Global data structures","Provide an additional user-selectable algorithm subsystem","Basic BaseOperation classes","Complex BaseOperation classes","Fundamental BaseOperation classes","Example for an algorithm subsystem with no alternatives","Example of an additional user-selectable algorithm subsystem","Examples","Overview on modularized algorithm subsystems","Modularity","Overwrite an existing algorithm subsystem","The Registry class","Testing","Index","Welcome to ELDAmwl\u2019s documentation!","Configuration","Installation and setup","Requirements","Installation","Module Index"],titleterms:{"class":[12,13,14,21],The:21,addit:[11,16],algorithm:[0,11,15,16,18,20],altern:15,backscatt:5,backscatter_factori:2,baeoperationfactori:[],base:2,baseoper:[12,13,14,18],baseoperationfactori:18,basic:12,chart:0,column:2,complex:13,config:3,config_default:3,config_exampl:3,config_example_linux:3,configur:25,constant:2,content:[2,3,4,5,6,7],contribut:9,correspond:18,create_test_db:7,data:10,data_storag:2,databas:[4,5,7],db_base:5,db_function:4,disable_test_elda_mwl_factori:6,document:24,elda_mwl_factori:2,eldamwl:[2,3,4,5,6,7,8,24],error_cod:2,exampl:[15,16,17],except:2,exist:20,extinct:5,extinction_factori:2,factori:2,flow:0,fundament:14,get_basic_product:2,global:10,index:[23,29],instal:[26,28],lidar_ratio:5,lidar_ratio_factori:2,list:18,log:2,main:2,measur:5,modul:[2,3,4,5,6,7,29],modular:[18,19],overview:18,overwrit:20,packag:[2,3,4,5,6,7],prepar:1,prepare_sign:2,product:2,provid:11,registri:[2,21],requir:27,select:[11,16],setup:26,signal:[1,2],step:[11,20],structur:10,submodul:[2,3,4,5,6,7],subpackag:[2,4,6],subsystem:[11,15,16,18,20],system_product:5,tabl:5,test:[6,7,22],test_factori:6,test_param:6,test_registri:6,test_sign:6,user:[11,16],volkers_db_funct:5,welcom:24}})