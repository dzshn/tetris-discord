from typing import Optional

import discord
from discord.ext import commands, tasks
from tinydb import TinyDB, where


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: TinyDB = bot.db
        self.update_leaderboard.start()

    @tasks.loop(minutes=5)
    async def update_leaderboard(self):
        for table in ['zen']:
            self.db.table('leaderboard').upsert(
                {
                    'table': table,
                    'top':
                        sorted(({
                            'user_id': i['user_id'],
                            'score': i['score']
                        } for i in self.db.table(table)), key=lambda x: x['score'], reverse=True)
                },
                where('table') == table
            )  # yapf: disable

    @update_leaderboard.before_loop
    async def before_update_leaderboard(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def top(self, ctx: commands.Context, page: Optional[int] = 0, mode: Optional[str] = None):
        if page < 0:
            raise commands.BadArgument(':eye:')

        if mode is None:
            await ctx.send(
                embed=discord.Embed(
                    color=0xfa50a0,
                    title='Top scores on all modes',
                    description='\n'.join(
                        f'**{i["table"].title()}:**\n' +
                        '\n'.join(f'\u200c · <@{j["user_id"]}>: **{j["score"]:,}**'
                                  for j in i["top"][:3])
                        for i in self.db.table('leaderboard')
                    )
                )
            )

        else:
            table = mode.lower()
            if self.db.table('leaderboard').contains(where('table') == table):
                top = self.db.table('leaderboard').get(where('table') == table)['top']
                await ctx.send(
                    embed=discord.Embed(
                        color=0xfa50a0,
                        title=f'Top scores on {table}',
                        description='\n'.join(
                            f'**#{i + 1 + page * 15}**: <@{j["user_id"]}>: **{j["score"]:,}**'
                            for i, j in enumerate(top[page * 15:(page + 1) * 15])
                        )
                    ).set_footer(text=f'Page {page} of {len(top) // 15} · top {page} {table}')
                )
            else:
                await ctx.send(f"Score for {table} doesn't exist!")


def setup(bot: commands.Bot):
    bot.add_cog(Stats(bot))
