import discord
import numpy as np
from discord.ext import commands, tasks
from tinydb import TinyDB, where
from tinydb.table import Table

from bot.lib.game import Game, Piece, Queue
from bot.lib.controls import Controls
from bot.lib.maps import Encoder


class ZenGame(Game):
    def __init__(self, save, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = Queue(initial_queue=save.get('queue', []), initial_bag=save.get('bag', []))
        if save.get('board') is not None:
            self.board, self.current_piece = Encoder.decode(save['board'])
        else:
            self.board = np.zeros((30, 10), dtype=np.int8)
            self.current_piece = Piece(self.board, self.queue.pop())

        self.score: int = save.get('score', 0)
        self.hold = save.get('hold', None)
        self.hold_lock = save.get('hold_lock', False)
        self.previous_score = self.score
        self.can_pc = self.board.any()

    def to_save(self) -> dict:
        return {
            'board': Encoder.encode(self.board, self.current_piece),
            'score': self.score,
            'queue': self.queue.next_pieces,
            'bag': self.queue.current_bag,
            'hold': self.hold,
            'hold_lock': self.hold_lock
        }


class Zen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: TinyDB = bot.db
        self.db_table: Table = bot.db.table('zen')
        self.autosave.start()

    @tasks.loop(minutes=5)
    async def autosave(self):
        for author, view in self.bot.get_cog('Manager').games.items():
            if not isinstance(view.game, ZenGame):
                continue

            self.db_table.upsert(view.game.to_save(), where('user_id') == author)

    @autosave.before_loop
    async def before_autosave(self):
        await self.bot.wait_until_ready()

    @commands.group()
    async def zen(self, ctx: commands.Context):
        """Start a Zen mode game.

        → 0 Gravity
          · possibly configurable by the end of 2024
        → All progress saved
        → Board can be reset at any time
          · via `zen restart`
        """
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

        game = ZenGame(
            self.db_table.get(where('user_id') == ctx.author.id) or {}, self.bot.config, user_settings
        )
        view = user_controls(game, ctx, msg)
        games[ctx.author.id] = view
        await view.update_message()
        await view.wait()

        self.db_table.upsert(game.to_save() | {'user_id': ctx.author.id}, where('user_id') == ctx.author.id)

        del games[ctx.author.id]

    @zen.command()
    async def restart(self, ctx: commands.Context):
        """Restarts current zen game, all score is kept"""
        games: dict[int, Controls] = self.bot.get_cog('Manager').games

        if ctx.author.id not in games or not isinstance(games[ctx.author.id].game, ZenGame):
            await ctx.send("There isn't a zen game running!")
            return

        games[ctx.author.id].game.reset()
        await games[ctx.author.id].update_message()


def setup(bot: commands.Bot):
    bot.add_cog(Zen(bot))
