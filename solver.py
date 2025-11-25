def solve_cnf(clauses, num_vars):
    """
        clauses: list of clauses, each clause is a list of ints
        num_vars: total number of variables

    Returns:
        ("SAT", model) where model is a list of ints,
        or ("UNSAT", None)
    """
    clauses = [list(c) for c in clauses]  # ensure normal lists

    assignment = dpll_iterative(clauses, num_vars)

    if assignment is None:
        return ("UNSAT", None)

    # Build DIMACS-style model from assignment dict
    model = []
    for v in range(1, num_vars + 1):
        val = assignment.get(v, False)
        model.append(v if val else -v)

    return ("SAT", model)


# Iterative DPLL with unit propagation and a simple branching heuristic
def dpll_iterative(clauses, num_vars):
    # Stack of partial assignments (DFS)
    stack = [dict()]

    while stack:
        assignment = stack.pop()

        # 1. Unit propagation on this assignment
        assignment = assignment.copy()  # work on our own copy
        if not unit_propagate(clauses, assignment):
            # Contradiction -> backtrack
            continue

        # 2. Check if all clauses are satisfied
        all_sat = True
        for clause in clauses:
            status = clause_status(clause, assignment)
            if status == "UNSAT":
                all_sat = False
                break
            if status != "SAT":
                all_sat = False

        if all_sat:
            return assignment

        # 3. Choose a branching literal from the shortest unsatisfied clause
        lit = choose_branch_literal(clauses, assignment)
        if lit is None:
            # Nothing left to branch on: treat as model
            return assignment

        var = abs(lit)
        prefer_true = lit > 0

        # 4. Push two branches: try preferred value first (so it is popped last)
        assign1 = assignment.copy()
        assign1[var] = prefer_true

        assign2 = assignment.copy()
        assign2[var] = not prefer_true

        # Stack is LIFO; we want assign1 explored first, so push assign2 then assign1
        stack.append(assign2)
        stack.append(assign1)

    # Explored all branches, no model found
    return None


def unit_propagate(clauses, assignment):
    changed = True
    while changed:
        changed = False
        for clause in clauses:
            status = clause_status(clause, assignment)
            if status == "UNSAT":
                return False
            if isinstance(status, tuple) and status[0] == "UNIT":
                lit = status[1]
                var = abs(lit)
                value = lit > 0

                if var in assignment:
                    if assignment[var] != value:
                        return False
                else:
                    assignment[var] = value
                    changed = True
                    # Restart scanning clauses with this new info
                    break
    return True


# Evaluate a single clause under the current assignment
def clause_status(clause, assignment):
    unassigned_lits = []

    for lit in clause:
        var = abs(lit)
        sign = lit > 0

        if var in assignment:
            if assignment[var] == sign:
                return "SAT"  # some literal is true
            # else this literal is false, check others
        else:
            unassigned_lits.append(lit)

    # No literal was true
    if not unassigned_lits:
        # All literals assigned and false
        return "UNSAT"

    if len(unassigned_lits) == 1:
        return ("UNIT", unassigned_lits[0])

    return "UNDEF"


# simple Moms Style Heuristic
def choose_branch_literal(clauses, assignment):
    # 1) Find the minimum length of any not-yet-satisfied clause
    min_len = None
    for clause in clauses:
        status = clause_status(clause, assignment)
        if status == "SAT":
            continue
        if status == "UNSAT":
            # contradiction will be handled elsewhere
            continue

        # collect unassigned literals in this clause
        unassigned = []
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                unassigned.append(lit)

        if not unassigned:
            continue

        length = len(unassigned)
        if min_len is None or length < min_len:
            min_len = length

    if min_len is None:
        # no clause to branch on -> treat as model or let caller handle
        return None

    # 2) Among clauses of that min length, count literal occurrences
    counts = {}  # lit -> frequency
    for clause in clauses:
        status = clause_status(clause, assignment)
        if status == "SAT":
            continue
        if status == "UNSAT":
            continue

        unassigned = []
        for lit in clause:
            var = abs(lit)
            if var not in assignment:
                unassigned.append(lit)

        if len(unassigned) != min_len:
            continue

        for lit in unassigned:
            counts[lit] = counts.get(lit, 0) + 1

    if not counts:
        return None

    # 3) Pick the literal with the highest count
    best_lit = max(counts, key=counts.get)
    return best_lit


# pick literal from shortest clause (not necessarily Moms)
# not as good as Moms (I think)
# def choose_branch_literal(clauses, assignment):
#     """
#     Pick a literal from the shortest clause that is not yet satisfied.
#     """
#     best_clause = None
#     best_len = None

#     for clause in clauses:
#         status = clause_status(clause, assignment)
#         if status == "SAT":
#             continue
#         if status == "UNSAT":
#             # Contradiction will be noticed elsewhere
#             continue

#         unassigned = []
#         for lit in clause:
#             var = abs(lit)
#             if var not in assignment:
#                 unassigned.append(lit)

#         if not unassigned:
#             continue

#         if best_clause is None or len(unassigned) < best_len:
#             best_clause = unassigned
#             best_len = len(unassigned)

#     if best_clause is None:
#         return None

#     return best_clause[0]
