# -*- coding: utf-8 -*-
"""Classes for extinction related db tables"""

from sqlalchemy import CHAR
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import DECIMAL
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ExtMethod(Base):
    """content of the db table _ext_methods

    """

    __tablename__ = '_ext_methods'

    ID = Column(
        INTEGER,
        primary_key=True,
        server_default=text('0'),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    python_classname = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    python_classname_get_used_binres = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    python_classname_get_effective_binres = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )


class ExtinctionOption(Base):
    """content of the db table extinction_options

    """

    __tablename__ = 'extinction_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        server_default=text('-1'),
    )
    ext_method_id = Column(
        '_ext_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    error_method_id = Column(
        '_error_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    overlap_file_id = Column(
        '_overlap_file_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text('-1'),
    )
    angstroem = Column(
        DECIMAL(10, 4),
        nullable=False,
        server_default=text('0.0000'),
    )


class OverlapFile(Base):
    __tablename__ = 'overlap_files'

    ID = Column(
        INTEGER,
        primary_key=True,
    )

    # Rule is: If a column has two underscores reduce to one
    hoi_stations_id = Column(
        '__hoi_stations__ID',
        CHAR(3),
    )
    start = Column(
        DateTime,
    )
    stop = Column(
        DateTime,
    )
    filename = Column(
        String(100),
        nullable=False,
        server_default=text(''),
    )
    interpolation_id = Column(
        '_interpolation_id',
        INTEGER,
    )
    submission_date = Column(
        DateTime,
    )
    status = Column(
        String(20),
        nullable=False,
    )
