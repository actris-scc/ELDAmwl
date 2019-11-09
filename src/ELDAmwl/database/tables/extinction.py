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

    ID = Column(INTEGER,
                primary_key=True,
                server_default=text("'0'"))
    method = Column(String(100),
                    nullable=False,
                    server_default=text("''"))
    python_classname = Column(String(100),
                              nullable=False,
                              server_default=text("''"))


class ExtinctionOption(Base):
    """content of the db table extinction_options

    """

    __tablename__ = 'extinction_options'

    ID = Column(INTEGER, primary_key=True)
    _product_ID = Column(INTEGER,
                         nullable=False,
                         server_default=text("'-1'"))
    _ext_method_ID = Column(INTEGER,
                            nullable=False,
                            index=True,
                            server_default=text("'-1'"))
    _error_method_ID = Column(INTEGER,
                              nullable=False,
                              index=True,
                              server_default=text("'-1'"))
    _overlap_file_ID = Column(INTEGER,
                              nullable=False,
                              index=True,
                              server_default=text("'-1'"))
    angstroem = Column(DECIMAL(10, 4),
                       nullable=False,
                       server_default=text("'0.0000'"))


class OverlapFile(Base):
    __tablename__ = 'overlap_files'

    ID = Column(INTEGER, primary_key=True)
    # Rule is: If a column has two underscores reduce to one
    _hoi_stations_ID = Column('__hoi_stations__ID', CHAR(3))
    start = Column(DateTime)
    stop = Column(DateTime)
    filename = Column(String(100), nullable=False, server_default=text("''"))
    _interpolation_id = Column(INTEGER)
    submission_date = Column(DateTime)
    status = Column(String(20), nullable=False)
