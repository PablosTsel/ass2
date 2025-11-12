"""
From SAT Assignment Part 1 - Non-consecutive Sudoku Encoder (Puzzle -> CNF)

Encodes non-consecutive Sudoku puzzles to CNF format.

Variable mapping: var(r,c,v) = r*N*N + c*N + v
where r,c are in range (0...N-1) and v in (1...N).

Constraints encoded:
  (1) Exactly one value per cell
  (2) For each value v and each row r: exactly one column c has v
  (3) For each value v and each column c: exactly one row r has v
  (4) For each value v and each sqrt(N)×sqrt(N) box: exactly one cell has v
  (5) Non-consecutive: orthogonal neighbors cannot differ by 1
  (6) Clues: unit clauses for the given puzzle
"""

from typing import Tuple, Iterable, List
import math


def var(r: int, c: int, v: int, N: int) -> int:
    """
    Convert (row, col, value) to variable number.
    r, c in [0, N-1], v in [1, N]
    Returns: variable number (1-indexed)
    """
    return r * N * N + c * N + v


def at_most_one_pairwise(literals: List[int]) -> List[List[int]]:
    """
    Generate pairwise encoding for at-most-one constraint.
    For each pair of literals, add clause: -lit1 OR -lit2
    """
    clauses = []
    for i in range(len(literals)):
        for j in range(i + 1, len(literals)):
            clauses.append([-literals[i], -literals[j]])
    return clauses


def exactly_one(literals: List[int]) -> List[List[int]]:
    """
    Generate clauses for exactly-one constraint.
    At least one: lit1 OR lit2 OR ... OR litn
    At most one: pairwise constraints
    """
    clauses = []
    # At least one
    clauses.append(literals[:])
    # At most one (pairwise)
    clauses.extend(at_most_one_pairwise(literals))
    return clauses


def to_cnf(input_path: str) -> Tuple[Iterable[Iterable[int]], int]:
    """
    Read puzzle from input_path and return (clauses, num_vars).

    - clauses: iterable of iterables of ints (each clause), no trailing 0s
    - num_vars: must be N^3 with N = grid size
    """
    # Read puzzle file
    with open(input_path, 'r') as f:
        lines = f.readlines()

    # Parse grid
    grid = []
    for line in lines:
        line = line.strip()
        if line:
            row = [int(x) for x in line.split()]
            grid.append(row)

    N = len(grid)
    num_vars = N * N * N

    # Validate grid
    if not all(len(row) == N for row in grid):
        raise ValueError("Grid must be square (N x N)")

    # Calculate box size
    box_size = int(math.sqrt(N))
    if box_size * box_size != N:
        raise ValueError(f"Grid size {N} must be a perfect square")

    clauses = []

    # (1) Exactly one value per cell
    for r in range(N):
        for c in range(N):
            literals = [var(r, c, v, N) for v in range(1, N + 1)]
            clauses.extend(exactly_one(literals))

    # (2) Each value appears exactly once per row
    for r in range(N):
        for v in range(1, N + 1):
            literals = [var(r, c, v, N) for c in range(N)]
            clauses.extend(exactly_one(literals))

    # (3) Each value appears exactly once per column
    for c in range(N):
        for v in range(1, N + 1):
            literals = [var(r, c, v, N) for r in range(N)]
            clauses.extend(exactly_one(literals))

    # (4) Each value appears exactly once per box
    for box_row in range(box_size):
        for box_col in range(box_size):
            for v in range(1, N + 1):
                literals = []
                for r in range(box_row * box_size, (box_row + 1) * box_size):
                    for c in range(box_col * box_size, (box_col + 1) * box_size):
                        literals.append(var(r, c, v, N))
                clauses.extend(exactly_one(literals))

    # (5) Non-consecutive constraint: orthogonal neighbors cannot differ by 1
    # For each pair of orthogonally adjacent cells (r1,c1) and (r2,c2),
    # and for each value v in [1, N-1]:
    #   If (r1,c1) has value v, then (r2,c2) cannot have v+1
    #   If (r1,c1) has value v+1, then (r2,c2) cannot have v
    for r in range(N):
        for c in range(N):
            # Check right neighbor
            if c + 1 < N:
                for v in range(1, N):
                    # If (r,c) = v, then (r,c+1) != v+1
                    clauses.append([-var(r, c, v, N), -var(r, c + 1, v + 1, N)])
                    # If (r,c) = v+1, then (r,c+1) != v
                    clauses.append([-var(r, c, v + 1, N), -var(r, c + 1, v, N)])

            # Check bottom neighbor
            if r + 1 < N:
                for v in range(1, N):
                    # If (r,c) = v, then (r+1,c) != v+1
                    clauses.append([-var(r, c, v, N), -var(r + 1, c, v + 1, N)])
                    # If (r,c) = v+1, then (r+1,c) != v
                    clauses.append([-var(r, c, v + 1, N), -var(r + 1, c, v, N)])

    # (6) Clues: unit clauses for given values
    for r in range(N):
        for c in range(N):
            if grid[r][c] != 0:
                v = grid[r][c]
                # Add unit clause asserting this cell has this value
                clauses.append([var(r, c, v, N)])

    return clauses, num_vars
