# -*- coding: utf-8 -*-
from ELDAmwl.component.interface import ICfg
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from ELDAmwl.config import register_config
from ELDAmwl.database.db_functions import register_db_func
from ELDAmwl.elda_mwl.elda_mwl import register_params
from ELDAmwl.elda_mwl.elda_mwl import RunELDAmwl
from ELDAmwl.errors.error_codes import NO_ERROR
from ELDAmwl.errors.error_codes import UNKNOWN_EXCEPTION
from ELDAmwl.errors.exceptions import ELDAmwlException
from ELDAmwl.errors.exceptions import WrongCommandLineParameter
from ELDAmwl.log.log import register_db_logger
from ELDAmwl.log.log import register_logger
from ELDAmwl.monte_carlo.operation import register_monte_carlo
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.utils.constants import ELDA_MWL_VERSION
from zope import component

import argparse
import sys
import traceback


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


def elda_setup_components(args=None, env='Production'):
    # Get the configuration
    register_config(args, env=env)

    # Setup the logging facility for this measurement ID
    register_logger()
    # register_plugins()

    # Bring up the global db_access
    register_db_func()

    # Bring up DB logger
    register_db_logger()

    # Bring up the global data storage
    register_datastorage()

    # Bring up the global parameter instance
    register_params()

    # REgister MontaCarlo Adapter
    register_monte_carlo()


class Main:

    @property
    def logger(self):
        return component.queryUtility(ILogger)

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    @property
    def params(self):
        return component.queryUtility(IParams)

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

        parser.add_argument('-c', dest='config_dir', default='.', type=str,
                            help='Config directory. default = "."')

        #    parser.add_argument('-L', dest='ll_db', default='QUIET', type=str,
        #                        choices=['QUIET', 'CRITICAL', 'ERROR',
        #                        'WARNING', 'INFO', 'DEBUG'],
        #                        help='how many output is written to the
        #                        SCC database. default = info')

        args = parser.parse_args()

        return args

    def elda_cmdline(self):
        """
        Parse the CMD line arguments
        """

        # Read command line paramters
        try:
            args = self.handle_args()
            # todo: transform system errors to exception
            # SystemError: error return without exception set
            # error: the following arguments are required: meas_id
            # returns 2
            #
            # elda_mwl.py: error: unrecognized arguments: -d
            # returns 2
            #
            # elda_mwl.py: error: argument - l: invalid choice
            # returns 2
        except Exception:
            raise WrongCommandLineParameter

        # Get the measurement ID from the command line
        meas_id = args.meas_id

        elda_setup_components(args=args)

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

        return args

    def elda(self, arg_dict):
        """
        Todo Ina Missing doc
        """

        self.logger.meas_id = arg_dict.meas_id
        elda_mwl = RunELDAmwl(arg_dict.meas_id)
        elda_mwl.read_tasks()
        elda_mwl.read_elpp_data()
        elda_mwl.prepare_signals()
        elda_mwl.get_basic_products()
        elda_mwl.get_derived_products()
        elda_mwl.get_lidar_constants()

        #        elda_mwl.write_single_output()
        elda_mwl.get_product_matrix()
        elda_mwl.quality_control()
        elda_mwl.write_mwl_output()
        return_code = elda_mwl.get_return_value()

        self.logger.info('the happy end')

        return return_code

    def run(self):

        try:
            args = self.elda_cmdline()
            return_code = self.elda(args)

            sys.exit(return_code)

        # todo: exit codes corresponding to needs of deamon
        except ELDAmwlException as e:
            if not self.logger:
                print('exception raised {0} {1}'.format(e.return_value, e))  # noqa T001
            else:
                self.logger.error('exception raised {0} {1}'.format(e.return_value, e))
            sys.exit(e.return_value)

        except Exception as e:
            self.logger.error('unknown exception raised {0}'.format(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for line in traceback.format_tb(exc_traceback):
                self.logger.error('exception: {}' % (line[:-1]))  # noqa P103
            sys.exit(UNKNOWN_EXCEPTION)


def run():
    main = Main()
    main.run()


if __name__ == '__main__':
    run()
