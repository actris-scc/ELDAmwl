# -*- coding: utf-8 -*-
"""Classes for measurement related db tables"""

# structure geneated with
# (ELDAmwl) C:\Users\imattis>sqlacodegen mysql+pymysql://earlinet:dwdlidar@localhost/scc_dev_20190228  # noqa E501
# > k:\auswertung\Mattis\myPrograms\python\ELDAmwl\db_structure.txt
from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import VARCHAR


class Measurements(Base):
    __tablename__ = 'measurements'

    num_id = Column(
        INTEGER,
        primary_key=True,
    )
    ID = Column(
        VARCHAR(15),
        nullable=False,
    )
    hoi_stations_id = Column(
        '__hoi_stations__ID',
        CHAR(3),
        index=True,
    )
    hoi_system_id = Column(
        '_hoi_system_ID',
        INTEGER,
        nullable=False,
        index=True,
    )
    start = Column(
        DateTime,
    )
    stop = Column(
        DateTime,
        nullable=False,
    )
    comment = Column(
        String(100),
        nullable=False,
    )
    calipso = Column(
        INTEGER,
        nullable=False,
    )
    cirrus = Column(
        INTEGER,
        nullable=False,
    )
    etna = Column(
        INTEGER,
        nullable=False,
    )
    rurban = Column(
        INTEGER,
        nullable=False,
    )
    stratos = Column(
        INTEGER,
        nullable=False,
    )
    dicycles = Column(
        INTEGER,
        nullable=False,
    )
    photosmog = Column(
        INTEGER,
        nullable=False,
    )
    forfires = Column(
        INTEGER,
        nullable=False,
    )
    sahadust = Column(
        INTEGER,
        nullable=False,
    )
    climatol = Column(
        INTEGER,
        nullable=False,
    )
    upload = Column(
        INTEGER,
        nullable=False,
    )
    hirelpp = Column(
        INTEGER,
        nullable=False,
    )
    cloudmask = Column(
        INTEGER,
        nullable=False,
    )
    elquick = Column(
        INTEGER,
        nullable=False,
    )
    elpp = Column(
        INTEGER,
        nullable=False,
    )
    elda = Column(
        INTEGER,
        nullable=False,
    )
    eldec = Column(
        INTEGER,
        nullable=False,
    )
    elic = Column(
        INTEGER,
        nullable=False,
    )
    hirelpp_return_code = Column(
        INTEGER,
    )
    cloudmask_return_code = Column(
        INTEGER,
    )
    elquick_return_code = Column(
        INTEGER,
    )
    elpp_return_code = Column(
        INTEGER,
        index=True,
    )
    elda_return_code = Column(
        INTEGER,
    )
    eldec_return_code = Column(
        INTEGER,
    )
    elic_return_code = Column(
        INTEGER,
    )
    interface_return_code = Column(
        INTEGER,
        index=True,
    )
    elpp_current_product_id = Column(
        INTEGER,
    )
    eldec_current_product_id = Column(
        INTEGER,
    )
    hirelpp_current_product_id = Column(
        INTEGER,
    )
    cloudmask_current_product_id = Column(
        INTEGER,
    )
    elda_current_product_id = Column(
        INTEGER,
    )
    elic_current_product_id = Column(
        INTEGER,
    )
    elquick_current_product_id = Column(
        INTEGER,
    )
    creation_date = Column(
        DateTime,
    )
    updated_date = Column(
        DateTime,
    )
    sounding_file_id = Column(
        INTEGER,
        index=True,
    )
    lidar_ratio_file_id = Column(
        INTEGER,
        index=True,
    )
    overlap_file_id = Column(
        INTEGER,
        index=True,
    )
    creation_auth_user_ID = Column(
        INTEGER,
    )
    update_auth_user_ID = Column(
        INTEGER,
    )
