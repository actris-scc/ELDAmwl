"""
Generate a new Test DB from CSV sources
"""

import os
import csv
import datetime
import sqlite3

import sqlalchemy
from sqlalchemy import DateTime
from sqlalchemy.orm import sessionmaker

from ELDAmwl.configs.config_default import STRP_DATE_TIME_FORMAT
from ELDAmwl.database.db import DBUtils
from ELDAmwl.database.tables.extinction import ExtMethod, ExtinctionOption, OverlapFile
from ELDAmwl.database.tables.measurements import Measurements
from ELDAmwl.database.tables.system_product import SystemProduct, MWLproductProduct, Products, ProductTypes, \
    ProductOptions, ErrorThresholds, ErrorThresholdsLow, ErrorThresholdsHigh

from ELDAmwl.errors import CsvFileNotFound, FillTableFailed
from ELDAmwl.log import logger

# List of all DB tables in the test DB
ALL_DB_TABLES = [
    SystemProduct,
    OverlapFile,
    ProductTypes,
    ExtMethod,
    ExtinctionOption,
    Measurements,
    MWLproductProduct,
    Products,
    ProductOptions,
    ErrorThresholds,
]

# Where does the test-DB live
TEST_DB_PATH = os.path.split(__file__)[0]
# name of the test DB
TEST_DB_FILENAME = "testDB.sqlite"
# file path of the test DB
TEST_DB_FILEPATH = os.path.join(TEST_DB_PATH, TEST_DB_FILENAME)
# Connect string for the sqlite engine
TEST_CONNECT_STRING = "sqlite+pysqlite:///" + TEST_DB_FILEPATH
# directory of the csv source files
CSV_DATA_SOURCE = os.path.join(TEST_DB_PATH, 'csv_sources')



class DBConstructor(object):
    """
    Construct a test DB from CSV files
    """

    def __init__(self):
        self.remove_db()

        self.engine = DBUtils(TEST_CONNECT_STRING).engine
        self.session = sessionmaker(bind=self.engine)()

        self.create_tables()
        self.fill_tables()

    def remove_db(self):
        """Remove the prior DB"""
        os.remove(TEST_DB_FILEPATH)

    def create_tables(self):
        """
        Create all DB tables
        Returns:
            Nothing
        """
        for table in ALL_DB_TABLES:

            logger.info("Creating table %s" % table.__tablename__)
            table.metadata.create_all(self.engine)
            logger.info("Created table %s, sucessfully" % table.__tablename__ )

    def csv_data( self, table ):
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
        except FileNotFoundError as e:
            logger.warning("CSV file %s not found" % file_name)
            raise CsvFileNotFound
        result = csv.DictReader(csvfile, delimiter=',')

        # Correct for double underscores in column nomes wich confuse sqlalchemy
        new_field_names = []
        for fieldname in result.fieldnames:
            new_field_names.append(fieldname.replace('__','_'))

        result.fieldnames = new_field_names

        return result

    def fill_tables(self):
        """
        Fills all DB tables with content from the CSV files. If a CSV file is not found the table is skipped.
        Returns:
            None

        """
        for table in ALL_DB_TABLES:
            logger.info("Filling table %s" % table.__tablename__)

            try:
                data = self.csv_data(table)
            except CsvFileNotFound:
                continue

            try:
                self.fill_table( table, data)
            except FillTableFailed:
                continue


    def refine_data(self, table, data):
        """
        Bring the data in shape
        Returns:
            refined data
        """

        # Find target columns wich are datetimes
        cols_to_refine = []
        for column in table.__table__.columns:
            if column.type.__class__ == DateTime:
                cols_to_refine.append(column.name)

        # refine the data
        new_data = []
        for row in data:
            new_row= row
            # Replace string 'Null' with None in all columns
            for col in table.__table__.columns:
                try:
                    if row[col.name] == 'NULL':
                        new_row[col.name] = None
                except KeyError:
                    logger.error("Refine data failed. Target table %s does not have a column %s" % (table.__tablename__,col) )
                    raise FillTableFailed

            # Make DateTime objects for the expecting columns
            for col in cols_to_refine:
                if not row[col]:
                    continue
                if row[col] =='0000-00-00 00:00:00':
                    new_row[col] = None
                else:
                    new_row[col] = datetime.datetime.strptime(row[col], STRP_DATE_TIME_FORMAT)

            new_data.append(new_row)
        return new_data

    def fill_table(self,table, data):
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
            except sqlalchemy.exc.IntegrityError :
                self.session.rollback()
                logger.info("Found bad row for table %s" % table.__tablename__)
                logger.info("Row %s" % row)



db_constructor = DBConstructor()

