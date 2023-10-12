# -*- coding: utf-8 -*-

from datetime import datetime
from math import pi


ELDA_MWL_VERSION = '0.0.3'

LIGHT_SPEED = 3.E8  # m / s

T0 = datetime(1904, 1, 1)
RAYL_LR = 8. * pi / 3

# maximum volume linear depolarization ratio that is allowed for depol calibration measurements.
# this value is used to calculate the K parameter.
MAX_CALIBR_DPEOL = 0.015

# ====== product types ======
RBSC = 0
EXT = 1
LR = 2
EBSC = 3
MWL = 12
AE = 13
CR = 14
VLDR = 15
PLDR = 16
BSCR = 17

PRODUCT_TYPES = [RBSC, EXT, LR, EBSC, MWL, AE, CR, VLDR, PLDR, BSCR]
PRODUCT_TYPE_NAME = {RBSC: 'raman_backscatter',
                     EXT: 'extinction',
                     LR: 'lidar_ratio',
                     EBSC: 'elastic_backscatter',
                     MWL: 'multi_wavelength_product',
                     AE: 'angstroem_exponent',
                     CR: 'color_ratio',
                     VLDR: 'vldr',
                     PLDR: 'pldr',
                     BSCR: 'basc_ratio',
}

BASIC_PRODUCT_TYPES = [RBSC, EXT, EBSC, VLDR]

# todo: put info on USE_CASES in db tables
COMBINE_DEPOL_USE_CASES = {RBSC: [7, 9, 10, 11, 12, 18, 17],
                           EBSC: [3, 4, 7, 8]}

MERGE_PRODUCT_USE_CASES = {EXT: [2, 4, 5],
                           RBSC: [2, 4, 6, 12, 13, 14, 15, 16, 19],
                           EBSC: [2, 5, 6, 9]}

# ====== signal detection types ======
ANALOG = 1
PH_CNT = 2
GLUED = ANALOG + PH_CNT

DETECTION_TYPES = [ANALOG, PH_CNT, GLUED]

# ====== signal altitude ranges ======
ALL_RANGE = 0
ULTRA_NEAR_RANGE = 1
NEAR_RANGE = 2
FAR_RANGE = 4

SIGNAL_ALTITUDE_RANGES = [ULTRA_NEAR_RANGE, NEAR_RANGE, FAR_RANGE]

# ====== signal scatterer type ======
PARTICLE = 1
NITROGEN = 2
OXYGEN = 4
WATER_VAPOR = 8

SIGNAL_SCATTERER_TPYES = [PARTICLE, NITROGEN, OXYGEN, WATER_VAPOR]

# ====== polarization configuration ======
PARALLEL = 1
CROSS = 2
TOTAL = PARALLEL + CROSS
P45 = 4
M45 = 8

POL_CONFIGS = [PARALLEL, CROSS, TOTAL, P45, M45]

# ====== polarization channel geometries ======
TRANSMITTED = 1
REFLECTED = 2

CHANNEL_GEOMETRIES = [TRANSMITTED, REFLECTED]

# ====== error calculation methods ======
# todo: write method ids in db and read from there
MC = 0
ASS = 1

ERROR_METHODS = [MC, ASS]

# ====== smooth types ======
# todo: write method ids in db and read from there
AUTO = 0
FIXED = 1

SMOOTH_TYPES = [AUTO, FIXED]

# ====== time and vertical resolutions ======
LOWRES = 0
HIGHRES = 1

RESOLUTIONS = [LOWRES, HIGHRES]
RESOLUTION_STR = ['lowres', 'highres']

# ====== bsc methods ======
# todo: write method ids in db and read from there
RAMAN = 0  # Raman
ELAST = 1  # elastic

BSC_METHODS = [RAMAN, ELAST]

# ====== elast bsc algorithms ======
# todo: write method ids in db and read from there
KF = 0  # Klett-Fernald
IT = 1  # iterative

ELAST_BSC_ALGORITHMS = [KF, IT]

# ====== lidar ratio input methods ======
PROFILE = 0
FIXED = 1

LR_INPUT_METHODS = [PROFILE, FIXED]

# ====== Raman bsc algorithms ======
# todo: write method ids in db and read from there
ANSM = 0  # Ansmann
BR = 1  # via backscatter ratio

RAMAN_BSC_ALGORITHMS = [ANSM, BR]

# ====== VLDR algorithms ======
# todo: write method ids in db and read from there
VF22 = 0  # V Freudenthaler 2022

VLDR_ALGORITHMS = [VF22]

# ====== fill values ======
NC_FILL_BYTE = -127
NC_FILL_INT = -2147483647
NC_FILL_STR = ''

MWL_PROD_ID_DEFAULT = 0

# ====== quality flags of data points ======
ALL_OK = 0
NEG_DATA = 1
BELOW_OVL = 2
ABOVE_MAX_ALT = 4
# HAS_CLOUD = 8
ABOVE_KLETT_REF = 16
# INVALID_DEPOL = 32
VALUE_OUTSIDE_VALID_RANGE = 32
BELOW_MIN_BSCR = 64
CALC_WINDOW_OUTSIDE_PROFILE = 128
UNCERTAINTY_TOO_LARGE = 256
SINGLE_POINT = 1024

# ====== quality flags of complete profiles ======
P_ALL_OK = 0
P_NEG_DATA = 1
P_TOO_LARGE_INTEGRAL = 2
P_EMPTY = 4
P_VALUE_OUTSIDE_VALID_RANGE = 32

# ===================
# Time strings
# ===================

STRP_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# ===================
# processing settings
# ===================

# [m] different maximum allowable smoothing
# lengths below and above RANGE_BOUNDARY
MAX_ALLOWABLE_SMOOTH = (500, 2000)  # [m]
MIN_REQUIRED_SMOOTH = (100, 500)  # [m]
MAX_SMOOTH_CHANGE = 3  # [bins] todo: change into m
MAX_AVERAGE_TIME = 2 * 60 * 60  # 2h
MIN_AVERAGE_TIME = 30 * 60  # 30min
RANGE_BOUNDARY = 2000
RANGE_BOUNDARY_KM = RANGE_BOUNDARY / 1000.

# =========================================
# settings for retrieval of lidar constants
# =========================================
ANGSTROEM_DEFAULT = 1.6
MOL_ANGSTROEM_DEFAULT = 4
ASSUMED_LR_DEFAULT = 50
ASSUMED_LR_ERROR_DEFAULT = 10
LOWEST_HEIGHT_RANGE = 100  # [m]
OVL_FACTOR = 1.0
OVL_FACTOR_ERR = 0.2

# =========================================
# settings for MC error retrievals
# =========================================
# how many samples shall be tried for MC error retrievals (factor)
MC_TRIALS_FACTOR = 2

# =========================================
# settings for quality control
# =========================================
# number of standard deviations used in testing for negative values
# if (value + NEG_TEST_STD_FACTOR * err) < 0 => value is negative
NEG_TEST_STD_FACTOR = 2

# =========================================
# EXIT_CODES
# =========================================
EXIT_CODE_OK = 0
EXIT_CODE_SOME = 1
EXIT_CODE_NONE = 2
