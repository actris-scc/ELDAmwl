# -*- coding: utf-8 -*-
import argparse
import importlib

from ELDAmwl.constants import ELDA_MWL_VERSION
from ELDAmwl.elda_mwl_factories import RunELDAmwl
from ELDAmwl.log import create_logger
from ELDAmwl.log import logger
from ELDAmwl.plugins import plugin


try:
    import ELDAmwl.configs.config as cfg  # noqa E401
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg  # noqa E401

# registry.status()


# meas_id = '20181017oh00'
# hoi_system_id =182 (RALPH Bauhof night)
# products=
#   328: Rbsc&Depol 532 (RBsc pid = 324), uc7 (without depol combination)
#   channels    453: elPP
#               454: elCP
#               395: vrRN2
#               445: elT
#   324: RBsc 532, uc7 (with depol comb)
#   379: LR 355 (377+378)
#   381: LR 532 (324 + 380)
#   330: EBsc 1064
#   378: RBsc 355
#   377: Ext 355
#   380: Ext 532
#   598: mwl (378 + 379 + 328)

def handle_args():
    parser = argparse.ArgumentParser(description='EARLINET Lidar Data Analyzer for \
                       multi-wavelengths measurements')

    parser.add_argument('meas_id', metavar='meas_id', type=str,
                        help='the id of a measurement')

    parser.add_argument('-i', dest='proc_inst', default=None, type=str,
                        help='processing_inst: name of the institution \
                            at which this code is running')

    # parser.add_argument('-c', dest='config_file', default=None, type=str,
    #                     help='name of config_file. It must be located in the path '
    #                          'ELDAmwl/src/configs, has the extension .py, and follow the'
    #                          'structure of config_default.py in this directory')
    #
    parser.add_argument('-l', dest='ll_file', default='DEBUG', type=str,
                        choices=['QUIET', 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
                        help='how many output is written to the log file. default = debug')

    #    parser.add_argument('-L', dest='ll_db', default='QUIET', type=str,
    #                        choices=['QUIET', 'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
    #                        help='how many output is written to the SCC database. default = info')

    args = parser.parse_args()

    # if args.config_file:
    #     try:
    #         conf_file = 'configs.' + args.config_file[:-3]
    #         cfg = importlib.import_module(conf_file)
    #     except ModuleNotFoundError:
    #         logger.error('cannot find config file {0} in path'
    #                      'ELDAmwl/src/configs'.format(args.config_file[:-3] + '.py'))
    #         import ELDAmwl.configs.config as cfg

    if args.ll_file:
        if args.ll_file == 'QUIET':
            logger.disabled = True
        else:
            logger.setLevel(args.ll_file)

    return args.meas_id


def main(meas_id):
    # ext_id = 377

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


if __name__ == '__main__':
    meas_id = handle_args()

    main(meas_id)
