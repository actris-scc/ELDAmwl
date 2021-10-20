import zope
from dynaconf import Dynaconf

from ELDAmwl.component.interface import ICfg


def register_config(env=None):
    cfg = Dynaconf(
        envvar_prefix="DYNACONF",
        settings_files=['settings.yaml', '../.secrets.yaml'],
        environments=True,
        env=env,
    )

    # `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
    # `settings_files` = Load these files in the order.

    zope.component.provideUtility(cfg, ICfg)
