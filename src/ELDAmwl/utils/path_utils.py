from logging import ERROR
from logging import log
from pathlib import Path


def dir_not_found_hint(path_str):
    abs_path = Path(path_str).absolute()

    log(ERROR,
        """To create the missing directory please do\n
           $mkdir {path}
        """.format(path=abs_path))
