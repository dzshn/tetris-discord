import base64

import numpy as np
from numpy.typing import NDArray

from bot.engine import Piece


def encode(board: NDArray[np.int8], piece: Piece | None) -> bytes:
    board = board.copy()
    mx, my = board.shape
    if len(board.flat) % 2 != 0:
        board = np.concatenate(([0] * my, board), dtype=np.int8)

    for i, j in enumerate(board.any(axis=1)):
        if j:
            board = board[i:]
            break

    encoded = bytearray()
    encoded.append(mx)
    encoded.append(my)
    if piece is not None:
        encoded.extend([piece.type, piece.x, piece.y, piece.r])
    else:
        encoded.extend([0, 0, 0, 0])

    for a, b in board.reshape((len(board.flat) // 2, 2)):
        encoded.append((a << 4) + b)

    return encoded


def decode(encoded: bytes) -> tuple[NDArray[np.int8], Piece]:
    mx, my, pt, px, py, pr, *encoded = encoded
    decoded = []
    for i in encoded:
        decoded.extend([i >> 4, i - (i >> 4 << 4)])

    board = np.array(decoded, dtype=np.int8).reshape((-1, my))
    board = np.concatenate((np.zeros((mx - len(board), my), dtype=np.int8), board))
    if pt:
        piece = Piece(board, type=pt, x=px, y=py, r=pr)
    else:
        piece = None

    return (board, piece)


def encode_string(board: NDArray[np.int8], piece: Piece | None) -> str:
    return base64.b64encode(encode(board, piece)).decode()


def decode_string(encoded: str) -> tuple[NDArray[np.int8], Piece]:
    return decode(base64.b64decode(encoded.encode()))
