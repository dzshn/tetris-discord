import json
import pathlib
import pkgutil
import traceback

import discord
from discord.ext import commands
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware

from bot import exts


class TetrisBot(commands.Bot):
    def __init__(self):
        config_path = pathlib.Path('config.json')
        if not config_path.exists():
            open('config.json', 'w').write(open('config_defaults.json').read())

        self.config = json.load(open('config_defaults.json')) | json.load(open('config.json'))
        self.db = TinyDB('db.json', storage=CachingMiddleware(JSONStorage))

        super().__init__(
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=True
            ),
            command_prefix=commands.when_mentioned_or('tt!'),
            case_insensitive=True,
        )

        def _imp_err(name: str):
            raise ImportError(name=name)

        for module in pkgutil.walk_packages(exts.__path__, exts.__name__ + '.', onerror=_imp_err):
            try:
                self.load_extension(module.name)

            except commands.NoEntryPointError:
                pass

            except commands.ExtensionError:
                traceback.print_exc()

    async def close(self):
        await super().close()
        self.db.close()


bot = TetrisBot()
bot.run(open('TOKEN').read())
