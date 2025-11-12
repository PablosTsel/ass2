#!/usr/bin/env python3
"""
Benchmark test for Sudoku solver performance
Tests realistic puzzles and measures performance
"""

import time
from encoder import to_cnf
from solver import solve_cnf

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def benchmark_4x4():
    """Benchmark on 4x4 puzzle"""
    print("Testing 4x4 Sudoku with non-consecutive constraint...")

    # Create a solvable 4x4 puzzle with strategic clues
    with open('bench_4x4.txt', 'w') as f:
        f.write("1 3 0 0\n")
        f.write("0 0 0 0\n")
        f.write("0 0 0 0\n")
        f.write("0 0 0 0\n")

    start = time.time()
    clauses, num_vars = to_cnf('bench_4x4.txt')
    encode_time = time.time() - start

    clauses_list = list(clauses)
    print(f"  Encoding time: {encode_time*1000:.2f}ms")
    print(f"  Variables: {num_vars}")
    print(f"  Clauses: {len(clauses_list)}")

    start = time.time()
    status, model = solve_cnf(clauses_list, num_vars)
    solve_time = time.time() - start

    print(f"  Solving time: {solve_time*1000:.2f}ms")
    print(f"  Result: {status}")
    print(f"  Total time: {(encode_time + solve_time)*1000:.2f}ms")

    return status, encode_time + solve_time

def benchmark_9x9():
    """Benchmark on 9x9 puzzle"""
    print("\nTesting 9x9 Sudoku with non-consecutive constraint...")

    # Create a 9x9 puzzle with some clues
    with open('bench_9x9.txt', 'w') as f:
        f.write("5 3 0 0 7 0 0 0 0\n")
        f.write("6 0 0 1 9 5 0 0 0\n")
        f.write("0 9 8 0 0 0 0 6 0\n")
        f.write("8 0 0 0 6 0 0 0 3\n")
        f.write("4 0 0 8 0 3 0 0 1\n")
        f.write("7 0 0 0 2 0 0 0 6\n")
        f.write("0 6 0 0 0 0 2 8 0\n")
        f.write("0 0 0 4 1 9 0 0 5\n")
        f.write("0 0 0 0 8 0 0 7 9\n")

    start = time.time()
    clauses, num_vars = to_cnf('bench_9x9.txt')
    encode_time = time.time() - start

    clauses_list = list(clauses)
    print(f"  Encoding time: {encode_time*1000:.2f}ms")
    print(f"  Variables: {num_vars}")
    print(f"  Clauses: {len(clauses_list)}")

    start = time.time()
    status, model = solve_cnf(clauses_list, num_vars)
    solve_time = time.time() - start

    print(f"  Solving time: {solve_time*1000:.2f}ms")
    print(f"  Result: {status}")
    print(f"  Total time: {(encode_time + solve_time)*1000:.2f}ms")

    return status, encode_time + solve_time

def analyze_encoding():
    """Analyze the encoding complexity"""
    print("\nEncoding Complexity Analysis:")
    print("-" * 70)

    sizes = [(4, "4x4"), (9, "9x9"), (16, "16x16")]

    for N, name in sizes:
        # Calculate theoretical number of clauses
        cells = N * N
        values = N

        # Constraint counts
        cell_clauses = cells * (1 + (values * (values - 1)) // 2)  # exactly-one per cell
        row_clauses = N * values * (1 + (N * (N - 1)) // 2)  # exactly-one per row
        col_clauses = N * values * (1 + (N * (N - 1)) // 2)  # exactly-one per col
        box_clauses = N * values * (1 + (N * (N - 1)) // 2)  # exactly-one per box

        # Non-consecutive (2 clauses per edge per value pair)
        edges = 2 * N * (N - 1)  # horizontal + vertical edges
        non_consec_clauses = edges * 2 * (values - 1)

        total_clauses = cell_clauses + row_clauses + col_clauses + box_clauses + non_consec_clauses
        total_vars = N * N * N

        print(f"\n{name} grid:")
        print(f"  Variables: {total_vars}")
        print(f"  Estimated clauses: ~{total_clauses:,}")
        print(f"    - Cell constraints: {cell_clauses:,}")
        print(f"    - Row constraints: {row_clauses:,}")
        print(f"    - Column constraints: {col_clauses:,}")
        print(f"    - Box constraints: {box_clauses:,}")
        print(f"    - Non-consecutive: {non_consec_clauses:,}")

def main():
    print_header("SAT SOLVER BENCHMARK SUITE")

    # Analyze encoding complexity
    analyze_encoding()

    print_header("PERFORMANCE BENCHMARKS")

    # Run benchmarks
    results = []

    # 4x4 test
    status_4x4, time_4x4 = benchmark_4x4()
    results.append(("4x4", status_4x4, time_4x4))

    # 9x9 test
    status_9x9, time_9x9 = benchmark_9x9()
    results.append(("9x9", status_9x9, time_9x9))

    # Summary
    print_header("BENCHMARK SUMMARY")

    print("Size  | Result | Time")
    print("-" * 35)
    for size, status, elapsed in results:
        print(f"{size:5} | {status:6} | {elapsed*1000:8.2f}ms")

    print("\n" + "="*70)
    print("PERFORMANCE ASSESSMENT:")
    print("="*70)

    if time_4x4 < 1.0:
        print("✓ 4x4 puzzles: EXCELLENT (< 1s)")
    else:
        print("⚠ 4x4 puzzles: Needs optimization")

    if time_9x9 < 5.0:
        print("✓ 9x9 puzzles: EXCELLENT (< 5s)")
    elif time_9x9 < 30.0:
        print("✓ 9x9 puzzles: GOOD (< 30s)")
    else:
        print("⚠ 9x9 puzzles: May need optimization")

    print("\nNOTE: Non-consecutive constraint makes puzzles much harder!")
    print("Many puzzles may be UNSAT due to the constraint.")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
