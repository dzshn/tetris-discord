import discord
import time
import math
from discord.ext import commands
from tinydb import TinyDB, where
from tinydb.table import Table

from bot.lib.game import Game
from bot.lib.controls import Controls


class MarathonGame(Game):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.level = 0
        self.until_lock = 20.0
        self.gravity_remainder = 0.0
        self.last_piece_time = time.time()

    def lock_piece(self):
        super().lock_piece()
        self.last_piece_time = time.time()
        self.gravity_remainder = 0
        self.until_lock = 20.0

    def drag(self, dist):
        super().drag(dist)
        delta = (time.time() - self.last_piece_time)
        self.gravity_remainder, drop = math.modf(
            delta / (0.8 - (self.level * 0.007)) + self.gravity_remainder
        )
        self.current_piece.x += int(drop)
        self.until_lock -= delta
        if self.until_lock <= 0:
            self.drop(30)
            self.lock_piece()

    def to_save(self) -> dict:
        return {
            'score': self.score,
        }


class Marathon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: TinyDB = bot.db
        self.db_table: Table = bot.db.table('marathon')

    @commands.command()
    async def marathon(self, ctx: commands.Context):
        if ctx.invoked_subcommand is not None:
            return

        games: dict[int, Controls] = self.bot.get_cog('Manager').games

        if ctx.author.id in games:
            await ctx.send("There's already a game running!")
            return

        embed = discord.Embed(color=0xfa50a0, title='Loading...').set_image(
            url='https://media.discordapp.net/attachments/825871731155664907/884158159537704980/dtc.gif'
        )
        msg = await ctx.send(embed=embed)
        user_settings: dict[str, int] = self.db.table('settings').get(where('user_id') == ctx.author.id) or {}
        user_controls = Controls.from_config(user_settings)

        game = MarathonGame(self.bot.config, user_settings)
        view = user_controls(game, ctx, msg)
        games[ctx.author.id] = view
        await view.update_message()
        await view.wait()

        self.db_table.upsert(game.to_save() | {'user_id': ctx.author.id}, where('user_id') == ctx.author.id)

        del games[ctx.author.id]


def setup(bot: commands.Bot):
    bot.add_cog(Marathon(bot))
