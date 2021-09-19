import datetime
import gc
import inspect
import json
import pathlib
import psutil
import statistics
import sys
from typing import Optional

import discord
from discord.ext import commands, tasks
from tinydb import TinyDB, where


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: TinyDB = bot.db
        self.status_msg: discord.Message = None
        self.update_leaderboard.start()
        self.update_status.start()

    def cog_unload(self):
        # mmmmMMm hacky code.. erh, here's what's up with it:
        #  -> commands.Bot.close() unloads extensions before calling super().close() ...
        #      So, that gives us time to do this
        #  -> asyncio.AbstractEventLoop.create_task only keeps a weak reference to the task ...
        #      Aaand since the function ends immediately after scheduling the task,
        #      the task object is garbage collected, so the gc needs to be frozen...
        #  -> to avoid triggering this when the cog is simply reloaded,
        #      we check if this is being called from `super().close()`
        # sorry!!!  ...i don't like it either
        frames = inspect.getouterframes(sys._getframe())
        if self.status_msg is not None and any('close' in i.frame.f_code.co_names for i in frames):
            task = self.bot.loop.create_task(
                self.status_msg.edit(
                    embed=discord.Embed(
                        color=0xfa5050,
                        title='Current status',
                        description='`Status :: Offline!`'
                        # TODO: show shutdown time?
                    )
                )
            )
            gc.freeze()
            task.add_done_callback(lambda *_: gc.unfreeze())

    @tasks.loop(minutes=5)
    async def update_leaderboard(self):
        for table in ['zen']:
            top = sorted(
                ({'user_id': i['user_id'], 'score': i['score']} for i in self.db.table(table)),
                key=lambda x: x['score'], reverse=True
            )  # yapf: disable

            self.db.table('leaderboard').upsert(
                {'table': table, 'top': top, 'median': int(statistics.median(i['score'] for i in top))},
                where('table') == table
            )  # yapf: disable

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=15)
    async def update_status(self):
        await self.bot.change_presence(activity=discord.Game('Tetris || https://tetris-dsc.dzshn.xyz'))
        if self.status_msg is None:
            status_msg: dict[str, int] = self.bot.config.get('status_msg')
            if status_msg is not None:
                try:
                    self.status_msg = await self.bot.get_channel(status_msg['ch']) \
                                                    .fetch_message(status_msg['msg'])
                except discord.NotFound:
                    config = json.load(open('config.json'))
                    del config['status_msg']
                    json.dump(config, open('config.json', 'w'))
                    self.bot.config = config
            else:
                return

        proc = psutil.Process()
        with proc.oneshot():
            await self.status_msg.edit(
                embed=discord.Embed(
                    color=0xfa50a0,
                    title='Current status',
                    description=f'`Status :: Online!`\nStarted <t:{int(proc.create_time())}:R>',
                    timestamp=datetime.datetime.now()
                ).add_field(
                    name='Data/usage',
                    value=(
                        f'`db.json` has `{pathlib.Path("db.json").stat().st_size / 1024:.2f}kb` of data\n'
                        f'`{proc.memory_info().rss / 1024 / 1024:.2f} mb` of '
                        f'`{psutil.virtual_memory().total / 1024 / 1024:.2f} mb` RAM has been allocated\n'
                        f'`{proc.cpu_percent():.2f}%` CPU used in `{proc.num_threads()}` threads'
                    )
                ).set_footer(text='Updates every 15 minutes')
            )

    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def top(self, ctx: commands.Context, page: Optional[int] = 0, mode: Optional[str] = None):
        if page < 0:
            raise commands.BadArgument(':eye:')

        if mode is None:
            embed = discord.Embed(color=0xfa50a0, title='Top scores on all modes')

            for i in self.db.table('leaderboard'):
                embed.add_field(
                    name=i["table"].title(),
                    value='\n'.join(
                        '**#{}**: <@{user_id}>: **{score:,}**'.format(j + 1, **k)
                        for j, k in enumerate(i['top'][:5])
                    )
                )

            await ctx.send(embed=embed)

        else:
            table_name = mode.lower()
            if self.db.table('leaderboard').contains(where('table') == table_name):
                table = self.db.table('leaderboard').get(where('table') == table_name)
                top = table['top']
                await ctx.send(
                    embed=discord.Embed(
                        color=0xfa50a0,
                        title=f'Top scores on {table_name}',
                        description=f'*Median score: **{table["median"]:,}***\n\n' + '\n'.join(
                            f'**#{i + 1 + page * 15}**: <@{j["user_id"]}>: **{j["score"]:,}**'
                            for i, j in enumerate(top[page * 15:(page + 1) * 15])
                        )
                    ).set_footer(text=f'Page {page} of {len(top) // 15} · top {page} {table_name}')
                )
            else:
                await ctx.send(f"Score for {table_name} doesn't exist!")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def setpersiststs(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
            await ctx.message.delete()

        msg = await channel.send(
            embed=discord.Embed(color=0xfa50a0, title='...!').set_image(
                url='https://media.discordapp.net/attachments/825871731155664907/884158159537704980/dtc.gif'
            )
        )
        config = json.load(open('config.json'))
        config['status_msg'] = {'ch': channel.id, 'msg': msg.id}
        json.dump(config, open('config.json', 'w'))
        self.bot.config = config
        self.update_status.restart()


def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))
