import discord
from discord.ext import commands, tasks
from tinydb import where
from tinydb.table import Table

from bot.lib import Controls, Game
from bot.lib.maps import Encoder


class ZenGame(Game):
    pass


class Zen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Table = bot.db.table('zen')
        self.autosave.start()

    @tasks.loop(minutes=5)
    async def autosave(self):
        for author, view in self.bot.get_cog('Manager').games:
            if not isinstance(view.game, ZenGame):
                continue

            game: ZenGame = view.game
            save = {
                'user_id': author,
                'board': Encoder.encode(game.board, game.current_piece),
                'score': game.score,
                'queue': game.queue,
                'hold': game.hold,
                'hold_lock': game.hold_lock
            }

            self.db.upsert(save, where('user_id') == author)

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
        game = ZenGame(self.bot.config)
        if (save := self.db.get(where('user_id') == ctx.author.id)) is not None:
            game.board, game.current_piece = Encoder.decode(save['board'])
            game.score = save['score']
            game.queue = save['queue']
            game.hold = save['hold']
            game.hold_lock = save['hold_lock']

        view = Controls(game, ctx, msg)
        games[ctx.author.id] = view
        await view.update_message()
        await view.wait()

        save = {
            'user_id': ctx.author.id,
            'board': Encoder.encode(game.board, game.current_piece),
            'score': game.score,
            'queue': game.queue,
            'hold': game.hold,
            'hold_lock': game.hold_lock
        }

        self.db.upsert(save, where('user_id') == ctx.author.id)

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
