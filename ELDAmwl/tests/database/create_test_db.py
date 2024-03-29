# -*- coding: utf-8 -*-
from ELDAmwl.component.interface import IDBConstructor
from ELDAmwl.component.interface import ILogger
from ELDAmwl.database.db import DBUtils
from ELDAmwl.database.tables.backscatter import BscCalibrLowestHeight
from ELDAmwl.database.tables.backscatter import BscCalibrMethod
from ELDAmwl.database.tables.backscatter import BscCalibrRangeSearchMethod
from ELDAmwl.database.tables.backscatter import BscCalibrUpperHeight
from ELDAmwl.database.tables.backscatter import BscCalibrValue
from ELDAmwl.database.tables.backscatter import BscCalibrWindow
from ELDAmwl.database.tables.backscatter import BscMethod
from ELDAmwl.database.tables.backscatter import ElastBackscatterOption
from ELDAmwl.database.tables.backscatter import ElastBscMethod
from ELDAmwl.database.tables.backscatter import IterBackscatterOption
from ELDAmwl.database.tables.backscatter import LRFile
from ELDAmwl.database.tables.backscatter import RamanBackscatterOption
from ELDAmwl.database.tables.backscatter import RamanBscMethod
from ELDAmwl.database.tables.channels import Channels
from ELDAmwl.database.tables.channels import ProductChannels
from ELDAmwl.database.tables.channels import Telescopes
from ELDAmwl.database.tables.depolarization import VLDROption, PolarizationCalibrationCorrectionFactors, VLDRMethod
from ELDAmwl.database.tables.eldamwl_class_names import EldamwlClassNames
from ELDAmwl.database.tables.eldamwl_products import EldamwlProducts
from ELDAmwl.database.tables.extinction import ExtinctionOption
from ELDAmwl.database.tables.extinction import ExtMethod
from ELDAmwl.database.tables.extinction import OverlapFile
from ELDAmwl.database.tables.general import ELDAmwlLogs, SccVersion
from ELDAmwl.database.tables.lidar_constants import LidarConstants
from ELDAmwl.database.tables.lidar_ratio import ExtBscOption
from ELDAmwl.database.tables.measurements import Measurements
from ELDAmwl.database.tables.system_product import ErrorThresholds
from ELDAmwl.database.tables.system_product import MCOption
from ELDAmwl.database.tables.system_product import MWLproductProduct
from ELDAmwl.database.tables.system_product import PreparedSignalFile
from ELDAmwl.database.tables.system_product import PreProcOptions
from ELDAmwl.database.tables.system_product import Products
from ELDAmwl.database.tables.system_product import ProductTypes
from ELDAmwl.database.tables.system_product import SmoothMethod
from ELDAmwl.database.tables.system_product import SmoothOptions
from ELDAmwl.database.tables.system_product import SmoothTypes
from ELDAmwl.database.tables.system_product import SystemProduct
from ELDAmwl.errors.exceptions import CsvFileNotFound
from ELDAmwl.errors.exceptions import FillTableFailed
from ELDAmwl.utils.constants import STRP_DATE_TIME_FORMAT
from sqlalchemy import DateTime
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from zope import component

import csv
import datetime
import os
import sqlalchemy
import zope


# List of all DB tables in the test DB
ALL_DB_TABLES = [
    BscCalibrMethod,
    BscCalibrLowestHeight,
    BscCalibrUpperHeight,
    BscCalibrWindow,
    BscCalibrValue,
    BscCalibrRangeSearchMethod,
    BscMethod,
    Channels,
    ElastBackscatterOption,
    ElastBscMethod,
    EldamwlClassNames,
    ELDAmwlLogs,
    EldamwlProducts,
    ErrorThresholds,
    ExtinctionOption,
    ExtBscOption,
    ExtMethod,
    IterBackscatterOption,
    LidarConstants,
    LRFile,
    MCOption,
    Measurements,
    MWLproductProduct,
    OverlapFile,
    PolarizationCalibrationCorrectionFactors,
    PreparedSignalFile,
    PreProcOptions,
    ProductChannels,
    Products,
    ProductTypes,
    RamanBackscatterOption,
    RamanBscMethod,
    SccVersion,
    SmoothMethod,
    SmoothOptions,
    SmoothTypes,
    SystemProduct,
    Telescopes,
    VLDROption,
    VLDRMethod,
]

# Where does the test-DB live
TEST_DB_PATH = os.path.split(__file__)[0]
# name of the test DB
TEST_DB_FILENAME = 'testDB.sqlite'
# file path of the test DB
TEST_DB_FILEPATH = os.path.join(TEST_DB_PATH, TEST_DB_FILENAME)
# Connect string for the sqlite engine
TEST_CONNECT_STRING = 'sqlite+pysqlite:///' + TEST_DB_FILEPATH
# directory of the csv source files
CSV_DATA_SOURCE = os.path.join(TEST_DB_PATH, 'csv_sources')


@zope.interface.implementer(IDBConstructor)
class DBConstructor(object):
    """
    Construct a test DB from CSV files
    """

    def __init__(self):
        self.logger = component.queryUtility(ILogger)
        self.engine = DBUtils(TEST_CONNECT_STRING).engine
        self.session = sessionmaker(bind=self.engine)()

    def run(self):
        self.remove_db()
        self.create_tables()
        self.fill_tables()

    def remove_db(self):
        """Remove the prior DB"""
        try:
            os.remove(TEST_DB_FILEPATH)
        except FileNotFoundError:
            pass

    def create_tables(self):
        """
        Create all DB tables
        Returns:
            Nothing
        """
        for table in ALL_DB_TABLES:

            self.logger.info('Creating table {0}'.format(table.__tablename__))
            table.metadata.create_all(self.engine)
            self.logger.info('Created table {0}, sucessfully'.format(table.__tablename__ ))  # noqa E501

    def csv_data(self, table):
        """
        Read the CSV file associated with the give table in a list of dicts.

        Args:
            table: the current table instance

        Returns:
            The parsed csv file as a list of dictionaries
        """
        file_name = os.path.join(CSV_DATA_SOURCE, table.__tablename__ + '.csv')
        try:
            csvfile = open(file_name)
        except FileNotFoundError:
            self.logger.warning('CSV file {0} not found'.format(file_name))
            raise CsvFileNotFound
        result = csv.DictReader(csvfile, delimiter=',')

        return result

    def fill_tables(self):
        """
        Fills all DB tables with content from the CSV files.
        If a CSV file is not found the table is skipped.
        Returns:
            None

        """
        for table in ALL_DB_TABLES:
            self.logger.info('Filling table {0}'.format(table.__tablename__))

            try:
                data = self.csv_data(table)
            except CsvFileNotFound:
                continue

            try:
                self.fill_table(table, data)
            except FillTableFailed:
                continue

    def refine_data(self, table, data):
        """
        Bring the data in shape
        Returns:
            refined data
        """

        # refine the data
        py_data = []
        for row in data:
            py_row = {}
            # Replace string 'Null' with None in all columns
            for col_py_name, col in inspect(table).c.items():
                col_db_name = col.expression.key
                try:
                    # Handle Columns that have the string 'NULL'
                    if row[col_db_name] == 'NULL':
                        py_row[col_py_name] = None
                    # Handle date time fields
                    elif col.type.__class__ == DateTime:
                        if not row[col_db_name]:
                            py_row[col_py_name] = None
                        elif row[col_db_name] == '0000-00-00 00:00:00' or row[col_db_name] == '-':   # noqa E501
                            py_row[col_py_name] = None
                        else:
                            py_row[col_py_name] = datetime.datetime.strptime(
                                row[col_db_name],
                                STRP_DATE_TIME_FORMAT,
                            )
                    else:
                        # All other cases
                        py_row[col_py_name] = row[col_db_name]
                except KeyError:
                    self.logger.error('Refine data failed. Target table {0} does not have a column {1}'.format(table.__tablename__, col))     # noqa E501
                    raise FillTableFailed

            py_data.append(py_row)
        return py_data

    def fill_table(self, table, data):
        """
        Fills a DB table with CSV content
        Args:
            table: The current table instance
            data: The CSV data as list of dicts

        Returns:
            Nothing
        """
        refined_data = self.refine_data(table, data)

        for row in refined_data:
            try:
                self.session.add(table(**row))
                self.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                self.session.rollback()
                self.logger.warning('Found bad row for table {0} Row {1}'.format(table.__tablename__, row))  # noqa E501
                raise e
            except Exception as e:
                self.logger.warning('Found Exception {0} bad row for table {1} Row {2}'.format(e, table.__tablename__, row))  # noqa E501
                raise e


def register_dbconstructor():
    db_constructor = DBConstructor()
    component.provideUtility(db_constructor, IDBConstructor)
