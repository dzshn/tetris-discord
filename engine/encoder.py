import base64
import enum
from typing import NamedTuple

import numpy as np
from numpy.typing import NDArray

from engine import Piece


class EncoderFlag(enum.IntFlag):
    HAS_PIECE = 1 << 0
    # HAS_QUEUE = 1 << 1


class EncoderData(NamedTuple):
    board: NDArray[np.int8]
    piece: Piece | None
    # queue: list[PieceType] | None


def encode(
    board: NDArray[np.int8],
    piece: Piece | None = None,
    # queue: list[PieceType] | None = None,
) -> bytes:
    board = board.copy()
    mx, my = board.shape
    if len(board.flat) % 2 != 0:
        board = np.concatenate(([0] * my, board), dtype=np.int8)

    for i, j in enumerate(board.any(axis=1)):
        if j:
            board = board[i:]
            break

    flags = EncoderFlag(0)
    if piece is not None:
        flags = flags | EncoderFlag.HAS_PIECE

    encoded = bytearray([flags, mx, my])
    if piece is not None:
        encoded.extend([piece.type, piece.x, piece.y, piece.r])
    else:
        encoded.extend([0, 0, 0, 0])

    for a, b in board.reshape((len(board.flat) // 2, 2)):
        encoded.append((a << 4) + b)

    return bytes(encoded)


def decode(encoded: bytes) -> EncoderData:
    flags, mx, my, *encoded = encoded
    flags = EncoderFlag(flags)
    if flags.HAS_PIECE:
        pt, px, py, pr, *encoded = encoded

    decoded = []
    for i in encoded:
        decoded.extend([i >> 4, i - (i >> 4 << 4)])

    board = np.array(decoded, dtype=np.int8).reshape((-1, my))
    board = np.concatenate((np.zeros((mx - len(board), my), dtype=np.int8), board))
    if flags.HAS_PIECE:
        piece = Piece(board, type=pt, x=px, y=py, r=pr)
    else:
        piece = None

    return EncoderData(board=board, piece=piece)


def encode_string(*args, **kwargs) -> str:
    return base64.b64encode(encode(*args, **kwargs)).decode()


def decode_string(*args, **kwargs) -> EncoderData:
    return decode(base64.b64decode(*args, **kwargs))
