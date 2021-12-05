import discord
from discord.ext import commands

import engine
from bot import controls
from bot import modes


class Tetris(commands.Cog):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        for mode in modes.MODES:
            mode.cog = self

            @commands.command(name=mode.name)
            async def cmd(self, ctx: commands.Context):
                await mode().command(ctx)

            setattr(cls, mode.name, cmd)
            self.__cog_commands__ += (cmd._update_copy(cls.__cog_settings__),)  # type: ignore

        return self

    def __init__(self):
        self.games: dict[int, tuple[engine.BaseGame, controls.Controls]] = {}

    @commands.command(hidden=True, aliases=['play', 'start'])
    async def tetris(self, ctx: commands.Context):
        await ctx.invoke(self.zen, ctx)

    @commands.command(aliases=['stop', 'leave'])
    async def quit(self, ctx: commands.Context):
        game, ctrl = self.games[ctx.author.id]
        ctrl.stop()
        await ctx.message.add_reaction('\N{waving hand sign}')

    @commands.command(aliases=['reset'])
    async def restart(self, ctx: commands.Context):
        try:
            await ctx.message.delete()

        except discord.Forbidden:
            pass

        game, ctrl = self.games[ctx.author.id]
        game.reset()
        await ctrl._callback()


def setup(bot: commands.Bot):
    bot.add_cog(Tetris())
