import asyncio
import subprocess
from typing import Literal

import discord
import psutil
from discord.ext import commands


class OnMaintenance(commands.CheckFailure):
    pass


class Manager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, discord.View] = {}

    PULL_OPTS = ('nopull', 'pull', 'forcepull')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def doupdate(self, ctx: commands.Context, pull_option: Literal[PULL_OPTS] = 'pull'):
        if pull_option != 'nopull':
            git_proc = await asyncio.subprocess.create_subprocess_shell(
                'git pull --dry-run --no-ff', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            git_stdout, git_stderr = await git_proc.communicate()
            if git_stdout.decode() or git_stderr.decode():
                await ctx.send(
                    'There may be changes to pull, proceed? [send yes/no]\n'
                    '```'
                    '$ git pull --dry-run --no-ff\n'
                    f'{git_stderr.decode()}\n{git_stdout.decode()}'
                    '```'
                )
                if pull_option != 'forcepull':
                    reply = await self.bot.wait_for(
                        'message',
                        check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                        timeout=60
                    ).content.lower()
                    do_pull = reply in ('y', 'yes')
                else:
                    do_pull = True

                if do_pull:
                    pull_proc = await asyncio.subprocess.create_subprocess_shell(
                        'git pull --no-ff', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                    pull_stdout, pull_stderr = await pull_proc.communicate()
                    if pull_proc.returncode != 0:
                        raise RuntimeError(
                            f'`git pull --no-ff` returned non-zero code {pull_proc.returncode}; '
                            f'stdout={pull_stdout!r} stderr={pull_stderr!r}'
                        )

                    await ctx.send('Pulled changes')

        async def lock(ctx):
            raise OnMaintenance('Currently reloading, sorry!')

        self.bot.add_check(lock)
        await self.bot.change_presence(status=discord.Status.dnd, activity=discord.Game('Reloading!'))

        if self.games:
            await asyncio.sleep(120)
            for view in self.games.values():
                view.stop()

        await asyncio.sleep(10)
        # FIXME: This forks and doesn't inherit the console (if any)
        subprocess.Popen(psutil.Process().cmdline())
        await self.bot.close()

    @commands.command(aliases=['cancel', 'quit'])
    async def stop(self, ctx: commands.Context):
        """Stops the current game"""
        if ctx.author.id not in self.games:
            raise commands.CheckFailure("There isn't any game running!")

        self.games[ctx.author.id].stop()
        await ctx.message.add_reaction('\N{waving hand sign}')


def setup(bot: commands.Bot):
    bot.add_cog(Manager(bot))
