import abc
import functools
from typing import Any, ClassVar

import discord
from discord.ext import commands

from bot import db
from bot.engine import BaseGame


class ABCMeta(abc.ABCMeta):
    # See https://bugs.python.org/issue43827 and https://github.com/python/cpython/pull/25385
    def __new__(mcls, name, bases, namespace, /, **kwargs):
        cls = type.__new__(mcls, name, bases, namespace, **kwargs)
        abc._abc_init(cls)  # type: ignore
        return cls


class BaseMode(metaclass=ABCMeta):
    name: ClassVar[str]
    game_cls: ClassVar[type]

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init_subclass__(cls, /, name: str, game_cls: BaseGame):
        cls.name = name
        cls.game_cls = game_cls  # type: ignore

    @abc.abstractmethod
    async def command(self, ctx: commands.Context):
        pass

    @abc.abstractmethod
    async def update_message(
        self, game: Any, message: discord.Message, view: discord.ui.View
    ):
        pass

    @functools.cached_property
    def db(self):
        return db.get_object()

    def get_callback(
        self, game: BaseGame, message: discord.Message, view: discord.ui.View
    ):
        async def callback(*_):
            return await self.update_message(game, message, view)

        return callback

    def get_check(self, ctx: commands.Context):
        async def check(interaction: discord.Interaction):
            return interaction.user == ctx.author

        return check
