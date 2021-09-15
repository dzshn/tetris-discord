import traceback

import discord
from discord.ext import commands

from bot.utils.formatting import codeblock


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandInvokeError) and await self.bot.is_owner(ctx.author):
            await ctx.send(
                embed=discord.Embed(
                    title='Error!',
                    color=0xfa5050,
                    description=codeblock(
                        '\n'.join(traceback.format_exception(type(error), error, error.__traceback__)),
                        max_size=4096
                    )
                )
            )

        else:
            await ctx.send(
                embed=discord.Embed(color=0xfa5050, title='Error!', description=codeblock(repr(error)))
            )


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
