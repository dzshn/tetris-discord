from dataclasses import dataclass

from engine import BaseGame
from engine import Piece
from engine import PieceType


@dataclass(frozen=True)
class DeltaFrame:
    p_piece: Piece | None
    c_piece: Piece

    def __post_init__(self):
        if self.p_piece is None:
            # HACK: yeah, this is a frozen object, shouldn't matter within here though
            #       equiv: `self.p_piece = Piece(board=self.c_piece.board, type=1)`
            object.__setattr__(
                self, 'p_piece', Piece(board=self.c_piece.board, type=1)  # type: ignore
            )

    @property
    def x(self) -> int:
        return self.c_piece.x - self.p_piece.x  # type: ignore

    @property
    def y(self) -> int:
        return self.c_piece.y - self.p_piece.y  # type: ignore

    @property
    def r(self) -> int:
        return (self.c_piece.r - self.p_piece.r) % 4  # type: ignore


class GameMixin:
    def __init__(self, **kwargs):
        BaseGame.__init__(self, **kwargs)


class Frameable(GameMixin):
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


class StandardScore(Frameable):
    '''Mixin implementing scoring based on the latest games.

    Conditions applied:  (where level == score_multiplier)

    | Condition                  | Score              | Back-to-Back? |
    | -------------------------- | ------------------ | ------------- |
    | Single                     | 100 * level        | No            |
    | Double                     | 300 * level        | No            |
    | Triple                     | 500 * level        | No            |
    | Tetris                     | 800 * level        | Yes           |
    | T-Spin Mini                | 100 * level        | -             |
    | T-Spin Mini Single         | 200 * level        | Yes           |
    | T-Spin Mini Double         | 400 * level        | Yes           |
    | T-Spin                     | 400 * level        | -             |
    | T-Spin Single              | 800 * level        | Yes           |
    | T-Spin Double              | 1200 * level       | Yes           |
    | T-Spin Triple              | 1600 * level       | Yes           |
    | Combo                      | 50 * combo * level | -             |
    | Soft drop                  | 1 * cell           | -             |
    | Hard drop                  | 2 * cell           | -             |
    | Back-to-Back clear         | score * 3 / 2      | -             |
    | Single Perfect-clear       | 800 * level        | -             |
    | Double Perfect-clear       | 1200 * level       | -             |
    | Triple Perfect-clear       | 1800 * level       | -             |
    | Tetris Perfect-clear       | 2000 * level       | -             |
    | Back-to-Back Perfect-clear | 3200 * level       | -             |

    Main source: <https://tetris.wiki/Scoring>
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.score_delta = 0
        self.score_multiplier = 1
        self.combo = 0
        self.back_to_back = 0

    def lock_piece(self):
        board = self.board.copy()
        piece = self.piece
        for x, y in piece.shape + piece.pos:
            board[x, y] = piece.type

        line_clears = sum(board.all(1))

        tspin = False
        tspin_mini = False
        if self.piece.type == PieceType.T and self.delta.r:
            x, y = piece.pos
            mx, my = board.shape

            # fmt: off
            # Find occupied corners, as well as account for board edges
            if x + 2 < mx and x + 2 < my:
                corners = sum(board[(x + 0, x + 2, x + 0, x + 2),
                                    (y + 0, y + 0, y + 2, y + 2)] != 0)
            elif x + 2 > mx and x + 2 < my:
                corners = sum(board[(x + 0, x + 0),
                                    (y + 0, y + 2)] != 0) + 2
            elif y + 2 < my and x + 1 > mx:
                corners = sum(board[(x + 0, x + 2),
                                    (y + 0, y + 0)] != 0) + 2

            if corners >= 3:
                tspin_mini = not (
                    board[[((y + 0, y + 2), (x + 0, x + 0)),
                           ((y + 2, y + 2), (x + 0, x + 2)),
                           ((y + 2, y + 0), (x + 2, x + 2)),
                           ((y + 0, y + 0), (x + 2, x + 0))][piece.r]] != 0
                ).all() and self.delta.x < 2

                tspin = not tspin_mini
            # fmt: on

        if line_clears:
            if tspin or tspin_mini or line_clears >= 4:
                self.back_to_back += 1
            else:
                self.back_to_back = 0
            self.combo += 1
        else:
            self.combo = 0

        # There are all blank lines, but also account for those that will be cleared later
        perfect_clear = not any((not row.all()) and row.any() for row in board)

        # Now actually calculate the score
        score_add = 0
        if perfect_clear:
            score_add += [0, 800, 1200, 1800, 2000][line_clears]
        elif tspin:
            score_add += [400, 800, 1200, 1600, 0][line_clears]
        elif tspin_mini:
            score_add += [100, 200, 400, 0, 0][line_clears]
        else:
            score_add += [0, 100, 300, 500, 800][line_clears]

        score_add += 50 * self.combo
        score_add *= self.score_multiplier

        if self.back_to_back > 1:
            score_add = score_add * 3 // 2
            if perfect_clear:
                # An odd edge-case but seems to be on games with per-line PC scores
                score_add += 200 * self.score_multiplier

        self.score += score_add
        self.score_delta = score_add

        super().lock_piece()

    def hard_drop(self):
        super().hard_drop()
        self.score += self.delta.x * 2

    def soft_drop(self):
        super().soft_drop()
        self.score += self.delta.x
