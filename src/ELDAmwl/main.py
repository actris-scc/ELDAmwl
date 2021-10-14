# -*- coding: utf-8 -*-
import logging
import sys
import traceback

from ELDAmwl.errors.error_codes import NO_ERROR, UNKNOWN_EXCEPTION
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.utils.constants import ELDA_MWL_VERSION
from ELDAmwl.database.db_functions import register_db_utils
from ELDAmwl.factories.elda_mwl_factories import RunELDAmwl
from ELDAmwl.errors.exceptions import ELDAmwlException, WrongCommandLineParameter
from ELDAmwl.log.log import register_logger

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


class Main:

    logger = logging.Logger

    def handle_args(self):
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

        return args

    def elda_init(self):
        """
        Initialization of the ELDA environment
        """

        # Read command line paramters
        try:
            args = self.handle_args()
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

        # Get the measurement ID from the command line
        meas_id = args.meas_id

        # Setup the logging facility for this measurement ID
        self.logger = register_logger(meas_id)
        # register_plugins()

        # customize the logger according to command line parameters
        if args.ll_file:
            if args.ll_file == 'QUIET':
                self.logger.disabled = True
            else:
                self.logger.setLevel(args.ll_file)

        self.logger.info('welcome to the EARLINET Lidar Data Analyzer for \
                           multi-wavelengths measurements (ELDAmwl)')
        self.logger.info('ELDAmwl version: {0}'.format(ELDA_MWL_VERSION))
        self.logger.info('analyze measurement number: ' + meas_id)

        # Bring up the global db_access
        register_db_utils()

        # Bring up the global data storage
        register_datastorage()

        return meas_id

    def elda(self):
        """
        Todo Ina Missing doc
        """
        meas_id = self.elda_init()

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

        self.logger.info('the end')

    def run(self):

        try:
            self.elda()

            sys.exit(NO_ERROR)

        except ELDAmwlException as e:
            self.logger.error('exception raised {0} {1}'.format(e.return_value, e))
            sys.exit(e.return_value)

        except Exception as e:
            self.logger.error('unknown exception raised {0}'.format(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for line in traceback.format_tb(exc_traceback):
                self.logger.error("exception: %s" % (line[:-1]))
            sys.exit(UNKNOWN_EXCEPTION)


if __name__ == '__main__':
    main = Main()
    main.run()
