import base64
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from bot.lib.game import Piece


class Encoder:
    """Simple system to encode/decode a tetris board into a string.

    Currently, the format is simply:
        data         ::= board_data[~garbage_data]@[piece_data]
        board_data   ::= <base64 encoded cell pairs: [(piece_type << 4 + piece_type), ...]>
        garbage_data ::= <base64 encoded position pairs: [(y_pos << 4 + y_pos), ...]>
        piece_data   ::= type+x+y+rotation

    Where the encoded board data is reshaped from (N, 10) to (N / 2 * 10, 2)
    and vice-versa for decoding, each cell pair is bitshifted to the same byte
    And the garbage data decodes to a list of 1~10 numbers of where the holes
    are positioned + 1 and is 0 terminated for a odd number of garbage lines

    this format is max ~200 characters for up to 30 rows
    """
    @staticmethod
    def encode(board: NDArray[int], piece: Optional[Piece] = None) -> str:
        pairs = []
        for i, j in enumerate(board):
            if j.any():
                board = board[i:]
                break

        garbage = []
        garbage_pairs = []
        for i, j in enumerate(board):
            if 8 in j:
                for garbage_row in board[i:]:
                    if len(np.nonzero()[0].flat) != 1:
                        raise ValueError('Invalid garbage lines')

                    garbage.append(np.nonzero(garbage_row == 0)[0][0] + 1)

                if len(garbage) % 2 != 0:
                    garbage.append(0)

                board = board[:i]
                break

        for i, j in board.reshape(len(board.flat) // 2, 2):
            pairs.append((i << 4) + j)

        encoded = base64.b64encode(bytes(pairs)).decode()
        if garbage:
            for i, j in np.reshape(garbage, (len(garbage) // 2, 2)):
                garbage_pairs.append((i << 4) + j)

            encoded += '~' + base64.b64encode(bytes(garbage_pairs)).decode()

        encoded += '@'
        if piece is not None:
            encoded += f'{piece.type}+{piece.x}+{piece.y}+{piece.rot}'

        return encoded

    @staticmethod
    def decode(encoded: str) -> (NDArray[np.int8], Optional[Piece]):
        board, piece = encoded.split('@') if encoded[-1] != '@' else (encoded.rstrip('@'), None)
        if '~' in board:
            board, garbage = board.split('~')
        else:
            garbage: str = None

        flat_board = []
        for i in base64.b64decode(board):
            flat_board.append(i >> 4)
            flat_board.append(i - (i >> 4 << 4))
            if len(flat_board) >= 150:
                break

        board = np.array(flat_board, dtype=np.int8).reshape((-1, 10))
        if board.shape[0] < 30:
            board = np.concatenate((np.zeros((30 - board.shape[0], 10), dtype=np.int8), board))

        if piece is not None:
            piece = Piece(board, *map(int, piece.split('+')))

        if garbage is not None:
            for i in base64.b64decode(garbage):
                for j in (i >> 4, i - (i >> 4 << 4)):
                    if j == 0:
                        break
                    board = np.concatenate((board, [[8] * 10]))
                    board[-1, j - 1] = 0

        return board, piece
