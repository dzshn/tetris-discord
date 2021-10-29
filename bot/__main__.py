import pkgutil
import traceback

import discord
from discord.ext import commands

from bot import config
from bot import exts


class TetrisBot(commands.Bot):
    def __init__(self):
        # TODO: There should probably be a `prefix` function

        super().__init__(
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=True
            ),
            command_prefix=commands.when_mentioned_or(config.data['prefix']),
            case_insensitive=True,
            activity=discord.Game('Loading...'),
            status=discord.Status.dnd,
        )

        self.load_extension('yade')

        def _imp_err(name: str):
            raise ImportError(name=name)

        for module in pkgutil.walk_packages(
            exts.__path__, exts.__name__ + '.', onerror=_imp_err  # type: ignore
        ):
            try:
                self.load_extension(module.name)

            except commands.NoEntryPointError:
                pass

            except commands.ExtensionError:
                traceback.print_exc()


bot = TetrisBot()
bot.run(open('TOKEN').read())
