# -*- coding: utf-8 -*-
from prefect.executors import DaskExecutor

from ELDAmwl.component.interface import ICfg
from ELDAmwl.component.interface import ILogger
from ELDAmwl.component.interface import IParams
from ELDAmwl.component.setup import ELDASetupComponents
from ELDAmwl.elda_mwl.elda_mwl import read_tasks, read_elpp_data, prepare_signals, get_basic_products, \
    get_derived_products, get_product_matrix, quality_control, write_mwl_output, read_params
from ELDAmwl.elda_mwl.elda_mwl import RunELDAmwl
from ELDAmwl.errors.error_codes import NO_ERROR
from ELDAmwl.errors.error_codes import UNKNOWN_EXCEPTION
from ELDAmwl.errors.exceptions import ELDAmwlException
from ELDAmwl.errors.exceptions import WrongCommandLineParameter
from ELDAmwl.utils.constants import ELDA_MWL_VERSION
from zope import component
from prefect.run_configs import UniversalRun


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

        parser.add_argument('-g', dest='test_data', default=None, type=str,
                            help='Class for which testdata should be generated. default = None')

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
        elda_mwl = RunELDAmwl()
        esc = ELDASetupComponents()
        rp = read_params()
        rt = read_tasks()
        rep = read_elpp_data()
        ps = prepare_signals()
        gbp = get_basic_products()
        gdp= get_derived_products()
        elda_mwl.set_dependencies(task=esc)
        elda_mwl.set_dependencies(task=rp, upstream_tasks=[esc], keyword_tasks=dict(meas_id=arg_dict.meas_id))
        elda_mwl.set_dependencies(task=rt, upstream_tasks=[rp])
        elda_mwl.set_dependencies(task=rep, upstream_tasks=[rt])
        elda_mwl.set_dependencies(task=ps, upstream_tasks=[rep])
        elda_mwl.set_dependencies(task=gbp, upstream_tasks=[ps])
        elda_mwl.set_dependencies(task=gdp, upstream_tasks=[gbp])

        gpm = get_product_matrix()
        qc = quality_control()
        wmo = write_mwl_output()
        #        elda_mwl.write_single_output()
        elda_mwl.set_dependencies(task=gpm, upstream_tasks=[gdp])
        elda_mwl.set_dependencies(task=qc, upstream_tasks=[gpm])
        elda_mwl.set_dependencies(task=wmo, upstream_tasks=[qc])
#        elda_mwl.visualize()
        executor = DaskExecutor(address='dask_master:8786')
        elda_mwl.executor = executor

        elda_mwl.run()
        elda_mwl.register(project_name="ELDAmwl")
        elda_mwl.run_agent()
#        elda_mwl.run()

        self.logger.info('the happy end')

    def run(self):

        try:
            meas_id = self.elda_cmdline()
            self.elda(meas_id)

            sys.exit(NO_ERROR)

        except ELDAmwlException as e:
            self.logger.error('exception raised {0} {1}'.format(e.return_value, e))
            sys.exit(e.return_value)

        except Exception as e:
            self.logger.error('unknown exception raised {0}'.format(e))
            exc_type, exc_value, exc_traceback = sys.exc_info()
            for line in traceback.format_tb(exc_traceback):
                self.logger.error('exception: {}' % (line[:-1]))  # noqa P103
            sys.exit(UNKNOWN_EXCEPTION)


def run():
    ELDASetupComponents().run()
    main = Main()
    main.run()


if __name__ == '__main__':
    run()
