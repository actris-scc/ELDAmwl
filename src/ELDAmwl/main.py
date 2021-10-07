# -*- coding: utf-8 -*-
import sys
import traceback

from ELDAmwl.constants import ELDA_MWL_VERSION
from ELDAmwl.elda_mwl_factories import RunELDAmwl
from ELDAmwl.exceptions import ELDAmwlException, UNKNOWN_EXCEPTION, WrongCommandLineParameter, NO_ERROR
from ELDAmwl.log import create_logger
from ELDAmwl.log import logger
# This import is mandatory
from ELDAmwl.plugins import register_plugins

import argparse


try:
    import ELDAmwl.configs.config as cfg  # noqa E401
except ModuleNotFoundError:
    import ELDAmwl.configs.config_default as cfg  # noqa E401


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

    parser.add_argument('-l', dest='ll_file', default='DEBUG', type=str,
                        choices=['QUIET', 'CRITICAL', 'ERROR',
                                 'WARNING', 'INFO', 'DEBUG'],
                        help='how many output is written to the '
                             'log file. default = debug')

    #    parser.add_argument('-L', dest='ll_db', default='QUIET', type=str,
    #                        choices=['QUIET', 'CRITICAL', 'ERROR',
    #                        'WARNING', 'INFO', 'DEBUG'],
    #                        help='how many output is written to the
    #                        SCC database. default = info')

    args = parser.parse_args()

    if args.ll_file:
        if args.ll_file == 'QUIET':
            logger.disabled = True
        else:
            logger.setLevel(args.ll_file)

    return args.meas_id


def main():

    try:
        try:
            meas_id = handle_args()
            # todo: transform system errors to exception
            # SystemError: error return without exception set
            # error: the following arguments are required: meas_id
            # returns 2
            #
            # main.py: error: unrecognized arguments: -d
            # returns 2
            #
            # main.py: error: argument - l: invalid choice
            # returns 2
        except Exception:
            raise WrongCommandLineParameter

        create_logger(meas_id)
        # register_plugins()

        logger.info('welcome to the EARLINET Lidar Data Analyzer for \
                   multi-wavelengths measurements (ELDAmwl)')
        logger.info('ELDAmwl version: {0}'.format(ELDA_MWL_VERSION))
        logger.info('analyze measurement number: ' + meas_id)

        elda_mwl = RunELDAmwl(meas_id)
        elda_mwl.read_tasks()
        elda_mwl.read_elpp_data()
        elda_mwl.prepare_signals()
        elda_mwl.get_basic_products()
        elda_mwl.get_derived_products()

#        elda_mwl.write_single_output()
        elda_mwl.get_product_matrix()
        elda_mwl.quality_control()
        elda_mwl.write_mwl_output()

        logger.info('the end')

        sys.exit(NO_ERROR)

    except ELDAmwlException as e:
        logger.error('exception raised {0} {1}'.format(e.return_value, e))
        sys.exit(e.return_value)

    except Exception as e:
        logger.error('unknown exception raised {0}'.format(e))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for line in traceback.format_tb(exc_traceback):
            logger.error("exception: %s" % (line[:-1]))
        sys.exit(UNKNOWN_EXCEPTION)


if __name__ == '__main__':

    main()
