"""SCC log table"""

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ELDALogs(Base):
    """
    SCC log table
    """

    __tablename__ = 'elda_logs'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    meas_id = Column(
        '__measurements__ID',
        String(100),
        nullable=False,
        server_default=text(''),
    )
    product_id = Column(
        'product_ID',
        INTEGER,
        nullable=False,
        server_default=text('-1'),
    )
    level = Column(
        INTEGER,
        nullable=False,
        server_default=text('-1'),
    )
    module_version = Column(
        String(45),
        nullable=False,
        server_default=text(''),
    )
    datetime = Column(
        DateTime,
        nullable=False,
    )
    message = Column(
        String(400),
        nullable=False,
        server_default=text(''),
    )
