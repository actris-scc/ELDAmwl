# -*- coding: utf-8 -*-
import os

from ELDAmwl.component.interface import ICfg, IDBFunc
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
from ELDAmwl.storage.cached_functions import gen_sg_params
from ELDAmwl.storage.data_storage import register_datastorage
from ELDAmwl.utils.constants import ELDA_MWL_VERSION, EXIT_CODE_NONE, MWL_PROD_ID_DEFAULT
from zope import component

import argparse
import sys
import traceback


def elda_setup_components(args=None):
    # Get the configuration
    register_config(args)

    # Setup the logging facility for this measurement ID
    register_logger(args.meas_id)
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

    gen_sg_params()


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
        # print(f'command line arguments {args}')

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

        self.logger.info('welcome to the EARLINET Lidar Data Analyzer for '
                         'multi-wavelengths measurements (ELDAmwl)')
        self.logger.info('ELDAmwl version: {0}'.format(ELDA_MWL_VERSION))
        self.logger.info('analyze measurement number: ' + meas_id)

        return args

    def elda(self, arg_dict):
        """
        Todo Ina Missing doc
        """

        try:
            self.logger.meas_id = arg_dict.meas_id
            elda_mwl = RunELDAmwl(arg_dict.meas_id)
            elda_mwl.read_tasks()
            elda_mwl.read_elpp_data()
            elda_mwl.prepare_signals()
            elda_mwl.get_basic_products()
            elda_mwl.get_derived_products()
            elda_mwl.get_lidar_constants()
            elda_mwl.quality_control()
            elda_mwl.get_product_matrix()
            elda_mwl.write_mwl_output()
            return_code = elda_mwl.get_return_value()

            self.logger.info('the happy end')

        except ELDAmwlException as e:
            dbfunc = component.queryUtility(IDBFunc)
            dbfunc.write_product_status_in_db(arg_dict.meas_id, MWL_PROD_ID_DEFAULT, None, e.return_value, str(e))
            return_code = EXIT_CODE_NONE

        return return_code

    def run(self):

        try:
            args = self.elda_cmdline()
            return_code = self.elda(args)

            sys.exit(return_code)

        # ELDAmwlExceptions are caught in self.elda
        # except ELDAmwlException as e:
        #     if not self.logger:
        #         print(f'exception raised {e.return_value} {e}')  # noqa T001
        #     else:
        #         self.logger.error(f'exception raised {e.return_value} {e}')
        #     sys.exit(EXIT_CODE_NONE)

        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            if not self.logger:
                print(f'unknown exception raised {e}')
                for line in traceback.format_tb(exc_traceback):
                    print(f'exception: {line[:-1]}')  # noqa P103
            else:
                self.logger.error(f'unknown exception raised {e}')
                for line in traceback.format_tb(exc_traceback):
                    self.logger.error(f'exception: {line[:-1]}')  # noqa P103
            sys.exit(EXIT_CODE_NONE)


def run():
    main = Main()
    main.run()


if __name__ == '__main__':
    run()
