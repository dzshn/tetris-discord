import discord
from discord.ext import commands
from tinydb import where
from tinydb.table import Table

from bot.lib import Controls, Game
from bot.lib.maps import Encoder


class Zen(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: Table = bot.db.table('zen')

    @commands.command()
    async def zen(self, ctx: commands.Context):
        games: dict[int, discord.View] = self.bot.get_cog('Manager').games

        if ctx.author.id in games:
            await ctx.send("There's already a game running!")
            return

        games[ctx.author.id] = None

        embed = discord.Embed(color=0xfa50a0, title='Loading...').set_image(
            url='https://media.discordapp.net/attachments/825871731155664907/884158159537704980/dtc.gif'
        )
        msg = await ctx.send(embed=embed)
        game = Game(self.bot.config)
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


def setup(bot: commands.Bot):
    bot.add_cog(Zen(bot))
