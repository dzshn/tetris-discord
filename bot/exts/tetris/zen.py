import discord
from discord.ext import commands

from bot.lib import Controls, Game


class TetrisCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def zen(self, ctx: commands.Context):
        games: dict[int, discord.View] = self.bot.get_cog('Manager').games

        if ctx.author.id in games:
            await ctx.send("There's already a game running!")
            return

        games[ctx.author.id] = None

        embed = discord.Embed(color=0xfa50a0, title='Loading...').set_image(
            url='https://media.discordapp.net/attachments/825871731155664907/884158159537704980/dtc.gif'
        )
        msg = await ctx.send(embed=embed)
        game = Game(self.bot.config)
        view = Controls(game, ctx, msg)
        games[ctx.author.id] = view
        await view.update_message()
        await view.wait()

        del games[ctx.author.id]


def setup(bot: commands.Bot):
    bot.add_cog(TetrisCog(bot))
