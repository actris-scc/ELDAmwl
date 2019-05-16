from sqlalchemy import Boolean, Index, INTEGER, CHAR, DateTime, Table, text, VARCHAR
from sqlalchemy import Column
#from sqlalchemy import Float
#from sqlalchemy import ForeignKey
#from sqlalchemy import Integer
from sqlalchemy import String
#from sqlalchemy.dialects.mssql import TINYINT
#from sqlalchemy.dialects.postgresql import INT4RANGE
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.testing.suite.test_reflection import metadata

Base = declarative_base()

# structure geneated with
# (ELDAmwl) C:\Users\imattis>sqlacodegen mysql+pymysql://earlinet:dwdlidar@localho
# st/scc_dev_20190228 > k:\auswertung\Mattis\myPrograms\python\ELDAmwl\db_structur
# e.txt

# Measurements = Table(
#     'measurements', metadata,
#     Column('ID', String(15), index=True),
#     Column('__hoi_stations__ID', CHAR(3), index=True),
#     Column('_hoi_system_ID', INTEGER(11), nullable=False, index=True, server_default=text("'0'")),
#     Column('start', DateTime),
#     Column('stop', DateTime, nullable=False, server_default=text("'1970-01-01 00:00:00'")),
#     Column('comment', String(100), nullable=False, server_default=text("''")),
#     Column('calipso', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('cirrus', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('etna', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('rurban', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('stratos', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('dicycles', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('photosmog', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('forfires', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('sahadust', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('climatol', TINYINT(1), nullable=False, server_default=text("'0'")),
#     Column('upload', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('hirelpp', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('cloudmask', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('elquick', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('elpp', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('elda', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('eldec', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('elic', INTEGER(11), nullable=False, server_default=text("'0'")),
#     Column('hirelpp_return_code', INTEGER(11)),
#     Column('cloudmask_return_code', INTEGER(11)),
#     Column('elquick_return_code', INTEGER(11)),
#     Column('elpp_return_code', INTEGER(11), index=True),
#     Column('elda_return_code', INTEGER(11)),
#     Column('eldec_return_code', INTEGER(11)),
#     Column('elic_return_code', INTEGER(11)),
#     Column('interface_return_code', INTEGER(11), index=True),
#     Column('elpp_current_product_id', INTEGER(11)),
#     Column('eldec_current_product_id', INTEGER(11)),
#     Column('hirelpp_current_product_id', INTEGER(11)),
#     Column('cloudmask_current_product_id', INTEGER(11)),
#     Column('elda_current_product_id', INTEGER(11)),
#     Column('elic_current_product_id', INTEGER(11)),
#     Column('elquick_current_product_id', INTEGER(11)),
#     Column('creation_date', DateTime),
#     Column('updated_date', DateTime),
#     Column('sounding_file_id', INTEGER(11), index=True),
#     Column('lidar_ratio_file_id', INTEGER(11), index=True),
#     Column('overlap_file_id', INTEGER(11), index=True),
#     Column('creation_auth_user_ID', INTEGER(11)),
#     Column('update_auth_user_ID', INTEGER(11))
# )

class Measurements(Base):
    __tablename__ = '_measurements'

    ID = Column(INTEGER, primary_key=True)
    meas_id = Column(VARCHAR(15), nullable=False)
    _hoi_stations_ID = Column('__hoi_stations__ID', CHAR(3), index=True)
    _hoi_system_ID = Column(INTEGER, nullable=False, index=True)
    start = Column(DateTime)
    stop = Column(DateTime, nullable=False)
    comment = Column(String(100), nullable=False)
    calipso = Column(INTEGER, nullable=False)
    cirrus= Column(INTEGER, nullable=False)
    etna = Column(INTEGER, nullable=False)
    rurban = Column(INTEGER, nullable=False)
    stratos = Column(INTEGER, nullable=False)
    dicycles = Column(INTEGER, nullable=False)
    photosmog = Column(INTEGER, nullable=False)
    forfires = Column(INTEGER, nullable=False)
    sahadust = Column(INTEGER, nullable=False)
    climatol = Column(INTEGER, nullable=False)
    upload = Column(INTEGER, nullable=False)
    hirelpp = Column(INTEGER, nullable=False)
    cloudmask = Column(INTEGER, nullable=False)
    elquick = Column(INTEGER, nullable=False)
    elpp = Column(INTEGER, nullable=False)
    elda = Column(INTEGER, nullable=False)
    eldec = Column(INTEGER, nullable=False)
    elic = Column(INTEGER, nullable=False)
    hirelpp_return_code = Column(INTEGER)
    cloudmask_return_code = Column(INTEGER)
    elquick_return_code = Column(INTEGER)
    elpp_return_code = Column(INTEGER, index=True)
    elda_return_code = Column(INTEGER)
    eldec_return_code = Column(INTEGER)
    elic_return_code = Column(INTEGER)
    interface_return_code = Column(INTEGER, index=True)
    elpp_current_product_id = Column(INTEGER)
    eldec_current_product_id = Column(INTEGER)
    hirelpp_current_product_id = Column(INTEGER)
    cloudmask_current_product_id = Column(INTEGER)
    elda_current_product_id = Column(INTEGER)
    elic_current_product_id = Column(INTEGER)
    elquick_current_product_id = Column(INTEGER)
    creation_date = Column(DateTime)
    updated_date = Column(DateTime)
    sounding_file_id = Column(INTEGER, index=True)
    lidar_ratio_file_id = Column(INTEGER, index=True)
    overlap_file_id = Column(INTEGER, index=True)
    creation_auth_user_ID = Column(INTEGER)
    update_auth_user_ID = Column(INTEGER)
