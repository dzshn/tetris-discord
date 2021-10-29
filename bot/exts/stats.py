import datetime
import gc
from typing import Optional

import aioredis
import discord
import psutil
from discord.ext import commands
from discord.ext import tasks

from bot import config
from bot.db import get_session


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._status_message: Optional[discord.Message] = None
        self.update_status.start()

    def cog_unload(self):
        if self._status_message is None:
            return

        task = self.bot.loop.create_task(
            self._status_message.edit(
                embed=discord.Embed(
                    color=0xFA5050,
                    title='Offline!',
                )
            )
        )

        # We might be mid-shutdown, in that case, the task object
        # is destroyed as `asyncio` only keeps a weakref to it,
        # so temporarily freeze the garbage collector
        #
        # notes:
        #   - atexit does not work for this as it's
        #     called after the loop is closed
        #   - just keeping this task under an attr
        #     doesn't work as it'll also be destroyed
        #   - related(?): https://bugs.python.org/issue21163
        gc.freeze()
        task.add_done_callback(lambda *_: gc.unfreeze())

    @tasks.loop(minutes=5)
    async def update_status(self):
        channel: Optional[discord.TextChannel] = self.bot.get_channel(
            config.data['status-channel']
        )  # type: ignore
        if channel is None:
            self.update_status.cancel()
            return

        if self._status_message is None:
            async for msg in channel.history(limit=10):
                if msg.author == self.bot.user:
                    self._status_message = msg
                    break
            else:
                self._status_message = await channel.send('\u200c')

        proc = psutil.Process()
        db = get_session()

        with proc.oneshot():
            embed = discord.Embed(
                color=0xFA50A0,
                title='Current stats',
                description=f'Online!\n\nStarted <t:{int(proc.create_time())}:R>',
                timestamp=datetime.datetime.now(),
            )

            try:
                db_mem = await db.memory_stats()
                embed.add_field(
                    name='Database',
                    value=(
                        f'**Session ::** {type(db).__name__}\n'
                        f'⇒ Memory allocated: `{db_mem["dataset.bytes"] / 1024:.2f}kb` (data) '
                        f'+ `{db_mem["overhead.total"] / 1024:.2f}kb` (redis)\n'
                        f'⇒ Keys stored: `{db_mem["keys.count"]:,}`\n'
                    ),
                    inline=False,
                )

            except aioredis.ResponseError:
                pass

            embed.add_field(
                name='Usage',
                value=(
                    f'**Bot ::** process info\n'
                    f'⇒ Memory allocated: `{proc.memory_info().rss / 1024 / 1024:.2f}mb`\n'
                    f'⇒ CPU usage: `{proc.cpu_percent():.1f}%` in `{proc.num_threads()}` '
                    'threads\n'
                    f'**Bot ::** discord info\n'
                    f'⇒ Latency: `{self.bot.latency * 1000:.1f}ms`'
                ),
                inline=False,
            )

            embed.set_footer(text='Updates every 5 minutes')

        await self._status_message.edit(embed=embed)

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()
        await self.bot.change_presence(activity=discord.Game('Tetris ─ td.dzshn.xyz'))


def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))
