import dataclasses
import enum
import math
import random
import secrets
from typing import NamedTuple, Optional, Union

import numpy as np
from numpy.typing import NDArray

from bot.lib.consts import SHAPES
from bot.lib.consts import SRS_I_KICKS
from bot.lib.consts import SRS_KICKS

PieceType = enum.IntEnum('PieceType', 'I L J S Z T O')

Seed = Union[str, bytes, int]
QueueSeq = list[PieceType]


class Position(NamedTuple):
    x: int = 0
    y: int = 0

    def __add__(self, other: tuple) -> 'Position':
        if isinstance(other, tuple):
            x, y = other
            return Position(x=self.x + x, y=self.y + y)

        return NotImplemented

    def __sub__(self, other: tuple) -> 'Position':
        if isinstance(other, tuple):
            x, y = other
            return Position(x=self.x - x, y=self.y - y)

        return NotImplemented


@dataclasses.dataclass
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
        if isinstance(other, Frame):
            return FrameDelta(self, other)

        return NotImplemented


@dataclasses.dataclass
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
    __slots__ = ('board', 'type', 'pos', '_rot', 'frame', 'delta')

    def __init__(
        self,
        board: NDArray[np.int8],
        t: PieceType,
        x: Optional[int] = None,
        y: Optional[int] = None,
        rot: int = 0
    ):
        self.board = board
        self.type = t
        if x is None and y is None:
            # e.g. for size (40, 10), align at (22, 3)
            self.pos = Position(board.shape[0] // 2 - 2, (board.shape[1] + 3) // 2 - 3)
        else:
            assert x is not None and y is not None, 'x, y should both be specified'
            self.pos = Position(x, y)

        self._rot = rot
        self.frame = Frame(pos=self.pos, rot=self.rot)
        self.delta = None

    def new_frame(self):
        new = Frame(pos=self.pos, rot=self.rot)
        if new != self.frame:
            self.delta = self.frame + new
            self.frame = new

    @property
    def x(self) -> int:
        return self.pos.x

    @x.setter
    def x(self, value: int):
        target = self.x
        # FIXME: using a for loop without proper var but
        #        incrementing `target` is redundant, same for `y.setter`
        step = int(math.copysign(1, value - self.x))
        for _ in range(abs(self.x - value)):
            if self.copy(x=target + step).overlaps():
                break

            target += step

        self.pos = Position(target, self.y)
        self.new_frame()

    @property
    def y(self) -> int:
        return self.pos.y

    @y.setter
    def y(self, value: int):
        target = self.y
        step = int(math.copysign(1, value - self.y))
        for _ in range(abs(self.y - value)):
            if self.copy(y=target + step).overlaps():
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
        if self.copy(rot=value).overlaps():
            kick_table = SRS_I_KICKS if self.type == PieceType.I else SRS_KICKS
            for x, y in kick_table[previous][value]:
                if not self.copy(x=self.x + x, y=self.y + y, rot=value).overlaps():
                    self.pos += (x, y)
                    break
            else:
                return

        self._rot = value
        self.new_frame()

    @property
    def shape(self) -> NDArray[np.int8]:
        return np.array(SHAPES[self.type - 1][self.rot], dtype=np.int8)

    def copy(self, **kwargs):
        kwargs = {
            'board': self.board,
            't': self.type,
            'x': self.x,
            'y': self.y,
            'rot': self.rot,
        } | kwargs
        return Piece(**kwargs)

    def overlaps(self) -> bool:
        board = self.board
        for x, y in self.shape + self.pos:
            if x not in range(board.shape[0]):
                return True
            if y not in range(board.shape[1]):
                return True
            if board[x, y]:
                return True
        return False


class Queue:
    __slots__ = ('_random', '_queue', '_bag')

    def __init__(self, /, queue: list[int], bag: list[int], seed: Seed):
        assert len(queue) == 4 or len(queue) == 0, 'invalid queue'
        assert len(bag) == len(set(bag)) < len(PieceType), 'invalid bag'

        self._random = random.Random(seed)
        self._queue = [PieceType(i) for i in queue]
        self._bag = [PieceType(i) for i in bag]
        for _ in range(4):
            if len(self._queue) > 4:
                break
            self._queue.append(self._next_piece())

    def _next_piece(self) -> PieceType:
        if not self._bag:
            self._bag = list(PieceType)
            self._random.shuffle(self._bag)

        return self._bag.pop()

    @property
    def pieces(self) -> QueueSeq:
        return self._queue.copy()

    @property
    def bag(self) -> QueueSeq:
        return self._bag.copy()

    def pop(self) -> PieceType:
        piece = self._queue.pop(0)
        self._queue.append(self._next_piece())
        return piece

    def __iter__(self):
        yield from self.pieces

    def __repr__(self):
        return f'Queue(queue={self.pieces}, bag={self.bag})'


class BaseGame:
    __slots__ = ('seed', 'queue', 'board', 'piece', 'hold', 'hold_lock')

    def __init__(self, **kwargs):
        self.seed = kwargs.get('seed') or secrets.token_bytes()
        self.queue = Queue(
            queue=kwargs.get('queue') or [], bag=kwargs.get('bag') or [], seed=self.seed
        )
        # XXX: Does this refactor actually work with other
        #      board sizes? that could be interesting
        self.board = np.zeros((40, 10), dtype=np.int8)
        self.piece = Piece(self.board, kwargs.get('piece') or self.queue.pop())
        self.hold: Optional[int] = None
        self.hold_lock = False

    # TODO: Make `self.piece` an property and implement
    #       the `on_frame` event there

    def reset(self):
        pass

    def lock_piece(self):
        piece = self.piece
        for x, y in piece.shape + piece.pos:
            self.board[x, y] = piece.type

        for row, clear in enumerate(self.board.all(1)):
            if clear:
                self.board[row] = 0
                self.board = np.concatenate(
                    (
                        np.roll(self.board[: row + 1], shift=1, axis=0),
                        self.board[row + 1 :],
                    )
                )

        for x, y in self.piece.shape + self.piece.pos:
            if x < 10:
                self.reset()
                break

        self.piece = Piece(self.board, self.queue.pop())

        if self.piece.overlaps():
            self.reset()

        self.hold_lock = False

    def render(self, tiles: list[str] = list(' ILJSZTOX@'), lines: int = 20) -> str:
        board = self.board.copy()
        ghost = self.piece.copy()
        ghost.x += 30
        for x, y in ghost.shape + ghost.pos:
            board[x, y] = 9

        for x, y in self.piece.shape + self.piece.pos:
            board[x, y] = self.piece.type

        return '\n'.join(''.join(tiles[j] for j in i) for i in board[-lines:])

    def swap(self):
        if self.hold is None:
            self.hold = self.piece.type
            self.piece = Piece(self.board, self.queue.pop())

        else:
            self.hold, self.piece = self.piece.type, Piece(self.board, self.hold)

        self.hold_lock = True
