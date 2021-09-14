import discord
from discord.ext import commands


class Manager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, discord.View] = {}

    async def cog_check(self, ctx: commands.Context):
        if ctx.author.id in self.games:
            return True

        raise commands.CheckFailure("There isn't any game running!")

    @commands.command(aliases=['cancel', 'quit'])
    async def stop(self, ctx: commands.Context):
        """Stops the current game"""
        self.games[ctx.author.id].stop()


def setup(bot: commands.Bot):
    bot.add_cog(Manager(bot))
