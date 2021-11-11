from ELDAmwl.config import register_config
from ELDAmwl.database.db_functions import register_db_func
from ELDAmwl.elda_mwl.elda_mwl import register_params
from ELDAmwl.log.log import register_logger, register_db_logger
from ELDAmwl.monte_carlo.operation import register_monte_carlo
from ELDAmwl.storage.data_storage import register_datastorage
from prefect import Task


class ELDASetupComponents(Task):

    def __init__(self):
        super(ELDASetupComponents, self).__init__()

    def run(self, env='Production'):
        # Get the configuration
        register_config(env=env)

        # Setup the logging facility for this measurement ID
        register_logger()
        # register_plugins()

        # Bring up the global db_access
        register_db_func()

        # Bring up DB logger
        register_db_logger()

        # Bring up the global data storage
        register_datastorage()

        # Bring up the global parameter instance
        register_params()

        # Register MonteCarlo Adapter
        register_monte_carlo()
