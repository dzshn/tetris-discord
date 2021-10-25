import pathlib
import sys
import warnings

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


class _Config:
    """Singleton class that lazy-loads `config.yaml`

    If such file isn't present or is invalid, warn and fallback to `config.sample.yaml`
    If the file is modified, other calls to .config will return the new version

    This shouldn't be directly used. Instead, a singleton instance is returned by `bot.config`
    """

    __slots__ = ('_cache_time', '_cached_cfg', '_sample_cfg')

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __init__(self):
        self._cache_time = 0
        self._cached_cfg: dict = None
        self._sample_cfg: dict = None

    @property
    def data(self) -> dict:
        if self._sample_cfg is None:
            self._sample_cfg = yaml.load(
                open('config.sample.yaml').read(), Loader=Loader
            )

        cfg_path = pathlib.Path('config.yaml')
        if not cfg_path.exists():
            warnings.warn('`config.yaml` does not exist', RuntimeWarning)
            return self._sample_cfg

        # XXX: Does `.stat()` have considerable overhead?
        cfg_stat = cfg_path.stat()
        if self._cached_cfg is None or self._cache_time < cfg_stat.st_mtime:
            try:
                self._cached_cfg = yaml.load(cfg_path.read_text(), Loader=Loader)

            except yaml.YAMLError:
                warnings.warn('`config.yaml` has invalid yaml', RuntimeWarning)
                return self._sample_cfg

            self._cache_time = cfg_stat.st_mtime
            if not isinstance(self._cached_cfg, dict):
                warnings.warn(
                    '`config.yaml` doest not convert to `dict`', RuntimeWarning
                )
                return self._sample_cfg

            if not self._cached_cfg.keys() == self._sample_cfg.keys():
                warnings.warn(
                    '`config.yaml` contains missing and/or invalid keys', RuntimeWarning
                )
                return self._sample_cfg

        return self._cached_cfg

    def __getitem__(self, key):
        return self.data[key]


sys.modules[__name__] = _Config()
