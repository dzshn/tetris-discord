import pathlib
import types

import yaml

try:
    from yaml import CLoader as Loader

except ImportError:
    from yaml import Loader


def _data() -> dict:
    sample_path = pathlib.Path("config.sample.yaml")
    config_path = pathlib.Path("config.yaml")

    sample = yaml.load(sample_path.read_text(), Loader=Loader)

    if config_path.exists():
        try:
            config = yaml.load(config_path.read_text(), Loader=Loader)
            if isinstance(config, dict):
                return sample | config

        except yaml.YAMLError:
            pass

    return sample


config = types.MappingProxyType(_data())
