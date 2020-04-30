# -*- coding: utf-8 -*-

from logging import DEBUG
from logging import INFO


# ===================
# Directories
# ===================

LOG_PATH = ''
SIGNAL_PATH = ''
PRODUCT_PATH = ''
TEMP_PATH = ''
PLUGINS_DIR = ''

# ===================
# database connection
# ===================

DB_SERVER = ''
DB_USER = ''
DB_PASS = ''
DB_DB = ''

# ===================
# Logging
# ===================

# The logfiles
# general log level
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

# ===================
# processing settings
# ===================

MAX_ALLOWABLE_SMOOTH = (500, 2000)  # [m]
MIN_REQUIRED_SMOOTH = (100, 500)  # [m]
MAX_SMOOTH_CHANGE = 3  # [bins] todo: change into m

MAX_AVERAGE_TIME = 2 * 60 * 60  # 2h
MIN_AVERAGE_TIME = 30 * 60  # 30min

RANGE_BOUNDARY = 2000
# [m] different maximum allowable smoothing
# lengths below and above RANGE_BOUNDARY

RANGE_BOUNDARY_KM = RANGE_BOUNDARY / 1000.
