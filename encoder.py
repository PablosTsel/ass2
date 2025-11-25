"""
SAT Assignment Part 1 - Non-consecutive Sudoku Encoder (Puzzle -> CNF)

THIS is the file to edit.

Implement: to_cnf(input_path) -> (clauses, num_vars)

You're required to use a variable mapping as follows:
    var(r,c,v) = r*N*N + c*N + v
where r,c are in range (0...N-1) and v in (1...N).

You must encode:
  (1) Exactly one value per cell
  (2) For each value v and each row r: exactly one column c has v
  (3) For each value v and each column c: exactly one row r has v
  (4) For each value v and each sqrt(N)×sqrt(N) box: exactly one cell has v
  (5) Non-consecutive: orthogonal neighbors cannot differ by 1
  (6) Clues: unit clauses for the given puzzle
"""

import math
from typing import Tuple, Iterable


def map_to_var(r, c, v, N):
    return r * N * N + c * N + v


def exactly_one(literals):
    clauses = []
    clauses.append(list(literals))  # At least one

    for i in range(len(literals)):
        for j in range(i + 1, len(literals)):
            clauses.append([-literals[i], -literals[j]])  # At most one

    return clauses


def to_cnf(input_path: str) -> Tuple[Iterable[Iterable[int]], int]:
    """
    Read puzzle from input_path and return (clauses, num_vars).


    - clauses: iterable of iterables of ints (each clause), no trailing 0s
    - num_vars: must be N^3 with N = grid size
    """
    grid = []
    clauses = []
    with open(input_path, "r") as f:
        for line in f:
            row = list(map(int, line.strip().split()))
            grid.append(row)
    N = len(grid)

    # (1) Exactly one value per cell
    for r in range(N):
        for c in range(N):
            literals = [map_to_var(r, c, v, N) for v in range(1, N + 1)]
            clauses.extend(exactly_one(literals))

    # (2)For each value v and each row r: exactly one column c has v
    for r in range(N):
        for v in range(1, N + 1):
            literals = [map_to_var(r, c, v, N) for c in range(N)]
            clauses.extend(exactly_one(literals))

    # (3) For each value v and each column c: exactly one row r has v
    for c in range(N):
        for v in range(1, N + 1):
            literals = [map_to_var(r, c, v, N) for r in range(N)]
            clauses.extend(exactly_one(literals))

    # (4) For each value v and each sqrt(N)×sqrt(N) box
    BoxSize = math.sqrt(N)
    for box_r in range(int(BoxSize)):
        for box_c in range(int(BoxSize)):
            for v in range(1, N + 1):
                literals = []
                for r in range(int(BoxSize)):
                    for c in range(int(BoxSize)):
                        literals.append(
                            map_to_var(
                                box_r * int(BoxSize) + r, box_c * int(BoxSize) + c, v, N
                            )
                        )
                clauses.extend(exactly_one(literals))

    # (5) Non-consecutive
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    for r in range(N):
        for c in range(N):
            for dr, dc in directions:
                r2, c2 = r + dr, c + dc
                if 0 <= r2 < N and 0 <= c2 < N:
                    for v in range(1, N):  # because v+1 must exist
                        # disallow (v, v+1)
                        clauses.append(
                            [-map_to_var(r, c, v, N), -map_to_var(r2, c2, v + 1, N)]
                        )
                        clauses.append(
                            [-map_to_var(r, c, v + 1, N), -map_to_var(r2, c2, v, N)]
                        )

    # (6) Clues
    for r in range(N):
        for c in range(N):
            v = grid[r][c]
            if v > 0:
                clauses.append([map_to_var(r, c, v, N)])  # unit clause

    num_vars = N * N * N
    return clauses, num_vars
