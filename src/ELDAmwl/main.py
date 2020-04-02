# -*- coding: utf-8 -*-

from ELDAmwl.constants import ELDA_MWL_VERSION
from ELDAmwl.elda_mwl_factories import RunELDAmwl
from ELDAmwl.log import create_logger
from ELDAmwl.log import logger


try:
    import ELDAmwl.configs.config as cfg  # noqa E401
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg  # noqa E401

# registry.status()


meas_id = '20181017oh00'
# hoi_system_id =182 (RALPH Bauhof night)
# products=
#   328: Rbsc&Depol 532, uc7
#   379: LR 355 (377+378)
#   381: LR 532 (324 + 380)
#   330: EBsc 1064
#   378: RBsc 355
#   377: Ext 355
#   380: Ext 532
#   598: mwl (378 + 379)

def main():
    ext_id = 377

    create_logger(meas_id)

    logger.info('welcome to the EARLINET Lidar Data Analyzer for \
               multi-wavelengths measurements (ELDAmwl)')
    logger.info('ELDAmwl version: {0}'.format(ELDA_MWL_VERSION))
    logger.info('analyze measurement number: ' + meas_id)

    elda_mwl = RunELDAmwl(meas_id)
    elda_mwl.read_tasks()
    elda_mwl.read_elpp_data()
    elda_mwl.prepare_signals()
    elda_mwl.get_basic_products()

    logger.info('the end')

if __name__ =='__main__':
    main()
