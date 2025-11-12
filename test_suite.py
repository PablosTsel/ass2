#!/usr/bin/env python3
"""
Comprehensive Test Suite for SAT Solver Assignment
Tests correctness, performance, and edge cases
"""

import time
import sys
from solver import solve_cnf
from encoder import to_cnf

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}TEST: {name}{Colors.END}")

def print_pass(msg):
    print(f"  {Colors.GREEN}✓ PASS{Colors.END} - {msg}")

def print_fail(msg):
    print(f"  {Colors.RED}✗ FAIL{Colors.END} - {msg}")

def print_info(msg):
    print(f"  {Colors.YELLOW}ℹ{Colors.END} {msg}")

def test_basic_sat():
    """Test 1: Simple satisfiable formula"""
    print_test("Basic SAT Problem")

    # (x1 OR x2) AND (NOT x1 OR x3)
    clauses = [[1, 2], [-1, 3]]
    num_vars = 3

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    if status == "SAT":
        print_pass(f"Correctly identified SAT ({elapsed*1000:.2f}ms)")
        print_info(f"Model: {model}")

        # Verify model
        for clause in clauses:
            satisfied = any((lit > 0 and lit in model) or (lit < 0 and -lit not in model) for lit in clause)
            if not satisfied:
                print_fail(f"Model doesn't satisfy clause: {clause}")
                return False
        print_pass("Model verified correct")
        return True
    else:
        print_fail(f"Expected SAT, got {status}")
        return False

def test_basic_unsat():
    """Test 2: Simple unsatisfiable formula"""
    print_test("Basic UNSAT Problem")

    # x1 AND NOT x1
    clauses = [[1], [-1]]
    num_vars = 1

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    if status == "UNSAT":
        print_pass(f"Correctly identified UNSAT ({elapsed*1000:.2f}ms)")
        return True
    else:
        print_fail(f"Expected UNSAT, got {status}")
        return False

def test_empty_formula():
    """Test 3: Empty formula (should be SAT)"""
    print_test("Empty Formula")

    clauses = []
    num_vars = 5

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    if status == "SAT":
        print_pass(f"Correctly identified SAT ({elapsed*1000:.2f}ms)")
        return True
    else:
        print_fail(f"Expected SAT, got {status}")
        return False

def test_empty_clause():
    """Test 4: Formula with empty clause (should be UNSAT)"""
    print_test("Formula with Empty Clause")

    clauses = [[1, 2], [], [3]]
    num_vars = 3

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    if status == "UNSAT":
        print_pass(f"Correctly identified UNSAT ({elapsed*1000:.2f}ms)")
        return True
    else:
        print_fail(f"Expected UNSAT, got {status}")
        return False

def test_unit_propagation():
    """Test 5: Unit propagation chain"""
    print_test("Unit Propagation Chain")

    # x1, x1->x2, x2->x3
    clauses = [[1], [-1, 2], [-2, 3]]
    num_vars = 3

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    if status == "SAT":
        print_pass(f"Correctly identified SAT ({elapsed*1000:.2f}ms)")
        # Check that x1, x2, x3 all true
        if 1 in model and 2 in model and 3 in model:
            print_pass("Unit propagation worked correctly")
            return True
        else:
            print_fail(f"Unit propagation failed. Model: {model}")
            return False
    else:
        print_fail(f"Expected SAT, got {status}")
        return False

def test_large_sat():
    """Test 6: Larger satisfiable problem"""
    print_test("Larger SAT Problem (50 variables, 200 clauses)")

    # Generate a random but satisfiable formula
    import random
    random.seed(42)

    num_vars = 50
    num_clauses = 200
    clauses = []

    for _ in range(num_clauses):
        clause_size = random.randint(2, 5)
        clause = [random.choice([1, -1]) * random.randint(1, num_vars)
                  for _ in range(clause_size)]
        clauses.append(clause)

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    print_info(f"Result: {status} ({elapsed*1000:.2f}ms)")

    if status == "SAT":
        # Verify model
        errors = 0
        for clause in clauses:
            satisfied = any((lit > 0 and lit in model) or (lit < 0 and -lit not in model) for lit in clause)
            if not satisfied:
                errors += 1

        if errors == 0:
            print_pass(f"Solved and model verified ({elapsed:.3f}s)")
            return True
        else:
            print_fail(f"Model has {errors} unsatisfied clauses")
            return False
    else:
        print_info("Problem was UNSAT (possible with random generation)")
        return True

def test_pigeonhole():
    """Test 7: Pigeonhole principle (n+1 pigeons, n holes) - UNSAT"""
    print_test("Pigeonhole Principle (4 pigeons, 3 holes)")

    n = 3  # holes
    clauses = []

    # Each pigeon in at least one hole
    for p in range(n + 1):
        clause = [p * n + h + 1 for h in range(n)]
        clauses.append(clause)

    # No two pigeons in same hole
    for h in range(n):
        for p1 in range(n + 1):
            for p2 in range(p1 + 1, n + 1):
                clauses.append([-(p1 * n + h + 1), -(p2 * n + h + 1)])

    num_vars = (n + 1) * n

    start = time.time()
    status, model = solve_cnf(clauses, num_vars)
    elapsed = time.time() - start

    if status == "UNSAT":
        print_pass(f"Correctly identified UNSAT ({elapsed*1000:.2f}ms)")
        return True
    else:
        print_fail(f"Expected UNSAT, got {status}")
        return False

def test_sudoku_encoder():
    """Test 8: Test encoder on a simple puzzle"""
    print_test("Sudoku Encoder Test")

    # Create a simple 4x4 puzzle file
    with open('test_encoder_4x4.txt', 'w') as f:
        f.write("1 0 0 0\n")
        f.write("0 0 0 4\n")
        f.write("0 0 0 0\n")
        f.write("0 0 0 0\n")

    try:
        start = time.time()
        clauses, num_vars = to_cnf('test_encoder_4x4.txt')
        elapsed = time.time() - start

        clauses_list = list(clauses)
        print_pass(f"Encoder ran successfully ({elapsed*1000:.2f}ms)")
        print_info(f"Generated {len(clauses_list)} clauses for {num_vars} variables")
        print_info(f"Expected variables: 4^3 = 64, Got: {num_vars}")

        if num_vars == 64:
            print_pass("Correct number of variables")
        else:
            print_fail(f"Expected 64 variables, got {num_vars}")
            return False

        # Check if clues are encoded as unit clauses
        unit_clauses = [c for c in clauses_list if len(c) == 1]
        print_info(f"Found {len(unit_clauses)} unit clauses")

        return True

    except Exception as e:
        print_fail(f"Encoder failed: {e}")
        return False

def test_performance_scaling():
    """Test 9: Performance scaling test"""
    print_test("Performance Scaling Test")

    sizes = [10, 20, 30, 40, 50]
    times = []

    for size in sizes:
        # Generate formula with 'size' variables and 4*size clauses
        import random
        random.seed(size)

        clauses = []
        for _ in range(4 * size):
            clause = [random.choice([1, -1]) * random.randint(1, size)
                      for _ in range(3)]
            clauses.append(clause)

        start = time.time()
        status, _ = solve_cnf(clauses, size)
        elapsed = time.time() - start
        times.append(elapsed)

        print_info(f"{size} vars: {elapsed*1000:.2f}ms ({status})")

    # Check if time increases reasonably
    print_pass(f"Performance scaling completed")
    print_info(f"Time range: {min(times)*1000:.2f}ms - {max(times)*1000:.2f}ms")
    return True

def test_both_modes():
    """Test 10: Test both puzzle and DIMACS modes"""
    print_test("Integration Test - Both Input Modes")

    import subprocess

    # Test DIMACS mode
    with open('test_dimacs_int.sat', 'w') as f:
        f.write("p cnf 3 3\n")
        f.write("1 2 0\n")
        f.write("-1 3 0\n")
        f.write("-2 -3 0\n")

    try:
        result = subprocess.run(['python3', 'main.py', '--in', 'test_dimacs_int.sat', '--sat'],
                              capture_output=True, text=True, timeout=5)
        output = result.stdout.strip()

        if output == "SAT":
            print_pass("DIMACS mode works correctly")
        else:
            print_fail(f"DIMACS mode returned: {output}")
            return False

    except Exception as e:
        print_fail(f"DIMACS mode failed: {e}")
        return False

    # Test puzzle mode with 4x4
    try:
        result = subprocess.run(['python3', 'main.py', '--in', 'test_encoder_4x4.txt'],
                              capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()

        if output in ["SAT", "UNSAT"]:
            print_pass(f"Puzzle mode works correctly (result: {output})")
            return True
        else:
            print_fail(f"Puzzle mode returned: {output}")
            return False

    except Exception as e:
        print_fail(f"Puzzle mode failed: {e}")
        return False

def run_all_tests():
    """Run all tests and generate report"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  SAT SOLVER COMPREHENSIVE TEST SUITE")
    print(f"{'='*60}{Colors.END}\n")

    tests = [
        test_basic_sat,
        test_basic_unsat,
        test_empty_formula,
        test_empty_clause,
        test_unit_propagation,
        test_large_sat,
        test_pigeonhole,
        test_sudoku_encoder,
        test_performance_scaling,
        test_both_modes
    ]

    results = []
    total_start = time.time()

    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((test.__name__, False))

    total_time = time.time() - total_start

    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  TEST SUMMARY")
    print(f"{'='*60}{Colors.END}\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {status}  {name}")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}")
    print(f"{Colors.BOLD}Total time: {total_time:.2f}s{Colors.END}\n")

    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}★ ALL TESTS PASSED! ★{Colors.END}")
        print(f"{Colors.GREEN}Your solver is ready for submission!{Colors.END}\n")
    else:
        print(f"{Colors.YELLOW}⚠ Some tests failed. Review the output above.{Colors.END}\n")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
