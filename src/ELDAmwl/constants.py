# -*- coding: utf-8 -*-

from datetime import datetime
from math import pi


ELDA_MWL_VERSION = '0.0.1'

LIGHT_SPEED = 3.E8  # m / s

T0 = datetime(1904, 1, 1)
RAYL_LR = 8. * pi / 3

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

PRODUCT_TYPES = [RBSC, EXT, LR, EBSC, MWL, AE, CR, VLDR, PLDR]
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
MC = 0
ASS = 1

ERROR_METHODS = [MC, ASS]

# ====== smooth methods ======
AUTO = 0
FIXED = 1

SMOOTH_METHODS = [AUTO, FIXED]

# ====== time and vertical resolutions ======
LOWRES = 0
HIGHRES = 1

RESOLUTIONS = [LOWRES, HIGHRES]
RESOLUTION_STR = ['lowres', 'highres']

# ====== elast bsc methods ======
KF = 0  # Klett-Fernald
IT = 1  # iterative

ELAST_BSC_METHODS = [KF, IT]

# ====== lidar ratio input methods ======
PROFILE = 0
FIXED = 1

LR_INPUT_METHODS = [PROFILE, FIXED]

# ====== Raman bsc methods ======
ANSM = 0  # Ansmann
BR = 1  # via backscatter ratio

RAMAN_BSC_METHODS = [ANSM, BR]

# ====== fill values ======
NC_FILL_BYTE = -127
NC_FILL_INT = -2147483647
NC_FILL_STR = ''

# ====== quality flags ======
ALL_OK = 0
NEG_DATA = 1
BELOW_OVL = 2
ABOVE_MAX_ALT = 4
HAS_CLOUD = 8
ABOVE_KLETT_REF = 16
INVALID_DEPOL = 32
BELOW_MIN_BSCR = 64
CALC_WINDOW_OUTSIDE_PROFILE = 124
