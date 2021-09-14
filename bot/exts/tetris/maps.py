import base64

import discord
import numpy as np
from discord.ext import commands
from numpy.typing import NDArray


class Maps(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def view(self, ctx: commands.Command, encoded: str):
        board, piece = encoded.strip('`').split('@') if '@' in encoded else (encoded.strip('`'), None)
        pairs = []
        for i in base64.b64decode(board):
            pairs.append([i >> 4, i - (i >> 4 << 4)])

        board = np.reshape(pairs, (len(pairs) * 2 // 10, 10))

        await ctx.send('\n'.join(''.join(self.bot.config['emotes']['pieces'][j] for j in i) for i in board))

    @commands.command()
    async def export(self, ctx: commands.Context):
        games: dict[int, discord.View] = self.bot.get_cog('Manager').games
        if ctx.author.id not in games:
            raise commands.CheckFailure("There isn't any game running!")

        game = games[ctx.author.id].game
        board: NDArray[np.int8] = game.board.copy()
        piece = game.current_piece
        export_board = []
        for i, j in enumerate(board):
            if j.any():
                board = board[i:]
                break

        for i, j in enumerate(reversed(board)):
            if 9 in j:
                # TODO: encode garbage lines separately
                board = board[:i]

        for i, j in board.reshape(len(board.flatten()) // 2, 2):
            export_board.append((i << 4) + j)

        await ctx.send(
            f'`{base64.b64encode(bytes(export_board)).decode()}@{piece.type}+{piece.x}+{piece.y}+{piece.rot}`'
        )


def setup(bot: commands.Bot):
    bot.add_cog(Maps(bot))
