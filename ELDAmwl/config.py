from os.path import exists
from pathlib import Path

from dynaconf import Dynaconf
from ELDAmwl.component.interface import ICfg

import zope

from ELDAmwl.errors.exceptions import ConfigFileNotFound
from ELDAmwl.utils.path_utils import abs_file_path


def register_config(args, env=None):
    if args is not None:
        config_dir = Path(abs_file_path(args.config_dir))
    else:
        config_dir = Path(abs_file_path('.'))

    if not exists(config_dir/'settings.yaml') :
        raise ConfigFileNotFound(config_dir/'settings.yaml')
    if not exists(config_dir / '.secrets.yaml'):
        raise ConfigFileNotFound(config_dir/'.secrets.yaml')

    cfg = Dynaconf(
        envvar_prefix='DYNACONF',  # replaced "DYNACONF" by 'DYNACONF'
        settings_files=[config_dir/'settings.yaml', config_dir/'.secrets.yaml'],
        environments=True,
        env=env,
    )

    # `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
    # `settings_files` = Load these files in the order.

    zope.component.provideUtility(cfg, ICfg)
