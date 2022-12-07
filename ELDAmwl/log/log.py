# -*- coding: utf-8 -*-
from ELDAmwl.component.interface import ICfg
from ELDAmwl.component.interface import IDBFunc
from ELDAmwl.component.interface import ILogger
from ELDAmwl.errors.exceptions import LogPathNotExists
from ELDAmwl.utils.path_utils import dir_not_found_hint
from logging import ERROR
from logging import FileHandler
from logging import Formatter
from logging import getLogger
from logging import StreamHandler
from sys import stdout
from zope import component

import datetime
import ELDAmwl
import os
import zope


# Log level codes according to DB-Definition and syslog
SYSLOG_ERROR = 3
SYSLOG_WARN = 4
SYSLOG_INFO = 6
SYSLOG_DEBUG = 7


@zope.interface.implementer(ILogger)
class Logger:
    """
    Logger class for logging to console, file and DB
    """
    logger = None
    db_log_func = None
    db_log_level = None
    meas_id = None

    def __init__(self, measurement_id):
        self.module_version = '4711'
        self.meas_id = measurement_id
        self.setup_logger()

    @property
    def cfg(self):
        return component.queryUtility(ICfg)

    def log_message(self, prod_id, msg):
        out_msg = '{}:{}: {}'.format(self.meas_id, prod_id, msg)
        return out_msg

    def critical(self, msg, prod_id=None):
        self.logger.critical(self.log_message(prod_id, msg))
        self.db_log(SYSLOG_ERROR, prod_id, msg)

    def fatal(self, msg, prod_id=None):
        self.logger.fatal(self.log_message(prod_id, msg))
        self.db_log(SYSLOG_ERROR, prod_id, msg)

    def error(self, msg, prod_id=None):
        self.logger.error(self.log_message(prod_id, msg))
        self.db_log(SYSLOG_ERROR, prod_id, msg)

    def warning(self, msg, prod_id=None):
        self.logger.warning(self.log_message(prod_id, msg))
        self.db_log(SYSLOG_WARN, prod_id, msg)

    def info(self, msg, prod_id=None):
        self.logger.info(self.log_message(prod_id, msg))
        self.db_log(SYSLOG_INFO, prod_id, msg)

    def debug(self, msg, prod_id=None):
        self.logger.debug(self.log_message(prod_id, msg))
        self.db_log(SYSLOG_DEBUG, prod_id, msg)

    def setLevel(self, level):
        # ToDo unclear how to manage levels here
        self.logger.setLevel(level)
        self.db_log_level = level

    def get_logger_formatter(self):
        """
        Check if a colored log is possible. Return get_logger and formatter instance.
        """
        try:
            from colorlog import ColoredFormatter

            import colorlog

            formatter = ColoredFormatter(
                '%(log_color)s%(asctime)s [%(process)d] '
                '%(levelname)-8s %(message)s',
                datefmt=None,
                reset=True,
                log_colors=self.cfg.log_colors,
                secondary_log_colors={},
                style='%',
            )
            get_logger = colorlog.getLogger


        except Exception as e:  # noqa E841
            #   print(e)
            get_logger = getLogger
            formatter = Formatter(
                '%(asctime)s [%(process)d] '
                '%(levelname)-8s %(message)s',
                '%Y-%m-%d %H:%M:%S',
            )
        return get_logger, formatter

    def setup_console_logger(self, formatter):
        """Console logger"""
        console_handler = StreamHandler(stdout)
        console_formatter = formatter
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(self.cfg.log_level_console)
        self.logger.addHandler(console_handler)

    def setup_file_logger(self, formatter):
        """
        File logger
        Has to be setup when the output filename is known
        """
        if not os.path.exists(self.cfg.LOG_PATH):
            self.error(ERROR, """Log file directory "{path}" does not exists""".format(path=self.cfg.LOG_PATH))
            dir_not_found_hint(self.cfg.LOG_PATH)
            raise LogPathNotExists

        log_file_path = os.path.join(
            self.cfg.LOG_PATH,
            '{id}.log'.format(id=self.meas_id),
        )
        file_handler = FileHandler(log_file_path)
        file_handler_formatter = formatter
        file_handler.setFormatter(file_handler_formatter)
        file_handler.setLevel(self.cfg.log_level_file)
        self.logger.addHandler(file_handler)

    def setup_db_logger(self):
        """
        Setup the DB logger. Should be called from the outside after a DB connection is established
        """
        self.db_log_func = component.queryUtility(IDBFunc).db_log

    def setup_logger(self):
        """
        Staggered setup of loggers.
        First the console logger will come up, then the file logger.
        The db logger has to be brought up via an external call after the DB connection is ensured-
        """
        get_logger, formatter = self.get_logger_formatter()
        self.logger = get_logger('ELDAmwl')
        self.logger.setLevel(self.cfg.log_level)

        self.setup_console_logger(formatter)
        self.setup_file_logger(formatter)

    def db_log(self, level, prod_id, msg):
        if self.db_log_func is None:
            return
        now = datetime.datetime.now()
        self.db_log_func(
            level,
            now,
            self.meas_id,
            prod_id,
            ELDAmwl.__version__,
            msg)


def register_logger(measurement_id):
    # prohibit more than one logger instance
    logger = component.queryUtility(ILogger)
    if logger is not None:
        return logger

    logger = Logger(measurement_id)  # ToDo Ina Where to get the module_version for logging ?
    component.provideUtility(logger, ILogger)
    return logger


def register_db_logger():
    # prohibit more than one logger instance
    logger = component.queryUtility(ILogger)
    logger.setup_db_logger()
