import abc
import functools

from discord.ext import commands

from bot.db import get_session
from bot.engine import BaseGame


class ABCMeta(abc.ABCMeta):
    # See https://bugs.python.org/issue43827 and https://github.com/python/cpython/pull/25385
    def __new__(mcls, name, bases, namespace, /, **kwargs):
        cls = type.__new__(mcls, name, bases, namespace, **kwargs)
        abc._abc_init(cls)
        return cls


class BaseMode(metaclass=ABCMeta):
    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init_subclass__(cls, /, name: str, game_cls: BaseGame):
        cls.name = name
        cls.game_cls = game_cls

    @abc.abstractmethod
    async def command(self, ctx: commands.Context):
        pass

    @functools.cached_property
    def db(self):
        return get_session(self.name)
