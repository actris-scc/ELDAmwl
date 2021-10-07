# -*- coding: utf-8 -*-
from logging import ERROR
from logging import FileHandler
from logging import Formatter
from logging import getLogger
from logging import log
from logging import StreamHandler
from sys import stdout

import os


from ELDAmwl.exceptions import LogPathNotExists

try:
    import ELDAmwl.configs.config as cfg
except ImportError:
    import ELDAmwl.configs.config_default as cfg


try:
    import colorlog
    from colorlog import ColoredFormatter

    formatter = ColoredFormatter(
                                    '%(log_color)s%(asctime)s [%(process)d] '
                                    '%(levelname)-8s %(message)s',
                                    datefmt=None,
                                    reset=True,
                                    log_colors=cfg.log_colors,
                                    secondary_log_colors={},
                                    style='%',
                                    )
    logger = colorlog.getLogger('ELDAmwl')

except Exception as e:  # noqa E841
    #   print(e)
    logger = getLogger('ELDAmwl')
    formatter = Formatter('%(asctime)s [%(process)d] '
                          '%(levelname)-8s %(message)s',
                          '%Y-%m-%d %H:%M:%S')

logger.setLevel(cfg.log_level)


console_handler = StreamHandler(stdout)
# formatter = Formatter('%(asctime)s %(levelname)-8s %(message)s',
#                      '%Y-%m-%d %H:%M:%S')
console_formatter = formatter
console_handler.setFormatter(console_formatter)
console_handler.setLevel(cfg.log_level_console)
logger.addHandler(console_handler)


def create_logger(meas_id):
    if not os.path.exists(cfg.LOG_PATH):
        log(ERROR,
            'Log file directory does not exists {path}, please create it '.
            format(path=cfg.LOG_PATH))
        raise LogPathNotExists

    file_handler = FileHandler(os.path.join(cfg.LOG_PATH,
                                            '{id}.log'.format(id=meas_id)))
    file_handler_formatter = formatter
    file_handler.setFormatter(file_handler_formatter)
    file_handler.setLevel(cfg.log_level_file)
    logger.addHandler(file_handler)
