from sqlalchemy import Column
from sqlalchemy import BIGINT, CHAR, INTEGER, FLOAT, DateTime, String, VARCHAR
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class LidarConstants(Base):
    """content of the db table lidar_constants

    """

    __tablename__ = 'lidar_constants'

    ID = Column(
        BIGINT,
        primary_key=True
    )
    # Rule is: If a column has two underscores reduce to one
    measurements_id = Column(
        '__measurements__ID',
        VARCHAR(15),
        nullable=True
    )
    product_id = Column(
        "_product_ID",
        INTEGER,
        nullable=False
    )
    channel_id = Column(
        "_channel_ID",
        INTEGER,
        nullable=False
    )
    hoi_system_id = Column(
        "_hoi_system_ID",
        INTEGER,
        nullable=False
    )
    filename = Column(
        String(100),
        nullable=False
    )
    calibr_factor = Column(
        FLOAT,
        nullable=True
    )
    calibr_factor_sys_err = Column(
        FLOAT,
        nullable=True
    )
    calibr_factor_stat_err = Column(
        FLOAT,
        nullable=True
    )
    lidar_const = Column(
        FLOAT,
        nullable=True
    )
    lidar_const_sys_err = Column(
        FLOAT,
        nullable=True
    )
    lidar_const_stat_err = Column(
        FLOAT,
        nullable=True
    )
    detection_wavelength = Column(
        FLOAT,
        nullable=True
    )
    profile_start_time = Column(
        DateTime,
        nullable=False
    )
    profile_end_time = Column(
        DateTime,
        nullable=False
    )
    calibr_window_bottom = Column(
        FLOAT,
        nullable=True
    )
    calibr_window_top = Column(
        FLOAT,
        nullable=True
    )
    InscribedAt = Column(
        DateTime,
        nullable=False
    )
    ELDA_version = Column(
        CHAR(50),
        nullable=True
    )
    is_latest_value = Column(
        INTEGER,
        nullable=False
    )


"""
how this table is used:

from ELDAmwl.database.tables.lidar_constants import LidarConstants
from sqlalchemy import create_engine
try:
    import ELDAmwl.configs.config as cfg
except ImportError:
    import ELDAmwl.configs.config_default as cfg

connect_str = 'mysql+pymysql://{user}:{passw}@{host}/{db}'.format(
            user=cfg.DB_USER,
            passw=cfg.DB_PASS,
            host=cfg.DB_SERVER,
            db=cfg.DB_DB)
engine = create_engine(connect_str)

conn = engine.connect()

res = conn.execute('select * from (SELECT __measurements__ID,
_product_ID, _hoi_system_ID, _channel_ID, profile_start_time, profile_end_time,
count(*)  as count FROM lidar_constants WHERE is_latest_value=1
group by  __measurements__ID, _product_ID, _hoi_system_ID,
_channel_ID, profile_start_time, profile_end_time) as selectcount where selectcount.count >1
order by __measurements__ID;')
duplicates = res.fetchall()

del_ids = []
for row in duplicates:
    statement=('select id, InscribedAt from lidar_constants '
                 'where __measurements__ID = "{}" and '
                 '_product_ID = {} and '
                 '_hoi_system_ID={} and '
                 '_channel_ID={} and '
                 'profile_start_time = "{}" and '
                 'profile_end_time = "{}" and '
                 'is_latest_value = 1 order by InscribedAt desc;').format(row[0],
                                                                          row[1],
                                                                          row[2],
                                                                          row[3],
                                                                          row[4],
                                                                          row[5])
    #print(statement)
    res = conn.execute(statement)
    for line in res.fetchall()[1:]:
        #print(row[0],line)
        del_ids.append(line[0])

outfile = open('d:/temp/delete_ids.txt', 'w')
for id in del_ids:
    outfile.write('{} '.format(id))

outfile.close()


"""
