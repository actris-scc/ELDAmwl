# -*- coding: utf-8 -*-

from logging import log, INFO, ERROR

from ELDAmwl.log import create_logger

from ELDAmwl.registry import registry
from ELDAmwl.elda_mwl_factories import RunELDAmwl
from ELDAmwl.constants import ELDA_MWL_VERSION

try:
    import ELDAmwl.configs.config as cfg
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg

#registry.status()


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
log(INFO, 'ELDAmwl version: {}'.format(ELDA_MWL_VERSION) );
log(INFO, 'analyze measurement number: ' + meas_id);

elda_mwl = RunELDAmwl(meas_id)
elda_mwl.read_tasks()
#elda_mwl.read_signals()
#db_functions.read_extinction_options(ext_id)

log(INFO,'the end')
