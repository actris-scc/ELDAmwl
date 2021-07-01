from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import BIGINT, CHAR, INTEGER, FLOAT, DateTime, String, VARCHAR
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class LidarConstants(Base):
    """content of the db table lidar_constants

    """

    __tablename__ = 'lidar_constants'

    ID = Column(BIGINT, primary_key=True)
    __measurements__ID = Column(VARCHAR(15), nullable=True)
    _product_ID = Column(INTEGER, nullable=False)
    _channel_ID = Column(INTEGER, nullable=False)
    _hoi_system_ID = Column(INTEGER, nullable=False)
    filename = Column(String(100), nullable=False)

    calibr_factor = Column(FLOAT, nullable=True)
    calibr_factor_sys_err = Column(FLOAT, nullable=True)
    calibr_factor_stat_err = Column(FLOAT, nullable=True)
    lidar_const = Column(FLOAT, nullable=True)
    lidar_const_sys_err = Column(FLOAT, nullable=True)
    lidar_const_stat_err = Column(FLOAT, nullable=True)

    detection_wavelength = Column(FLOAT, nullable=True)

    profile_start_time = Column(DateTime, nullable=False)
    profile_end_time = Column(DateTime, nullable=False)

    calibr_window_bottom = Column(FLOAT, nullable=True)
    calibr_window_top = Column(FLOAT, nullable=True)

    InscribedAt = Column(DateTime, nullable=False)

    ELDA_version = Column(CHAR(50), nullable=True)

    is_latest_value = Column(INTEGER, nullable=False)


