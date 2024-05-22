import os

from dynaconf import Dynaconf
from ELDAmwl.component.interface import ICfg
from ELDAmwl.errors.exceptions import ConfigFileNotFound
from ELDAmwl.utils.misc import current_environment
from ELDAmwl.utils.path_utils import abs_file_path
from os.path import exists
from pathlib import Path

import zope

def register_config(args):
    if args is not None:
        config_dir = Path(abs_file_path(args.config_dir))
    else:
        config_dir = Path(abs_file_path('.'))

    if not exists(config_dir / 'settings.yaml'):
        raise ConfigFileNotFound(config_dir / 'settings.yaml')

    if current_environment() == 'testing':
        settings_files = [config_dir / 'settings.yaml']
    else:
        if not exists(config_dir / '.secrets.yaml'):
            raise ConfigFileNotFound(config_dir / '.secrets.yaml')
        settings_files = [config_dir / 'settings.yaml', config_dir / '.secrets.yaml']

    cfg = Dynaconf(
        envvar_prefix='DYNACONF',  # replaced "DYNACONF" by 'DYNACONF'
        settings_files=settings_files,
        environments=True,
        env=current_environment(),
    )

    # `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
    # `settings_files` = Load these files in the order.

    zope.component.provideUtility(cfg, ICfg)
