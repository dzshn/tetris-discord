import dataclasses
import enum
import math
from random import SystemRandom
from typing import NamedTuple, Optional

import discord
import numpy as np
from numpy.typing import NDArray

from bot.lib.consts import SHAPES
from bot.lib.consts import SRS_I_KICKS
from bot.lib.consts import SRS_KICKS

Pieces = enum.Enum('PIECES', 'I L J S Z T O')
random = SystemRandom()


class Position(NamedTuple):
    x: int = 0
    y: int = 0

    def __add__(self, other: tuple) -> 'Position':
        if not isinstance(other, tuple):
            return NotImplemented

        x, y = other
        return Position(x=self.x + x, y=self.y + y)


@dataclasses.dataclass()
class Frame:
    pos: Position
    rot: int

    @property
    def x(self) -> int:
        return self.pos.x

    @property
    def y(self) -> int:
        return self.pos.y

    def __add__(self, other: 'Frame') -> 'FrameDelta':
        if not isinstance(other, Frame):
            return NotImplemented

        return FrameDelta(previous=self, current=other)


@dataclasses.dataclass()
class FrameDelta:
    previous: Frame
    current: Frame

    @property
    def x(self) -> int:
        return self.current.x - self.previous.x

    @property
    def y(self) -> int:
        return self.current.y - self.previous.y

    @property
    def rotation(self) -> int:
        return self.current.rot - self.previous.rot


class Piece:
    def __init__(self, board: NDArray[np.int8], t: int, x: int = 10, y: int = 3, r: int = 0):
        self.board = board
        self.type = t
        self.pos = Position(x, y)
        self._rot = r
        self.frame = Frame(pos=self.pos, rot=self.rot)
        self.delta = None

    def new_frame(self):
        new = Frame(pos=self.pos, rot=self.rot)
        if new != self.frame:
            self.delta = self.frame + Frame(pos=self.pos, rot=self.rot)
            self.frame = new

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

        self.pos = Position(target, self.y)
        self.new_frame()

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

        self.pos = Position(self.x, target)
        self.new_frame()

    @property
    def rot(self) -> int:
        return self._rot

    @rot.setter
    def rot(self, value: int):
        value %= 4
        previous = self._rot
        if Piece(self.board, self.type, self.x, self.y, value).overlaps():
            kick_table = SRS_I_KICKS if self.type == Pieces.I else SRS_KICKS
            for x, y in kick_table[previous][value]:
                if not Piece(self.board, self.type, self.x + x, self.y + y, value).overlaps():
                    self.pos = Position(self.x + x, self.y + y)
                    break
            else:
                return

        self._rot = value
        self.new_frame()

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
            other_pos = other

        elif isinstance(other, Piece):
            other_pos = other.pos

        else:
            return NotImplemented

        x, y = self.pos + other_pos

        return Piece(self.board, self.type, x, y, self.rot)


class Queue:
    def __init__(self, initial_queue: list[int] = [], initial_bag: list[int] = []):
        self._queue = initial_queue[:4]
        self._bag = initial_bag
        for _ in range(4):
            if len(self._queue) < 4:
                self._queue.append(self._next_piece())

    def _next_piece(self) -> int:
        if not self._bag:
            self._bag = [i.value for i in Pieces]
            random.shuffle(self._bag)

        return self._bag.pop()

    @property
    def next_pieces(self) -> list[int]:
        return self._queue.copy()

    @property
    def current_bag(self) -> list[int]:
        return self._bag.copy()

    def pop(self) -> int:
        piece = self._queue.pop(0)
        self._queue.append(self._next_piece())
        return piece


class Game:
    def __init__(self, config: dict, user_settings: dict):
        self.emotes = config['skins'][user_settings.get('skin', 0)]['pieces']
        self.queue = Queue()
        self.board = np.zeros((30, 10), dtype=np.int8)
        self.current_piece = Piece(self.board, self.queue.pop())
        self.score = 0
        self.hold: Optional[int] = None
        self.hold_lock = False
        self.previous_score = 0
        self.combo = 0
        self.b2b = 0
        self.action_text: Optional[str] = None
        self.can_pc = False

    def reset(self):
        self.queue = Queue()
        self.board = np.zeros((30, 10), dtype=np.int8)
        self.current_piece = Piece(self.board, self.queue.pop())
        self.previous_score = self.score
        self.hold = None
        self.hold_lock = False
        self.combo = 0
        self.b2b = 0
        self.action_text: str = None
        self.can_pc = False

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

            if corners >= 3 and self.current_piece.delta.rotation:
                tspin = True
                front_corner_offsets = [
                    ((x, x), (y, y + 2)),          # ▒▒██▒▒ <- these corners
                    ((x, x + 2), (y + 2, y + 2)),  # ██████
                    ((x + 2, x + 2), (y, y + 2)),
                    ((x, x + 2), (y, y))
                ]  # yapf: disable

                # Only is a mini if a front corner isn't present and it wasn't a X -> +2 kick
                mini_spin = not np.all(
                    self.board[front_corner_offsets[self.current_piece.rot]] != 0
                ) and self.current_piece.delta.x < 2

        line_clears = 0
        for row, clear in enumerate(self.board.all(1)):
            if clear:
                self.board[row] = 0
                self.board = np.concatenate(
                    (np.roll(self.board[:row + 1], shift=1, axis=0), self.board[row + 1:])
                )
                line_clears += 1

        if tspin:
            if mini_spin:
                self.action_text = ['Mini T-Spin', 'Mini T-Spin Single', 'Mini T-Spin Double'][line_clears]
                self.score += [100, 200, 400][line_clears]
                if self.b2b > 1:
                    self.score += [0, 100, 200][line_clears]
            else:
                self.action_text = ['T-Spin', 'T-Spin Single', 'T-Spin Double', 'T-Spin Triple'][line_clears]
                self.score += [400, 800, 1200, 1600][line_clears]
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

        for sx, sy in self.current_piece.shape + self.current_piece.pos:
            if sx < 10:
                self.reset()
                self.action_text = 'Top out!'

        self.current_piece = Piece(self.board, self.queue.pop())
        self.hold_lock = False

        if self.current_piece.overlaps():
            self.reset()
            self.action_text = 'Block out!'

    def get_board_text(self) -> str:
        board = self.board.copy()
        piece = self.current_piece
        ghost = piece.copy()
        ghost.x += 30
        for sx, sy in ghost.shape + ghost.pos:
            board[sx, sy] = 9

        for sx, sy in piece.shape + piece.pos:
            board[sx, sy] = piece.type

        return '\n'.join(''.join(self.emotes[j] for j in i) for i in board[14:])

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(
            color=0xfa50a0, title=self.action_text or discord.Embed.Empty, description=self.get_board_text()
        )
        embed.add_field(
            name='Hold', value=f'`{Pieces(self.hold).name}`' if self.hold is not None else '`None`'
        )
        embed.add_field(name='Queue', value=', '.join(f'`{Pieces(i).name}`' for i in self.queue.next_pieces))
        embed.add_field(name='Score', value=f'**{self.score:,}**\n+{self.score - self.previous_score}')
        return embed

    def drop(self, height: int):
        self.current_piece.x += height

    def hard_drop(self):
        self.current_piece.x += 30
        self.previous_score = self.score
        self.score += self.current_piece.delta.x * 2
        self.lock_piece()

    def soft_drop(self):
        self.drop(5)
        self.score += self.current_piece.delta.x

    def swap(self):
        if self.hold is None:
            self.hold = self.current_piece.type
            self.current_piece = Piece(self.board, self.queue.pop())

        else:
            self.hold, self.current_piece = self.current_piece.type, Piece(self.board, self.hold)

        self.hold_lock = True

    def rotate(self, turns: int):
        self.current_piece.rot += turns

    def drag(self, dist: int):
        self.current_piece.y += dist

    def to_save(self):
        return NotImplemented
