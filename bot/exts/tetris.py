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
# yapf: disable
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
]
SRS_KICKS = [
    [
        [...],
        [(+0, -1), (-1, -1), (+2, +0), (+2, -1)],            # 0 -> 1  +90
        [(-1, +0), (-1, +1), (-1, -1), (+0, +1), (+0, -1)],  # 0 -> 2  180
        [(+0, +1), (-1, +1), (+2, +0), (+2, +1)]             # 0 -> 3  -90
    ],
    [
        [(+0, +1), (+1, +1), (-2, +0), (-2, +1)],            # 1 -> 0  -90
        [...],
        [(+0, +1), (+1, +1), (-2, +0), (-2, +1)],            # 1 -> 2  +90
        [(+0, +1), (-2, +1), (-1, +1), (-2, +0), (-1, +0)]   # 1 -> 3  180
    ],
    [
        [(+1, +0), (+1, -1), (+1, 1), (+0, -1), (+0, +1)],   # 2 -> 0  180
        [(+0, -1), (-1, -1), (+2, +0), (+2, -1)],            # 2 -> 1  -90
        [...],
        [(+0, +1), (-1, +1), (+2, +0), (+2, +1)]             # 2 -> 3  +90
    ],
    [
        [(+0, -1), (+1, -1), (-2, +0), (-2, -1)],            # 3 -> 0  +90
        [(+0, -1), (-2, -1), (-1, -1), (-2, +0), (-1, +0)],  # 3 -> 1  180
        [(+0, -1), (+1, -1), (-2, +0), (-2, -1)],            # 3 -> 2  -90
        [...]
    ]
]
# yapf: enable


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
        previous = self._rot
        if Piece(self.board, self.type, self.x, self.y, value).overlaps():
            for x, y in SRS_KICKS[previous][value]:
                if not Piece(self.board, self.type, self.x + x, self.y + y, value).overlaps():
                    self.pos = (self.x + x, self.y + y)
                    break
            else:
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
        self.combo = 0
        self.b2b = 0
        self.score = 0
        self.previous_score = 0
        self.last_move: str = None
        self.action_text: str = None
        self.can_pc = False

    def _queue_iter(self) -> int:
        current_bag = []
        while True:
            if not current_bag:
                current_bag = [i.value for i in Pieces]
                random.shuffle(current_bag)

            yield current_bag.pop()

    def lock_piece(self):
        if not self.can_pc:
            self.can_pc = True

        piece = self.current_piece
        for sx, sy in piece.shape + piece.pos:
            self.board[sx, sy] = piece.type

        tspin = False
        if self.current_piece.type == Pieces.T.value:
            x, y = self.current_piece.pos
            max_x, max_y = self.board.shape
            if x + 2 < max_x and y + 2 < max_y:
                corners = sum(self.board[(x, x + 2, x, x + 2), (y, y, y + 2, y + 2)] != 0)

            elif x + 2 > max_x and y + 2 < max_y:
                corners = 2
                corners += sum(self.board[(x, x), (y, y + 2)] != 0)

            elif x + 2 < max_x and y + 2 > max_y:
                corners = 2
                corners += sum(self.board[(x, x + 2), (y, y)] != 0)

            else:
                corners = 3
                corners += self.board[x, y] != 0

            if corners >= 3 and self.last_move[0] == 'r':
                tspin = True

        line_clears = 0
        for row, clear in enumerate(self.board.all(1)):
            if clear:
                self.board[row] = 0
                self.board = np.concatenate(
                    (np.roll(self.board[:row + 1], shift=1, axis=0), self.board[row + 1:])
                )
                line_clears += 1

        if tspin:
            # TODO: Mini tspins are uncool and shouldn't give as much score.
            self.score += [400, 800, 1200, 1600][line_clears]
            self.action_text = ['T-Spin', 'T-Spin Single', 'T-Spin Double', 'T-Spin Triple'][line_clears]
            if self.b2b > 1:
                self.score += [0, 400, 600, 800][line_clears]

            self.b2b += 1
            if line_clears > 0:
                self.combo += 1

            else:
                self.combo = 0

        else:
            self.score += [0, 100, 300, 500, 800][line_clears]
            self.action_text = [None, 'Single', 'Double', 'Triple', 'Tetris'][line_clears]
            if line_clears == 4:
                self.b2b += 1
                self.combo += 1
                if self.b2b > 1:
                    self.score += 400

            elif line_clears > 0:
                self.b2b = 0
                self.combo += 1

            else:
                self.b2b = 0
                self.combo = 0

        if self.b2b > 1:
            self.action_text = f'Back-to-Back {self.action_text}'

        if self.combo > 1:
            self.score += 50 * (self.combo - 1)
            self.action_text = f'{self.action_text} + Combo {self.combo - 1}x'

        if not self.board.any():
            self.score += [0, 700, 900, 1200, 1200][line_clears]
            if self.b2b > 1:
                self.score += 2000

            self.action_text = f'Perfect Clear + {self.action_text}'

        if self.action_text:
            self.action_text += '!' * (
                line_clears // 2 + (self.combo > 1) + (self.b2b > 1) + tspin + (not self.board.any())
            )

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
    def __init__(self, game: Game, ctx: commands.Context, message: discord.Message):
        super().__init__()
        self.game = game
        self.ctx = ctx
        self.message = message

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.ctx.author

    @discord.ui.button(label='X', style=discord.ButtonStyle.danger, row=0)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.stop()
        for i in self.children:
            i.disabled = True

        self.game.hold_lock = True
        await self.update_message()

    @discord.ui.button(label='⇊', style=discord.ButtonStyle.primary, row=0)
    async def hard_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        dist = self.game.current_piece.x
        self.game.current_piece.x += 30
        self.game.previous_score = self.game.score
        self.game.score += (self.game.current_piece.x - dist) * 2
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
        prev_r = self.game.current_piece.rot
        self.game.current_piece.rot += 2
        if self.game.current_piece.rot != prev_r:
            self.game.last_move = 'r2'
        await self.update_message()

    @discord.ui.button(label='🡸', style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, button: discord.ui.Button, interaction: discord.Interaction):
        prev_y = self.game.current_piece.y
        self.game.current_piece.y -= 1
        if self.game.current_piece.y != prev_y:
            self.game.last_move = 'mL'
        await self.update_message()

    @discord.ui.button(label='🡻', style=discord.ButtonStyle.primary, row=1)
    async def soft_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        dist = self.game.current_piece.x
        self.game.current_piece.x += 5
        self.game.previous_score = self.game.score
        self.game.score += self.game.current_piece.x - dist
        await self.update_message()

    @discord.ui.button(label='🡺', style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, button: discord.ui.Button, interaction: discord.Interaction):
        prev_y = self.game.current_piece.y
        self.game.current_piece.y += 1
        if self.game.current_piece.y != prev_y:
            self.game.last_move = 'mR'
        await self.update_message()

    @discord.ui.button(label='↺', style=discord.ButtonStyle.primary, row=1)
    async def rotate_ccw(self, button: discord.ui.Button, interaction: discord.Interaction):
        prev_r = self.game.current_piece.rot
        self.game.current_piece.rot -= 1
        if self.game.current_piece.rot != prev_r:
            self.game.last_move = 'rL'
        await self.update_message()

    @discord.ui.button(label='↻', style=discord.ButtonStyle.primary, row=1)
    async def rotate_cw(self, button: discord.ui.Button, interaction: discord.Interaction):
        prev_r = self.game.current_piece.rot
        self.game.current_piece.rot += 1
        if self.game.current_piece.rot != prev_r:
            self.game.last_move = 'rR'
        await self.update_message()

    async def update_message(self):
        self.swap.disabled = self.game.hold_lock
        embed = discord.Embed(
            color=0xfa50a0,
            title=self.game.action_text or discord.Embed.Empty,
            description=self.game.get_text()
        )
        embed.add_field(
            name='Hold', value=f'`{Pieces(self.game.hold).name}`' if self.game.hold is not None else '`None`'
        )
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in self.game.queue))
        embed.add_field(
            name='Score', value=f'**{self.game.score:,}** +{self.game.score - self.game.previous_score}'
        )
        await self.message.edit(embed=embed, view=self)


class TetrisCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: dict[int, Game] = {}

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
        if ctx.author.id in self.players:
            await ctx.send("There's already a game running!")
            return

        self.players[ctx.author.id] = None
        msg = await ctx.send(
            embed=discord.Embed(color=0xfa50a0, title='Loading...').set_image(
                url='https://media.discordapp.net/attachments/825871731155664907/884158159537704980/dtc.gif'
            )
        )

        game = Game(self.bot.config)
        self.players[ctx.author.id] = game

        embed = discord.Embed(color=0xfa50a0, description=game.get_text())
        embed.add_field(name='Hold', value='`None`')
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in game.queue))
        embed.add_field(name='Score', value='**0** +0')
        view = Controls(game, ctx, msg)
        await msg.edit(embed=embed, view=view)
        await view.wait()

        del self.players[ctx.author.id]


def setup(bot: commands.Bot):
    bot.add_cog(TetrisCog(bot))
