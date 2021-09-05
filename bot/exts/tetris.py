import enum
import itertools
import random

import discord
import numpy as np
from discord.ext import commands

Pieces = enum.Enum('PIECES', 'I L J S Z T O')
EMOTES = [
    '<:BG:883851510319026177>', '<:I_:883851823616766002>', '<:L_:883851571857854524>',
    '<:J_:883851652547891210>', '<:S_:883852392460845076>', '<:Z_:883852343442034749>',
    '<:T_:883852443044184145>', '<:O_:883852312462913556>', '<:GA:883951745309483079>',
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


class Game:
    def __init__(self):
        self.board = np.zeros((30, 10), dtype=int)
        self._queue = self._queue_iter()
        self.current_piece = (next(self._queue), 10, 3, 0)
        self.queue = list(itertools.islice(self._queue, 4))
        self.hold = None

    def _queue_iter(self) -> int:
        current_bag = []
        while True:
            if not current_bag:
                current_bag = [i.value for i in Pieces]
                random.shuffle(current_bag)

            yield current_bag.pop()

    def get_text(self):
        board = self.board.copy()
        piece, x, y, rot = self.current_piece
        for i in range(x, 30):
            for sx, sy in SHAPES[piece - 1][rot]:
                if i + sx >= 30 or board[i + sx, y + sy]:
                    ghx = i - 1
                    break

        for sx, sy in SHAPES[piece - 1][rot]:
            board[ghx + sx, y + sy] = 9

        for sx, sy in SHAPES[piece - 1][rot]:
            board[x + sx, y + sy] = piece

        return '\n'.join(''.join(EMOTES[j] for j in i) for i in board[14:])


class Controls(discord.ui.View):
    def __init__(self, game: Game, message: discord.Message):
        super().__init__()
        self.game = game
        self.message = message

    @discord.ui.button(label='\u200c', disabled=True, row=0)
    async def _0(self, *_):
        pass

    @discord.ui.button(label='⇊', style=discord.ButtonStyle.primary, row=0)
    async def hard_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        piece, x, y, rot = self.game.current_piece
        for i in range(x, 30):
            for sx, sy in SHAPES[piece - 1][rot]:
                if i + sx >= 30 or self.game.board[i + sx, y + sy]:
                    x = i - 1
                    break

        for sx, sy, in SHAPES[piece - 1][rot]:
            self.game.board[x + sx, y + sy] = piece

        self.game.current_piece = (self.game.queue.pop(0), 10, 3, 0)
        self.game.queue.append(next(self.game._queue))
        await self.update_message()

    @discord.ui.button(label='\u200c', disabled=True, row=0)
    async def _1(self, *_):
        pass

    @discord.ui.button(label='⤭', style=discord.ButtonStyle.primary, row=0)
    async def swap(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.game.hold is None:
            self.game.hold = self.game.current_piece[0]
            self.game.current_piece = (self.game.queue.pop(0), 10, 3, 0)
            self.game.queue.append(next(self.game._queue))

        else:
            self.game.hold, self.game.current_piece = self.game.current_piece[0], (self.game.hold, 10, 3, 0)

        button.disabled = True
        await self.update_message()

    @discord.ui.button(label='🗘', style=discord.ButtonStyle.primary, row=0)
    async def rotate_cw2(self, button: discord.ui.Button, interaction: discord.Interaction):
        p, x, y, r = self.game.current_piece
        r += 2
        if r > 3:
            r -= 4
        self.game.current_piece = (p, x, y, r)
        await self.update_message()

    @discord.ui.button(label='🡸', style=discord.ButtonStyle.primary, row=1)
    async def move_left(self, button: discord.ui.Button, interaction: discord.Interaction):
        p, x, y, r = self.game.current_piece
        y -= 1
        self.game.current_piece = (p, x, y, r)
        await self.update_message()

    @discord.ui.button(label='🡻', style=discord.ButtonStyle.primary, row=1)
    async def soft_drop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.update_message()

    @discord.ui.button(label='🡺', style=discord.ButtonStyle.primary, row=1)
    async def move_right(self, button: discord.ui.Button, interaction: discord.Interaction):
        p, x, y, r = self.game.current_piece
        y += 1
        self.game.current_piece = (p, x, y, r)
        await self.update_message()

    @discord.ui.button(label='↺', style=discord.ButtonStyle.primary, row=1)
    async def rotate_ccw(self, button: discord.ui.Button, interaction: discord.Interaction):
        p, x, y, r = self.game.current_piece
        r -= 1
        if r < 0:
            r = 3
        self.game.current_piece = (p, x, y, r)
        await self.update_message()

    @discord.ui.button(label='↻', style=discord.ButtonStyle.primary, row=1)
    async def rotate_cw(self, button: discord.ui.Button, interaction: discord.Interaction):
        p, x, y, r = self.game.current_piece
        r += 1
        if r > 3:
            r = 0
        self.game.current_piece = (p, x, y, r)
        await self.update_message()

    async def update_message(self):
        embed = discord.Embed(color=0xfa50a0, description=self.game.get_text())
        embed.add_field(
            name='Hold', value=Pieces(self.game.hold).name if self.game.hold is not None else 'None'
        )
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in self.game.queue))
        await self.message.edit(embed=embed, view=self)


class TetrisCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def zen(self, ctx: commands.Context):
        game = Game()
        embed = discord.Embed(color=0xfa50a0, description=game.get_text())
        embed.add_field(name='Hold', value='None')
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in game.queue))
        msg = await ctx.send('\u200c')
        view = Controls(game, msg)
        await msg.edit(embed=embed, view=view)


def setup(bot: commands.Bot):
    bot.add_cog(TetrisCog(bot))
