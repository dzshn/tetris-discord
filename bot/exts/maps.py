import discord
import numpy as np
from discord.ext import commands
from tinydb import where

from bot.lib import Game, Pieces
from bot.lib.maps import Encoder


class Maps(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def convert(self, ctx: commands.Command, *, text: str):
        text = text.strip('`\n').upper()
        board = np.zeros((text.count('\n') + 1, 10), dtype=np.int8)
        for x, line in enumerate(text.splitlines()):
            for y, char in enumerate(line):
                if x >= 30 or y >= 10:
                    raise commands.BadArgument('Matrix is too big!')

                if char == ' ' or char == '_':
                    continue
                if char == 'X' or char == 'G':
                    board[x, y] = 8
                else:
                    try:
                        board[x, y] = Pieces[char].value

                    except KeyError as e:
                        raise commands.BadArgument(f'Invalid piece "{char}"') from e

        encoded = Encoder.encode(board)
        await ctx.send(f'`{encoded}`')

    @commands.command()
    async def view(self, ctx: commands.Command, encoded: str):
        try:
            board, piece = Encoder.decode(encoded.strip('`'))
        except ValueError as e:
            raise commands.BadArgument('Invalid map string') from e

        if piece is not None:
            ghost = piece.copy()
            ghost.x += 30
            for x, y in ghost.shape + ghost.pos:
                board[x, y] = 9

            for x, y in piece.shape + piece.pos:
                board[x, y] = piece.type

        user_skin = self.bot.db.table('settings').get(where('user_id') == ctx.author.id).get('skin', 0)

        await ctx.send(
            embed=discord.Embed(
                color=0xfa50a0,
                description='\n'.join(
                    ''.join(self.bot.config['skins'][user_skin]['pieces'][j] for j in i) for i in board[-16:]
                )
            )
        )

    @commands.command()
    async def export(self, ctx: commands.Context):
        games: dict[int, discord.View] = self.bot.get_cog('Manager').games
        if ctx.author.id not in games:
            raise commands.CheckFailure("There isn't any game running!")

        game: Game = games[ctx.author.id].game
        encoded = Encoder.encode(game.board, game.current_piece)
        await ctx.send(f'`{encoded}`')


def setup(bot: commands.Bot):
    bot.add_cog(Maps(bot))
