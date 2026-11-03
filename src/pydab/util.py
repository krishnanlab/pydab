import logging.config
import pathlib

import yaml


def config_logger():
    """Configure logger using the config file."""
    path = pathlib.Path(__file__).absolute().parent.joinpath("logging.yaml")
    with open(path) as f:
        logging.config.dictConfig(yaml.safe_load(f.read()))
