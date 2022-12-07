"""SCC database table for logging and exit codes"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import BIGINT
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy import VARCHAR


class ELDAmwlLogs(Base):
    """
    SCC log table
    """

    __tablename__ = 'eldamwl_logs'

    ID = Column(
        BIGINT,
        primary_key=True,
    )
    measurements_id = Column(
        VARCHAR(15),
        nullable=False,
    )
    product_id = Column(
        INTEGER,
        nullable=True,
    )
    level = Column(
        INTEGER,
        nullable=False,
        server_default=text("'-1'"),
    )
    module_version = Column(
        String(45),
        nullable=False,
        server_default=text("''"),
    )
    datetime = Column(
        DateTime,
        nullable=False,
    )
    message = Column(
        String(400),
        nullable=False,
        server_default=text("''"),
    )


class ELDAmwlExitCodes(Base):
    """
    table with description of exit codes
    """

    __tablename__ = 'eldamwl_exitcodes'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    description = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )


class EldaMwlProductStatus(Base):
    """
    table with description of status of ELDAmwl products
    """

    __tablename__ = 'eldamwl_product_status'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    measurement_id = Column(
        '__measurements__ID',
        VARCHAR(15),
        nullable=False,
    )
    mwl_product_id = Column(
        '_mwl_product_id',
        INTEGER,
        nullable=True,
    )
    product_id = Column(
        '_product_id',
        INTEGER,
        nullable=True,
    )
    status_code = Column(
        INTEGER,
        nullable=True,
    )
    description = Column(
        String(500),
        server_default=text("''"),
    )
