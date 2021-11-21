from dataclasses import dataclass
from typing import Optional

from bot.engine import BaseGame
from bot.engine import Piece
from bot.engine import PieceType


@dataclass(frozen=True)
class DeltaFrame:
    p_piece: Optional[Piece]
    c_piece: Piece

    def __post_init__(self):
        if self.p_piece is None:
            # HACK: yeah, this is a frozen object, shouldn't matter within here though
            #       equiv: `self.p_piece = Piece(board=self.c_piece.board.type=1)`
            object.__setattr__(self, 'p_piece', Piece(board=self.c_piece.board, type=1))

    @property
    def x(self) -> int:
        return self.c_piece.x - self.p_piece.x

    @property
    def y(self) -> int:
        return self.c_piece.y - self.p_piece.y

    @property
    def r(self) -> int:
        return (self.c_piece.r - self.p_piece.r) % 4


class Frameable(BaseGame):
    __slots__ = ('delta',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.delta = DeltaFrame(None, self.piece.copy())

    def move(self, x: int = 0, y: int = 0):
        p = self.piece.copy()
        super().move(x=x, y=y)
        c = self.piece.copy()

        self.delta = DeltaFrame(p, c)

    def rotate(self, turns: int):
        p = self.piece.copy()
        super().rotate(turns=turns)
        c = self.piece.copy()

        self.delta = DeltaFrame(p, c)


