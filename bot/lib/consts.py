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
        [(+1, +0), (+1, -1), (+1, +1), (+0, -1), (+0, +1)],  # 2 -> 0  180
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
