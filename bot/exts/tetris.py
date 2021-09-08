import enum
import itertools
import random

import discord
import numpy as np
from numpy.typing import NDArray
from discord.ext import commands

Pieces = enum.Enum('PIECES', 'I L J S Z T O')
# EMOTES = [
#     '<:BG:883851510319026177>', '<:I_:883851823616766002>', '<:L_:883851571857854524>',
#     '<:J_:883851652547891210>', '<:S_:883852392460845076>', '<:Z_:883852343442034749>',
#     '<:T_:883852443044184145>', '<:O_:883852312462913556>', '<:GA:883951745309483079>',
#     '<:GH:883951718549823528>'
# ]
EMOTES = [
    '<:BG:883851510319026177>', '<:I_:884981803448930345>', '<:L_:884981803260190740>',
    '<:J_:884981802966585396>', '<:S_:884981802886914059>', '<:Z_:884981803033690114>',
    '<:T_:884981803067269121>', '<:O_:884981803125997569>', '<:GA:883951745309483079>',
    '<:GH:883951718549823528>'
]
SHAPES = [
    [
        [(1, 0), (1, 1), (1, 2), (1, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)]
    ],
    [
        [(0, 2), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 0)],
        [(0, 0), (0, 1), (1, 1), (2, 1)]
    ],
    [
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 0), (2, 1)]
    ],
    [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (2, 0), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)]
    ],
    [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 2), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)]
    ],
    [
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 0), (1, 1), (2, 1)]
    ],
    [
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (1, 2)]
    ]
]  # yapf: disable


class Piece:
    def __init__(self, t: int, x: int = 10, y: int = 3, r: int = 0):
        self.type = t
        self.pos = (x, y)
        self.rot = r

    @property
    def x(self) -> int:
        return self.pos[0]

    @x.setter
    def x(self, value):
        self.pos = (value, self.y)

    @property
    def y(self) -> int:
        return self.pos[1]

    @y.setter
    def y(self, value):
        self.pos = (self.x, value)

    @property
    def shape(self) -> NDArray[np.int8]:
        return np.array(SHAPES[self.type - 1][self.rot], dtype=np.int8)

    def rotate(self, r: int):
        self.rot += r
        if self.rot > 3:
            self.rot -= 4

        if self.rot < 0:
            self.rot += 4

    def overlaps(self, board: NDArray) -> bool:
        for sx, sy in self.shape + self.pos:
            if sx >= board.shape[0] or sy >= board.shape[1] or board[sx, sy] != 0:
                return True

        return False

    def __add__(self, other):
        if isinstance(other, tuple):
            x, y = other

        elif isinstance(other, Piece):
            x, y = other.pos

        else:
            return NotImplemented

        return Piece(self.type, self.x + x, self.y + y, self.rot)


class Game:
    def __init__(self):
        self.board = np.zeros((30, 10), dtype=int)
        self._queue = self._queue_iter()
        self.current_piece = Piece(next(self._queue))
        self.queue = list(itertools.islice(self._queue, 4))
        self.hold = None

    def _queue_iter(self) -> int:
        current_bag = []
        while True:
            if not current_bag:
                current_bag = [i.value for i in Pieces]
                random.shuffle(current_bag)

            yield current_bag.pop()

    def get_text(self) -> str:
        board = self.board.copy()
        piece = self.current_piece
        for i in range(piece.x, 30):
            if (piece + (i, 0)).overlaps(board):
                ghost_x = i - 1
                break

        for sx, sy in piece.shape + piece.pos + (ghost_x, 0):
            board[sx, sy] = 9

        for sx, sy in piece.shape + piece.pos:
            board[sx, sy] = piece.type

        return '\n'.join(''.join(EMOTES[j] for j in i) for i in board[14:])


class Controls(discord.ui.View):
    def __init__(self, game: Game, message: discord.Message):
        super().__init__()
        self.game = game
        self.message = message

    @discord.ui.button(label='X', style=discord.ButtonStyle.danger, row=0)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()
        for i in self.children:
            i.disabled = True

        await self.update_message()

    @discord.ui.button(label='⇊', style=discord.ButtonStyle.primary, row=0)
    async def hard_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        piece = self.game.current_piece
        for i in range(piece.x, 30):
            if (piece + (i, 0)).overlaps(self.game.board):
                ghost_x = i - 1
                break

        for sx, sy in piece.shape + piece.pos + (ghost_x, 0):
            self.game.board[sx, sy] = piece.type

        self.game.current_piece = Piece(self.game.queue.pop(0))
        self.game.queue.append(next(self.game._queue))
        await self.update_message()

    @discord.ui.button(label='\u200c', disabled=True, row=0)
    async def _1(self, *_):
        pass

    @discord.ui.button(label='⤭', style=discord.ButtonStyle.primary, row=0)
    async def swap(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.game.hold is None:
            self.game.hold = self.game.current_piece.type
            self.game.current_piece = Piece(self.game.queue.pop(0))
            self.game.queue.append(next(self.game._queue))

        else:
            self.game.hold, self.game.current_piece = self.game.current_piece.type, Piece(self.game.hold)

        button.disabled = True
        await self.update_message()
        button.disabled = False

    @discord.ui.button(label='🗘', style=discord.ButtonStyle.primary, row=0)
    async def rotate_cw2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.rotate(2)
        await self.update_message()

    @discord.ui.button(label='🡸', style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.y -= 1
        await self.update_message()

    @discord.ui.button(label='🡻', style=discord.ButtonStyle.primary, row=1)
    async def soft_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.update_message()

    @discord.ui.button(label='🡺', style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.y += 1
        await self.update_message()

    @discord.ui.button(label='↺', style=discord.ButtonStyle.primary, row=1)
    async def rotate_ccw(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.rotate(-1)
        await self.update_message()

    @discord.ui.button(label='↻', style=discord.ButtonStyle.primary, row=1)
    async def rotate_cw(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.rotate(1)
        await self.update_message()

    async def update_message(self):
        embed = discord.Embed(color=0xfa50a0, description=self.game.get_text())
        embed.add_field(
            name='Hold', value=f'`{Pieces(self.game.hold).name}`' if self.game.hold is not None else '`None`'
        )
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in self.game.queue))
        await self.message.edit(embed=embed, view=self)


class TetrisCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def dtc(self, ctx: commands.Context):
        await ctx.send(
            embed=discord.Embed(
                description='\n'.join(
                    ''.join(EMOTES[' ILJSZTO'.find(j)] for j in i) for i in ['          '] * 9 + [
                        '  LL      ',
                        '   LZZ   I',
                        'JJ LTZZOOI',
                        'J  TTTIOOI',  # My beloved <3
                        'J   SSIZZI',
                        'OO SSLIJZZ',
                        'OO LLLIJJJ'
                    ]
                )
            )
        )

    @commands.command()
    async def zen(self, ctx: commands.Context):
        msg = await ctx.send(embed=discord.Embed(color=0xfa50a0, description='<a:dtcg:884158922020225054>'))
        game = Game()
        embed = discord.Embed(color=0xfa50a0, description=game.get_text())
        embed.add_field(name='Hold', value='`None`')
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in game.queue))
        view = Controls(game, msg)
        await msg.edit(embed=embed, view=view)


def setup(bot: commands.Bot):
    bot.add_cog(TetrisCog(bot))
