import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        await ctx.send(
            embed=discord.Embed(color=0xfa5050, title='Error!', description=f'```{error!r}```'[:1800])
        )


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
