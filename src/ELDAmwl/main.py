# -*- coding: utf-8 -*-

from logging import log, INFO, ERROR

#from ELDAmwl.database.db import DBUtils
#from ELDAmwl.database import db_functions
from ELDAmwl.log import create_logger

from ELDAmwl.registry import registry
from ELDAmwl.elda_mwl_factories import RunELDAmwl
#from ELDAmwl.signals import Signals

try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg

#import ELDAmwl.plugins.plugin

registry.status()


meas_id = '20181017oh00'
#hoi_system_id =182 (RALPH Bauhof night)
#products=
#   328: Rbsc&Depol 532, uc7
#   379: LR 355 (377+378)
#   381: LR 532
#   330: EBsc 1064
#   378: RBsc 355
#   377: Ext 355
#   598: mwl (378 + 379)

ext_id = 377

create_logger(meas_id)

log(INFO,'welcome to the EARLINET Lidar Data Analyzer for multi-wavelengths measurements (ELDAmwl)')
log(INFO, 'ELDA version: ' );
log(INFO, 'analyze measurement number: ' + meas_id);

elda_mwl = RunELDAmwl(meas_id)
elda_mwl.read_tasks()
elda_mwl.read_signals()
#sig = Signals.from_nc_file('K:\\auswertung\Mattis\myPrograms\python\ELDAmwl\data\intermediate\\20181017oh00_0000379.nc', 0)

#db_utils = DBUtils()

#db_functions.read_extinction_options(ext_id)
#db_utils.read_tasks(meas_id)

#extinction = Extinction('Huhu Params').get_product()

log(INFO,'the end')
