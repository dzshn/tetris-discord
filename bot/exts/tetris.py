from discord.ext import commands

from bot import modes


class Tetris(commands.Cog):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        for mode in modes.MODES:

            @commands.command(name=mode.name)
            async def cmd(self, ctx, *_, **__):
                return await mode().command(ctx)

            setattr(cls, mode.name, cmd)
            self.__cog_commands__ += (cmd._update_copy(cls.__cog_settings__),)  # type: ignore

        return self


def setup(bot: commands.Bot):
    bot.add_cog(Tetris())
