# -*- coding: utf-8 -*-
"""example Classes for db tables by Volker"""

from attrdict import AttrDict
from copy import copy
from eprofile.database.engine_pid_guard import add_engine_pidguard
from eprofile.database.tables.privileged_ip import PrivilegedIP
from eprofile.database.tables.station import Station
from eprofile.database.tables.windprofiler import COLS_INCOMING_Windprofiler
from eprofile.database.tables.windprofiler import Windprofiler
from eprofile.database.tables.windprofiler_comb_dayfiles import WindprofilerCombDaily  # noqa E501
from eprofile.database.tables.windprofiler_daily import COLS_WindprofilerDaily
from eprofile.database.tables.windprofiler_mode import WindprofilerMode
from eprofile.database.tables.windprofiler_ql import WindprofilerQL
from eprofile.log import logger
from psycopg2._range import NumericRange
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import psycopg2
from sqlalchemy.orm import sessionmaker

import os


class DBFunc(object):
    def __init__(self, cfg, instrument_table=None, daily_table=None):
        self.cfg = cfg
        self.init_engine()
        self.daily_table = daily_table
        self.instrument_table = instrument_table

    def connect_string(self):
        result = 'postgres://{0}:{1}@{2}/{3}'.format(
            self.cfg.DB_USER, self.cfg.DB_PASS, self.cfg.DB_SERVER,
            self.cfg.DB_DB)
        return result

    def init_engine(self):
        self.engine = create_engine(self.connect_string(),
                                    connect_args={'sslmode': 'disable'})

        # Added parallel forking guard
        add_engine_pidguard(self.engine)
        # create a configured "Session" class
        self.session = sessionmaker(bind=self.engine)()

    # Quicklooks
    # ==========

    def insert_QL(self, data):
        ql = WindprofilerQL(**data)
        self.session.add(ql)
        self.session.commit()
        return ql

    def get_quicklooks(self, where, limit=None):
        day_files_without_quicklooks = self.session.query(
            self.daily_table.measurement_date,
            self.daily_table.day_file_name,
            self.instrument_table.wigos).filter_by(**where).join(
            self.instrument_table).order_by(
            self.daily_table.longitude.desc(),
            self.daily_table.latitude.desc())
        if limit:
            day_files_without_quicklooks = day_files_without_quicklooks.limit(
                limit)
        metadata = []
        for day_file in day_files_without_quicklooks:
            metadata.append({
                'measurement_date': day_file[0],
                'day_file_path': os.path.join(self.cfg.DAY_FILES_FOLDER,
                                              day_file[1]),
                'wigos': day_file[2],
            })
        return metadata

    def get_windprofiler_ql_to_be_processed(self, ql_mode, limit=None):
        query = self.session.query(self.instrument_table,
                                   self.daily_table.measurement_date) \
            .join(WindprofilerMode,
                  WindprofilerMode.windprofiler_id == self.instrument_table.id) \
            .join(self.daily_table,
                  self.daily_table.windprofiler_mode_id == WindprofilerMode.id) \
            .filter(self.daily_table.quicklook_state == ql_mode)
        if limit:
            query = query.limit(limit)
        return query

    def get_windprofiler_ql_to_be_processed_as_dict(self, ql_mode, limit=None):
        query_result = self.get_windprofiler_ql_to_be_processed(ql_mode,
                                                                limit).all()

        for instrument, date in query_result:
            result_dict = AttrDict()
            for field in COLS_INCOMING_Windprofiler:
                result_dict[field] = copy(getattr(instrument, field))
            yield result_dict, date

    def lookup_quicklooks(self, where, instrument_where, zoom=None):
        if instrument_where:
            day_files = self.session.query(self.daily_table,
                                           self.instrument_table,
                                           Station,
                                           ).filter_by(**where).join(
                self.instrument_table,
                self.daily_table.instrument_id == self.instrument_table.id,
            ).filter_by(**instrument_where)
        else:
            day_files = self.session.query(self.daily_table,
                                           self.instrument_table,
                                           Station).filter_by(**where).join(
                self.instrument_table,
                self.daily_table.instrument_id ==
                                               self.instrument_table.id).join(
                Station,
                self.instrument_table.station_id == Station.id)
        if zoom is not None:
            day_files = day_files.filter(
                self.instrument_table.zoom_range.contains(int(zoom)))

        day_files.join(Station, self.daily_table.station_id == Station.id)

        return day_files.order_by(self.daily_table.longitude.desc(),
                                  self.daily_table.latitude.desc())

    def lookup_windprofiler_ql(self, filter_instrument, measurement_date,
                               zoom=None):
        result = self.session.query(WindprofilerQL, Windprofiler, Station) \
            .filter_by(**filter_instrument) \
            .filter(WindprofilerQL.measurement_date == measurement_date) \
            .join(Windprofiler,
                  Windprofiler.id == WindprofilerQL.windprofiler_id) \
            .join(Station, Windprofiler.station_id == Station.id)

        if zoom is not None:
            result = result.filter(
                Windprofiler.zoom_range.contains(int(zoom)))

        return result

    # Low High
    # ========

    def get_low_high_modes(self, instrument_id):
        instrument_modes = self.session.query(WindprofilerMode) \
            .join(self.instrument_table,
                  self.instrument_table.id ==
                  WindprofilerMode.windprofiler_id) \
            .filter(self.instrument_table.id == instrument_id).all()
        return instrument_modes

    def get_low_high_dayfiles(self, instrument_id, date):
        day_files = self.session.query(
            self.daily_table, WindprofilerMode) \
            .join(WindprofilerMode,
                  WindprofilerMode.id ==
                  self.daily_table.windprofiler_mode_id) \
            .join(self.instrument_table,
                  self.instrument_table.id ==
                  WindprofilerMode.windprofiler_id) \
            .filter(self.daily_table.measurement_date == date) \
            .filter(self.instrument_table.id == instrument_id).all()
        return day_files

    def lookup_mode(self, mode_id):
        mode = self.session.query(WindprofilerMode).filter(
            WindprofilerMode.id == mode_id).all()
        return mode

    # Instruments
    # ====================
    def get_ceilometer(self, wigos):
        result = self.session.query(self.instrument_table).filter(
            self.instrument_table.wigos == wigos).all()
        # this is save due to the unique constraint on
        # self.instrument_table.wigos
        if result:
            return result[0]
        return result

    def get_windprofiler_mode(self, wigos, instrument_id):

        result = self.session.query(WindprofilerMode, Station,
                                    self.instrument_table) \
            .filter(WindprofilerMode.wigos == wigos) \
            .filter(WindprofilerMode.name == instrument_id) \
            .join(self.instrument_table,
                  self.instrument_table.id ==
                  WindprofilerMode.windprofiler_id) \
            .join(Station) \
            .all()
        if result:
            return result[0]
        return result

    def lookup_instruments_and_stations(self, where, zoom=None):
        data = self.session.query(self.instrument_table, Station).join(
            Station).filter_by(**where)
        if zoom is not None:
            data = data.filter(
                self.instrument_table.zoom_range.contains(int(zoom)))

        return data.order_by(Station.longitude.desc(), Station.latitude.desc())

    def lookup_instrument_and_station(self, instrument_id):
        data = self.session.query(self.instrument_table, Station) \
            .join(Station) \
            .filter(self.instrument_table.id == instrument_id)
        return data.all()

    def update_instruments(self, instruments, data):
        if 'zoom_range' in data:
            zoom = data['zoom_range']
            data['zoom_range'] = NumericRange(zoom[0], zoom[1])
        for wmo in instruments:
            filter_data = {
                'wigos': wmo,
            }
            query = self.session.query(self.instrument_table).filter_by(
                **filter_data)
            query.update(data)
            self.session.commit()

    # Stations
    # ============================

    def get_station(self, wigos):
        result = self.session.query(Station).filter(
            Station.wigos == wigos).all()
        # this is save due to the unique constraint on Station.station_wigos
        if result:
            return result[0]
        return result

    def lookup_stations(self, where, zoom_range=None, privileged=False):

        stations = self.session.query(Station).filter_by(**where).join(
            self.instrument_table)

        if zoom_range is not None:
            stations = stations.filter(
                self.instrument_table.zoom_range.contains(int(zoom_range)))

        if privileged is False:
            stations = stations.filter_by(ip_filter=privileged)

        return stations.order_by(Station.longitude.desc(),
                                 Station.latitude.desc())

    def lookup_instruments(self, where, zoom_range=None):
        if zoom_range is None:
            result = self.session.query(self.instrument_table).filter_by(
                **where)
        else:
            result = self.session.query(self.instrument_table).filter_by(
                **where).filter(
                self.instrument_table.zoom_range.contains(int(zoom_range)))
        return result

    # Dayfiles
    # ====================

    def lookup_dayfiles(self, where, instrument_where=None, zoom=None):
        if instrument_where:
            day_files = self.session.query(self.daily_table).filter_by(
                **where).join(self.instrument_table).filter_by(
                **instrument_where)
        else:
            day_files = self.session.query(self.daily_table).filter_by(**where)
        if zoom is not None:
            day_files = day_files.filter(
                self.instrument_table.zoom_range.contains(int(zoom)))

        return day_files

    def select_ceilometer_date(self, instrument_id, measurement_date):
        result = self.session.query(self.daily_table) \
            .filter_by(**{'instrument_id': instrument_id,
                          'measurement_date': measurement_date})
        return result

    def insert_day(self, data):
        day = self.daily_table(**data)
        self.session.add(day)
        self.session.commit()
        return day

    def select_date_ceilometer(self, measurement_date, wigos):
        result = self.session.query(self.daily_table) \
            .filter(
            self.daily_table.measurement_date == measurement_date).join(
            self.instrument_table) \
            .filter(self.instrument_table.wigos == wigos)
        return result

    def select_date_wigos_windprofiler(self, measurement_date, wigos,
                                       instrument_name):
        result = self.session.query(self.daily_table) \
            .filter(
            self.daily_table.measurement_date == measurement_date).join(
            WindprofilerMode) \
            .filter(WindprofilerMode.wigos == wigos) \
            .filter(WindprofilerMode.name == instrument_name)
        return result

    def get_dayfile_for_windprofiler_mode_and_date_as_dict(self,
                                                           measurement_date,
                                                           windprofiler_mode_id):  # noqa E501
        result = self.session.query(self.daily_table) \
            .filter(self.daily_table.measurement_date == measurement_date) \
            .filter(
            self.daily_table.windprofiler_mode_id ==
            windprofiler_mode_id).all()
        if len(result) != 1:
            return None
        result_dict = AttrDict()
        for field in COLS_WindprofilerDaily:
            result_dict[field] = copy(getattr(result[0], field))

        return result_dict

    # Combined Dayfiles
    # ===========================

    def lookup_comb_dayfile(self, date):
        res = self.session.query(WindprofilerCombDaily).filter(
            WindprofilerCombDaily.measurement_date == date).all()
        return res

    def insert_comb_dayfile(self, date, file):
        res = self.lookup_comb_dayfile(date)
        if res:
            return
        cd = WindprofilerCombDaily(day_file_name=file, measurement_date=date)
        self.session.add(cd)
        self.session.commit()
        return cd

    # Provileged IP
    # ==============================
    def lookup_privileged_ips(self):
        result = self.session.query(PrivilegedIP)
        return result

    # Metadata
    # ==============================

    def metadata_stations(self, params=None):

        return self.session.query(Station)

    # Obsolete
    # ======================================

    def migrate(self, source, target):
        logger.info('Migrating WMO stations to WIGOS')

        source_connection = psycopg2.connect(source)
        source_cur = source_connection.cursor()

        target_engine = create_engine(target,
                                      connect_args={'sslmode': 'disable'})
        target_session = sessionmaker(bind=target_engine)()

        source_cur.execute("""SELECT * from station""")

        for line in source_cur.fetchall():
            data = {
                'id': line[0],
                'station_wmo': line[1],
                'station_name': line[2],
                'latitude': line[3],
                'longitude': line[4],
                'altitude': line[5],
                'nws': line[6],
                'station_wigos': '0-20000-0-' + line[1],
            }
            station = Station(**data)
            target_session.add(station)
            target_session.commit()

#         logger.info("Migrated WMO station to WIGOS, successfully")
#         logger.info("Migrating WMO instruments to WIGOS")

        source_cur.execute("""SELECT * from ceilometer""")

        for line in source_cur.fetchall():
            data = {
                'id': line[0],
                'station_id': line[1],
                'wmo': line[2],
                'type': line[3],
                'file_length': line[4],
                'status': line[5],
                'calibrated': line[6],
                'reference': line[7],
                'wavelength': line[8],
                'manager': line[9],
                'operator': line[10],
                'moving': line[11],
                'ip_filter': line[12],
                'zoom_range': line[13],
                'wigos': '0-20000-0-' + line[2],
            }

            ceilometer = self.instrument_table(**data)
            target_session.add(ceilometer)
            target_session.commit()
        logger.info('Migrated WMO instruments to WIGOS, successfully')
