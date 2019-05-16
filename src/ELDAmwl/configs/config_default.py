# -*- coding: utf-8 -*-

from logging import INFO, DEBUG

from ELDAmwl.registry import Registry

# ===================
# Directories
# ===================

LOG_PATH = 'd:/myprograms/FPC/ELDA/log'
SIGNAL_PATH = 'd:/myprograms/FPC/ELDA/intermediate/cfFormat72hExercise'
PRODUCT_PATH = 'd:/myprograms/FPC/ELDA/output'
SAVGOL_FILE = 'd:/myprograms/FPC/ELDA/input/Savitzky_Golay.txt'
TEMP_PATH = 'd:/temp'


# database connection

DB_SERVER = 'localhost'
DB_USER = 'earlinet'
DB_PASS = 'dwdlidar'
DB_DB = 'scc_dev_20190228'

# ===================
# Logging
# ===================

# The logfiles
#general log level
log_level = DEBUG
# The desired loglevel for console output
log_level_console = INFO
# The desired loglevel for the logfile
log_level_file = INFO
# Colors for the log console output (Options see colorlog-package)
log_colors = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bg_white',
}

WRITE_EXTENDED_OUTPUT = True
APPEND_LOG_FILE = False


# ===================
# Time strings
# ===================

STRP_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
