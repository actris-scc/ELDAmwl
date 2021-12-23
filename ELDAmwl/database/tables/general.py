"""SCC database table for logging and exit codes"""

from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column, VARCHAR, BIGINT
from sqlalchemy import DateTime
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text


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
    Stable with description of exit codes
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
