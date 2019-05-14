# -*- coding: utf-8 -*-

from logging import log, INFO, ERROR

from ELDAmwl.database.db import DBUtils
from ELDAmwl.log import create_logger

from ELDAmwl.registry import Registry
import ELDAmwl.factory


try:
    import configs.config as cfg
except ModuleNotFoundError:
    import configs.config_default as cfg

registry = Registry()

registry.update( cfg.registry.factory_registry )

registry.status()


meas_id = '20180515oh01'
create_logger(meas_id)

log(INFO,'hello world')


db_utils = DBUtils()

db_utils.read_tasks(meas_id)

log(INFO,'the end')
