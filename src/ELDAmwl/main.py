# -*- coding: utf-8 -*-
from ELDAmwl import log
from ELDAmwl.database.db import DBUtils
from ELDAmwl.log import create_logger


log.notice('hello world')

meas_id = '20180515oh01'
create_logger(meas_id)

db_utils = DBUtils()

db_utils.read_tasks(meas_id)
