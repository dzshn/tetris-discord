import enum
import math
import random
import secrets
from typing import NamedTuple, TypeAlias

import numpy as np
from numpy.typing import NDArray

from engine.consts import SHAPES
from engine.consts import SRS_I_KICKS
from engine.consts import SRS_KICKS

Seed: TypeAlias = str | bytes | int
QueueSeq: TypeAlias = list['PieceType']

PieceType = enum.IntEnum('PieceType', 'I L J S Z T O')
Position = NamedTuple('Position', [('x', int), ('y', int)])


class Piece:
    __slots__ = ('board', 'type', 'pos', 'r')

    def __init__(
        self,
        board: NDArray[np.int8],
        type: PieceType,
        x: int | None = None,
        y: int | None = None,
        pos: int | None = None,
        r: int = 0,
    ):
        self.board = board
        self.type = type
        if pos is not None:
            self.pos = pos
        else:
            if x is None:
                x = board.shape[0] // 2 - 2
            if y is None:
                y = (board.shape[1] + 3) // 2 - 3

            self.pos = Position(x, y)

        self.r = r

    @property
    def x(self) -> int:
        return self.pos.x

    @x.setter
    def x(self, value: int):
        self.pos = Position(value, self.y)

    @property
    def y(self) -> int:
        return self.pos.y

    @y.setter
    def y(self, value: int):
        self.pos = Position(self.x, value)

    @property
    def shape(self) -> NDArray[np.int8]:
        return np.array(SHAPES[self.type - 1][self.r], dtype=np.int8)

    def copy(self, **kwargs) -> 'Piece':
        return Piece(
            board=self.board,
            type=self.type,
            x=kwargs.get('x', self.x),
            y=kwargs.get('y', self.y),
            r=kwargs.get('r', self.r),
        )

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
    def __init__(self, **kwargs):
        self.seed = kwargs.get('seed') or secrets.token_bytes()
        self.queue = Queue(
            queue=kwargs.get('queue') or [], bag=kwargs.get('bag') or [], seed=self.seed
        )
        self.board = np.zeros((40, 10), dtype=np.int8)
        self.piece = Piece(self.board, kwargs.get('piece') or self.queue.pop())
        self.hold: int | None = None
        self.hold_lock = False

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

        for ix in range(ghost.x, self.board.shape[0]):
            if ghost.copy(x=ix).overlaps():
                break
            ghost.x = ix

        for x, y in ghost.shape + ghost.pos:
            board[x, y] = 9

        for x, y in self.piece.shape + self.piece.pos:
            board[x, y] = self.piece.type

        return '\n'.join(''.join(tiles[j] for j in i) for i in board[-lines:])

    def swap(self):
        if self.hold_lock:
            return

        if self.hold is None:
            self.hold = self.piece.type
            self.piece = Piece(self.board, self.queue.pop())

        else:
            self.hold, self.piece = self.piece.type, Piece(self.board, self.hold)

        self.hold_lock = True

    def drag(self, x: int = 0, y: int = 0):
        self.move(self.piece.x + x, self.piece.y + y)

    def move(self, x: int = 0, y: int = 0):
        piece = self.piece
        new_x, new_y = from_x, from_y = piece.pos

        x_step = int(math.copysign(1, x - from_x))
        for ix in range(from_x, x + x_step, x_step):
            if piece.copy(x=ix).overlaps():
                break
            new_x = ix

        y_step = int(math.copysign(1, y - from_y))
        for iy in range(from_y, y + y_step, y_step):
            if piece.copy(y=iy).overlaps():
                break
            new_y = iy

        piece.pos = Position(new_x, new_y)

    def rotate(self, turns: int):
        piece = self.piece
        from_r = piece.r
        from_x, from_y = piece.pos
        new_r = (piece.r + turns) % 4

        kick_table = SRS_I_KICKS if piece.type == PieceType.I else SRS_KICKS
        kicks = [(+0, +0)] + kick_table[from_r][new_r]  # type: ignore

        for x, y in kicks:
            if not piece.copy(x=from_x + x, y=from_y + y, r=new_r).overlaps():
                piece.pos = Position(from_x + x, from_y + y)
                piece.r = new_r
                break

    def hard_drop(self):
        self.drag(x=self.board.shape[0])
        self.lock_piece()

    def soft_drop(self, height: int = 5):
        self.drag(x=height)
