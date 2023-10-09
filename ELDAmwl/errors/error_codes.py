# -*- coding: utf-8 -*-

# those error codes shall be transformed into exceptions, where applicable

NO_ERROR = 0

# ERROR_INI_FILE_NOT_EXISTS = 1
ERROR_LR_FILE_NOT_EXISTS = 2
ERROR_SIG_FILE_NOT_EXISTS = 3
ERROR_SG_FILE_NOT_EXISTS = 4
INVALID_MEASUREMENT_ID = 5
ERROR_LOG_DIR_NOT_EXISTS = 6
USE_CASE_NOT_IMPLEMENTED = 7
PRODUCT_NOT_IMPLEMENTED = 8
DB_ERROR = 9
NC_OPEN_ERROR = 10
CAL_RANGE_HIGHER_THAN_VALID = 11
# NO_LR_VAR = 'Cannot find variable Lidar_Ratio in lr file'
NO_VALID_POINTS_FOR_CAL = 13
CANNOT_CREATE_MERGED_SIG = 14
# DIFF_VERT_RES = 15
NOISE_OF_FR_TOO_LARGE_FOR_MERGE = 16
NO_PRODUCT_OPTIONS_IN_DB = 17
DIFF_SCAN_ANGLES = 18
MISSING_EXT_SUBPROFILE = 19
ITER_BSC_NOT_CONV = 20
ERR_NOT_ENOUGH_SG_COEFFICIENTS = 21
UNKNOWN_EXCEPTION = 22
# ERR_RUNTIME_EXCEPTION = 22
ERR_INVALID_NB_OF_MC_ITERATIONS = 23
ERR_NO_MC_OPTIONS_FOR_KLETT = 24
NO_STABLE_SOLUTION_FOR_KLETT = 25
MISSING_CHANNEL_ID_IN_NCFILE = 26
NEGATIVE_CALIBRATION_VALUE = 27
WRONG_ELPP_VERSION = 28
MULTIPLE_DEPOL_NOT_YET_IMPLEMENTED = 29
CANNOT_FIND_CORRECT_CHANNEL_IDX_IN_FILE = 30
ZERO_DETECTION_LIMIT = 31
WRONG_COMMAND_LINE_PARAM = 41
DIFFERENT_CLOUD_MASK_EXISTS = 42
DIFFERENT_HEADER_EXISTS = 43
DIFFERENT_BSC_OPTIONS_IN_MEASUREMENT = 44
NO_MC_OPTIONS_IN_DB = 45
NO_BSC_CAL_OPTIONS_IN_DB = 46
NO_OVL_FILE_IN_DB = 47
COULD_NOT_FIND_CALIBR_WINDOW = 48
DIFFERENT_WL_IN_EXT_AND_BSC_FOR_LR = 49
INTEGRATION_FAILED = 50
NOT_ENOUGH_MC_SAMPLES = 51
NO_PRODUCTS_GENERATED = 52
NEG_BSC_FOR_LIDAR_CONSTANT = 53
DIFFERENT_PRODS_RESOLUTION = 54
COULD_NOT_FIND_PRODS_RESOLUTION = 55
NO_PARAMS_FOR_DEPOL_UNCERTAINTY_IN_DB = 60
NO_BSC_FOR_LIDAR_CONSTANT = 61
NO_MWL_PRODUCT_DEFINED = 62
# ===============================================
# error codes which occur only during development
# ===============================================

# Raised if the requested data are not found in data storage
DATA_NOT_IN_STORAGE = 100
# Raised on attempt to add more than one override to class registry
CLASS_REGISTRY_TOO_MAY_OVERRIDES = 101
# Raised on attempt to normalize a signal by number of laser shots several times
REPEATED_ATTEMPT_TO_NORMALZE_BY_SHOTS = 102
# Raised on attempt to correct a signal for molecular transmission several times
REPEATED_ATTEMPT_TO_CORRECT_MOL_TRANSM = 103
