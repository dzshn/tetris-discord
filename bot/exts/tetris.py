import enum
import itertools
import math
import random
from typing import Any

import discord
import numpy as np
from numpy.typing import NDArray
from discord.ext import commands

Pieces = enum.Enum('PIECES', 'I L J S Z T O')
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
    def __init__(self, board: NDArray[np.int8], t: int, x: int = 10, y: int = 3, r: int = 0):
        self.board = board
        self.type = t
        self.pos = (x, y)
        self._rot = r

    @property
    def x(self) -> int:
        return self.pos[0]

    @x.setter
    def x(self, value: int):
        target = self.x
        step = int(math.copysign(1, value - self.x))
        for _ in range(abs(self.x - value)):
            if Piece(self.board, self.type, target + step, self.y, self.rot).overlaps():
                break

            target += step

        self.pos = (target, self.y)

    @property
    def y(self) -> int:
        return self.pos[1]

    @y.setter
    def y(self, value: int):
        target = self.y
        step = int(math.copysign(1, value - self.y))
        for _ in range(abs(self.y - value)):
            if Piece(self.board, self.type, self.x, target + step, self.rot).overlaps():
                break

            target += step

        self.pos = (self.x, target)

    @property
    def rot(self) -> int:
        return self._rot

    @rot.setter
    def rot(self, value: int):
        value %= 4
        if Piece(self.board, self.type, self.x, self.y, value).overlaps():
            return

        self._rot = value

    @property
    def shape(self) -> NDArray[np.int8]:
        return np.array(SHAPES[self.type - 1][self.rot], dtype=np.int8)

    def copy(self):
        return Piece(self.board, self.type, self.x, self.y, self.rot)

    def overlaps(self) -> bool:
        board = self.board
        for sx, sy in self.shape + self.pos:
            if not 0 <= sx < board.shape[0]:
                return True

            if not 0 <= sy < board.shape[1]:
                return True

            if board[sx, sy]:
                return True

        return False

    def __add__(self, other):
        if isinstance(other, tuple):
            x, y = other

        elif isinstance(other, Piece):
            x, y = other.pos

        else:
            return NotImplemented

        return Piece(self.board, self.type, self.x + x, self.y + y, self.rot)


class Game:
    def __init__(self, config: dict[str, Any]):
        self.emotes: list[str] = config['emotes']['pieces']
        self.board = np.zeros((30, 10), dtype=np.int8)
        self._queue = self._queue_iter()
        self.current_piece = Piece(self.board, next(self._queue))
        self.queue = list(itertools.islice(self._queue, 4))
        self.hold = None
        self.hold_lock = False

    def _queue_iter(self) -> int:
        current_bag = []
        while True:
            if not current_bag:
                current_bag = [i.value for i in Pieces]
                random.shuffle(current_bag)

            yield current_bag.pop()

    def lock_piece(self):
        piece = self.current_piece
        for sx, sy in piece.shape + piece.pos:
            self.board[sx, sy] = piece.type

        self.current_piece = Piece(self.board, self.queue.pop(0))
        self.queue.append(next(self._queue))
        self.hold_lock = False

    def get_text(self) -> str:
        board = self.board.copy()
        piece = self.current_piece
        ghost = piece.copy()
        ghost.x += 30
        for sx, sy in ghost.shape + ghost.pos:
            board[sx, sy] = 9

        for sx, sy in piece.shape + piece.pos:
            board[sx, sy] = piece.type

        return '\n'.join(''.join(self.emotes[j] for j in i) for i in board[14:])


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

        self.game.hold_lock = True
        await self.update_message()

    @discord.ui.button(label='⇊', style=discord.ButtonStyle.primary, row=0)
    async def hard_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.x += 30
        self.game.lock_piece()
        await self.update_message()

    @discord.ui.button(label='\u200c', disabled=True, row=0)
    async def _1(self, *_):
        pass

    @discord.ui.button(label='⤭', style=discord.ButtonStyle.primary, row=0)
    async def swap(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.game.hold is None:
            self.game.hold = self.game.current_piece.type
            self.game.current_piece = Piece(self.game.board, self.game.queue.pop(0))
            self.game.queue.append(next(self.game._queue))

        else:
            self.game.hold, self.game.current_piece = self.game.current_piece.type, Piece(
                self.game.board, self.game.hold
            )

        self.game.hold_lock = True
        button.disabled = True
        await self.update_message()

    @discord.ui.button(label='🗘', style=discord.ButtonStyle.primary, row=0)
    async def rotate_cw2(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.rot += 2
        await self.update_message()

    @discord.ui.button(label='🡸', style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.y -= 1
        await self.update_message()

    @discord.ui.button(label='🡻', style=discord.ButtonStyle.primary, row=1)
    async def soft_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.x += 5
        await self.update_message()

    @discord.ui.button(label='🡺', style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.y += 1
        await self.update_message()

    @discord.ui.button(label='↺', style=discord.ButtonStyle.primary, row=1)
    async def rotate_ccw(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.rot -= 1
        await self.update_message()

    @discord.ui.button(label='↻', style=discord.ButtonStyle.primary, row=1)
    async def rotate_cw(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.game.current_piece.rot += 1
        await self.update_message()

    async def update_message(self):
        self.swap.disabled = self.game.hold_lock
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
        dtc = [' ' * 10] * 9 + [
            '  LL      ',
            '   LZZ   I',
            'JJ LTZZOOI',
            'J  TTTIOOI',  # My beloved <3
            'J   SSIZZI',
            'OO SSLIJZZ',
            'OO LLLIJJJ'
        ]
        await ctx.send(
            embed=discord.Embed(
                description='\n'.join(
                    ''.join(self.bot.config['emotes']['pieces'][' ILJSZTO'.find(j)] for j in i) for i in dtc
                )
            )
        )

    @commands.command()
    async def zen(self, ctx: commands.Context):
        msg = await ctx.send(
            embed=discord.Embed(color=0xfa50a0, title='Loading...').set_image(
                url='https://media.discordapp.net/attachments/825871731155664907/884158159537704980/dtc.gif'
            )
        )
        game = Game(self.bot.config)
        embed = discord.Embed(color=0xfa50a0, description=game.get_text())
        embed.add_field(name='Hold', value='`None`')
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in game.queue))
        view = Controls(game, msg)
        await msg.edit(embed=embed, view=view)


def setup(bot: commands.Bot):
    bot.add_cog(TetrisCog(bot))
