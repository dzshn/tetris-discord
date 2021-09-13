import base64

import discord
import numpy as np
from discord.ext import commands
from numpy.typing import NDArray


class Manager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.games: dict[int, discord.View] = {}

    async def cog_check(self, ctx: commands.Context):
        if ctx.author.id in self.games:
            return True

        raise commands.CheckFailure("There isn't any game running!")

    @commands.command()
    async def view(self, ctx: commands.Command, encoded: str):
        board, piece = encoded.strip('`').split('@')
        pairs = []
        for i in base64.b64decode(board):
            pairs.append([i >> 4, i & 0b1111])

        await ctx.send(
            '\n'.join(
                ''.join(self.bot.config['emotes']['pieces'][j]
                        for j in i)
                for i in np.reshape(pairs, (len(pairs) * 2 // 10, 10))
            )
        )

    @commands.command()
    async def export(self, ctx: commands.Context):
        game = self.games[ctx.author.id].game
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

    @commands.command(aliases=['cancel', 'quit'])
    async def stop(self, ctx: commands.Context):
        """Stops the current game"""
        self.games[ctx.author.id].stop()


def setup(bot: commands.Bot):
    bot.add_cog(Manager(bot))
