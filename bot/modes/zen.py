import discord
from discord.ext import commands

from bot import config
from bot import controls
from bot import engine
from bot.modes import base


class ZenGame(engine.BaseGame):
    ...


class ZenMode(base.BaseMode, name='zen', game_cls=ZenGame):
    async def command(self, ctx: commands.Context):
        game = ZenGame()
        view = controls.DefaultControls(game)
        message = await ctx.send(content='\u200c', view=view)

        async def callback(interaction: discord.Interaction):
            await self.update_message(game, message)

        view.callback = callback
        await self.update_message(game, message)
        await view.wait()

    async def update_message(self, game: ZenGame, message: discord.Message):
        await message.edit(
            content=None,
            embed=discord.Embed(
                color=0xFA50A0,
                description=game.render(tiles=config['skins'][0]['pieces'], lines=16),
            ),
        )
