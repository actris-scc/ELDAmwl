from ELDAmwl.database.tables.db_base import Base
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import FLOAT
from sqlalchemy import INTEGER
from sqlalchemy import String
from sqlalchemy import text


class VLDRMethod(Base):
    """content of the db table _vldr_methods

    """

    __tablename__ = '_vldr_methods'

    ID = Column(
        'id',
        INTEGER,
        primary_key=True,
        server_default=text("'0'"),
    )
    method = Column(
        String(100),
        nullable=False,
        server_default=text("''"),
    )


class VLDROption(Base):
    """content of the db table vldr_options

    """

    __tablename__ = 'vldr_options'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        server_default=text("'-1'"),
    )
    vldr_method_id = Column(
        '_vldr_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'"),
    )
    error_method_id = Column(
        '_error_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'-1'"),
    )
    smooth_method_id = Column(
        '_smooth_method_ID',
        INTEGER,
        nullable=False,
        index=True,
        server_default=text("'0'"),
    )


class PolarizationCalibrationCorrectionFactors(Base):
    """content of the db table polarization_calibration_correction_factors

    """

    __tablename__ = 'polarization_calibration_correction_factors'

    ID = Column(
        INTEGER,
        primary_key=True,
    )
    product_id = Column(
        '_product_ID',
        INTEGER,
        nullable=False,
        server_default=text("'-1'"),
    )
    wavelength = Column(
        FLOAT,
        nullable=False,
    )
    range_id = Column(
        '_range_ID',
        INTEGER,
        nullable=False,
        server_default=text("'-1'"),
    )
    correction_date = Column(
        DateTime,
        nullable=False,
    )
    correction_submission_date = Column(
        DateTime,
        nullable=False,
    )
    a_K = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    b_K = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    c_K = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    a_lowerbound = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    b_lowerbound = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    c_lowerbound = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    a_upperbound = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    b_upperbound = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
    c_upperbound = Column(
        FLOAT,
        nullable=False,
        server_default=text("'0.0'"),
    )
