import discord
from discord.ext import commands

from bot import config
from bot import controls
from bot import engine
from bot.engine.mixins import StandardScore
from bot.modes import base


class ZenGame(StandardScore, engine.BaseGame):
    pass


class ZenMode(base.BaseMode, name='zen', game_cls=ZenGame):
    async def command(self, ctx: commands.Context):
        game = ZenGame()
        view = controls.DefaultControls(game)
        message = await ctx.send(content='\u200c', view=view)
        view.set_callback(self.get_callback(game, message, view))
        view.set_check(self.get_check(ctx))
        await self.update_message(game, message, view)
        await view.wait()

    async def update_message(
        self, game: ZenGame, message: discord.Message, view: discord.ui.View
    ):
        embed = discord.Embed(
            color=0xFA50A0,
            description=game.render(tiles=config.data['skins'][0]['pieces'], lines=16),
        )

        embed.add_field(name='Score', value=game.score)

        await message.edit(content=None, embed=embed, view=view)
