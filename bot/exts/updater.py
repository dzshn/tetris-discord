import asyncio
import atexit
import os
from asyncio.subprocess import create_subprocess_shell
from asyncio.subprocess import PIPE
from asyncio.subprocess import STDOUT
from typing import Literal

import psutil
from discord.ext import commands


class OnMaintenance(commands.CheckFailure):
    pass


class Updater(commands.Cog):
    def __init__(self):
        ...

    async def cog_check(self, ctx: commands.Context):
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner()

        return True

    @commands.command(hidden=True)
    @commands.is_owner()
    async def update(
        self, ctx: commands.Context, pull_opt: Literal['pull', 'nopull'] = 'pull'
    ):
        if pull_opt == 'pull':
            fetch_proc = await create_subprocess_shell(
                'git fetch --dry-run', stdout=PIPE, stderr=STDOUT
            )
            fetch_stdout, _ = await fetch_proc.communicate()
            if fetch_stdout:
                await ctx.send(
                    'There might be changes to pull, proceed?\n'
                    f'```$ git fetch --dry-run\n{fetch_stdout.decode()}```'
                )

                try:
                    reply = await ctx.bot.wait_for(
                        'message',
                        check=lambda m: (
                            m.author == ctx.author and m.channel == ctx.channel
                        ),
                        timeout=60,
                    )
                    reply = reply.content.lower()

                except asyncio.TimeoutError:
                    reply = None

                if reply in ('y', 'yes'):
                    pull_proc = await create_subprocess_shell(
                        'git pull --ff-only', stdout=PIPE, stderr=STDOUT
                    )
                    pull_stdout, _ = await pull_proc.communicate()
                    await ctx.send(f'```$ git pull --ff-only\n{pull_stdout}```')

            else:
                await ctx.send('Nothing to pull, skipping')

        # TODO: The bot should check for running games somehow
        cmdline = psutil.Process().cmdline()
        atexit.register(os.execlp, cmdline[0], *cmdline)
        await ctx.bot.close()


def setup(bot: commands.Bot):
    bot.add_cog(Updater())
