# -*- coding: utf-8 -*-

from logging import INFO, DEBUG

from ELDAmwl.registry import Registry

# ===================
# Directories
# ===================

LOG_PATH = ''
SIGNAL_PATH = ''
PRODUCT_PATH = ''
TEMP_PATH = ''


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
