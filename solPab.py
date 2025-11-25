"""
SAT Assignment Part 2 - Non-consecutive Sudoku Solver (Puzzle -> SAT/UNSAT)

Implementation of a DPLL-based SAT solver with optimizations:
- Two-watched literals for efficient unit propagation
- VSIDS branching heuristic
- Iterative approach to avoid recursion limits
"""

from typing import Iterable, List, Tuple, Optional, Set
from collections import defaultdict, deque


class SATSolver:
    """
    DPLL-based SAT solver with two-watched literals and VSIDS heuristic.
    """

    def __init__(self, clauses: Iterable[Iterable[int]], num_vars: int):
        self.num_vars = num_vars

        # Convert clauses to lists and store
        self.clauses = [list(c) for c in clauses]
        self.num_clauses = len(self.clauses)

        # Assignment: None = unassigned, True = positive, False = negative
        self.assignment = [None] * (num_vars + 1)

        # Watch lists: literal -> list of clause indices watching this literal
        # For each clause, we watch exactly 2 literals (or 1 for unit clauses)
        self.watch_list = defaultdict(list)

        # For each clause, track which two literals are being watched
        self.watched = {}  # clause_id -> [lit1, lit2] or [lit1]

        # Decision stack for backtracking: [(var, value, decision_level)]
        self.decision_stack = []
        self.decision_level = 0

        # Propagation queue for unit propagation
        self.propagation_queue = deque()

        # VSIDS heuristic: activity scores for variables
        self.activity = [0.0] * (num_vars + 1)
        self.activity_increment = 1.0
        self.activity_decay = 0.95

        # Track which clauses are satisfied (for efficiency)
        self.satisfied_clauses = set()

        # Initialize watches for all clauses
        self._initialize_watches()

    def _initialize_watches(self):
        """Set up initial watch literals for all clauses."""
        for clause_idx, clause in enumerate(self.clauses):
            if len(clause) == 0:
                # Empty clause - immediately UNSAT
                continue
            elif len(clause) == 1:
                # Unit clause - watch the single literal
                lit = clause[0]
                self.watch_list[lit].append(clause_idx)
                self.watched[clause_idx] = [lit]
                # Add to propagation queue
                self.propagation_queue.append(lit)
            else:
                # Watch first two literals
                lit1, lit2 = clause[0], clause[1]
                self.watch_list[lit1].append(clause_idx)
                self.watch_list[lit2].append(clause_idx)
                self.watched[clause_idx] = [lit1, lit2]

    def _is_clause_satisfied(self, clause_idx: int) -> bool:
        """Check if a clause is satisfied by current assignment."""
        if clause_idx in self.satisfied_clauses:
            return True

        clause = self.clauses[clause_idx]
        for lit in clause:
            var = abs(lit)
            val = self.assignment[var]
            if val is not None and (val == (lit > 0)):
                self.satisfied_clauses.add(clause_idx)
                return True
        return False

    def _literal_value(self, lit: int) -> Optional[bool]:
        """Get the truth value of a literal under current assignment."""
        var = abs(lit)
        val = self.assignment[var]
        if val is None:
            return None
        return val if lit > 0 else not val

    def _assign(self, lit: int) -> bool:
        """
        Assign a literal to true.
        Returns False if this creates a conflict, True otherwise.
        """
        var = abs(lit)
        value = lit > 0

        # Check for conflict
        if self.assignment[var] is not None:
            if self.assignment[var] != value:
                return False  # Conflict!
            return True  # Already assigned consistently

        # Make assignment
        self.assignment[var] = value
        self.decision_stack.append((var, value, self.decision_level))

        return True

    def _update_watch(self, clause_idx: int, false_literal: int) -> bool:
        """
        Update watch for a clause when one of its watched literals becomes false.
        Returns False if conflict detected, True otherwise.
        """
        clause = self.clauses[clause_idx]
        watched = self.watched[clause_idx]

        # If clause already satisfied, nothing to do
        if self._is_clause_satisfied(clause_idx):
            return True

        # Find a new literal to watch (unassigned or true)
        for lit in clause:
            if lit == false_literal:
                continue

            # Check if this literal is already watched
            if lit in watched:
                continue

            lit_val = self._literal_value(lit)

            # Watch literals that are unassigned or true
            if lit_val is None or lit_val is True:
                # Replace the false watch with this new literal
                self.watch_list[false_literal].remove(clause_idx)
                self.watch_list[lit].append(clause_idx)

                # Update watched list
                watched_idx = watched.index(false_literal)
                watched[watched_idx] = lit

                return True

        # Couldn't find a new literal to watch
        # Check if this is a unit clause or conflict

        # Find the other watched literal(s)
        other_lits = [lit for lit in watched if lit != false_literal]

        if not other_lits:
            # All literals are false - CONFLICT
            return False

        # Check if other watched literal is unassigned
        for lit in other_lits:
            lit_val = self._literal_value(lit)
            if lit_val is None:
                # Unit propagation - this literal must be true
                self.propagation_queue.append(lit)
                return True
            elif lit_val is True:
                # Other literal is true - clause satisfied
                self.satisfied_clauses.add(clause_idx)
                return True

        # All other literals are false - CONFLICT
        return False

    def _propagate(self) -> bool:
        """
        Perform Boolean Constraint Propagation (unit propagation).
        Returns False if conflict detected, True otherwise.
        """
        while self.propagation_queue:
            lit = self.propagation_queue.popleft()

            # Assign this literal
            if not self._assign(lit):
                return False  # Conflict during assignment

            # Check all clauses watching the negation of this literal
            neg_lit = -lit

            # Make a copy of the watch list since it may be modified
            watching_clauses = self.watch_list[neg_lit][:]

            for clause_idx in watching_clauses:
                if not self._update_watch(clause_idx, neg_lit):
                    return False  # Conflict detected

        return True

    def _all_vars_assigned(self) -> bool:
        """Check if all variables are assigned."""
        for i in range(1, self.num_vars + 1):
            if self.assignment[i] is None:
                return False
        return True

    def _select_variable_vsids(self) -> Optional[int]:
        """Select an unassigned variable using VSIDS heuristic."""
        best_var = None
        best_activity = -1.0

        for var in range(1, self.num_vars + 1):
            if self.assignment[var] is None:
                if self.activity[var] > best_activity:
                    best_activity = self.activity[var]
                    best_var = var

        return best_var

    def _select_variable_dlis(self) -> Optional[int]:
        """Select variable using DLIS (Dynamic Largest Individual Sum) heuristic."""
        literal_count = defaultdict(int)

        for clause_idx, clause in enumerate(self.clauses):
            # Skip satisfied clauses
            if self._is_clause_satisfied(clause_idx):
                continue

            for lit in clause:
                var = abs(lit)
                if self.assignment[var] is None:
                    literal_count[lit] += 1

        if not literal_count:
            return None

        # Return the variable (not literal) with highest count
        best_lit = max(literal_count.items(), key=lambda x: x[1])[0]
        return abs(best_lit)

    def _bump_activity(self, var: int):
        """Increase activity score for a variable (VSIDS)."""
        self.activity[var] += self.activity_increment

        # Rescale if necessary to prevent overflow
        if self.activity[var] > 1e100:
            for i in range(len(self.activity)):
                self.activity[i] *= 1e-100
            self.activity_increment *= 1e-100

    def _decay_activities(self):
        """Decay activity increment (VSIDS)."""
        self.activity_increment /= self.activity_decay

    def _backtrack(self, target_level: int):
        """Backtrack to a specific decision level."""
        while self.decision_stack and self.decision_stack[-1][2] > target_level:
            var, _, _ = self.decision_stack.pop()
            self.assignment[var] = None

        self.decision_level = target_level

        # Clear satisfied clauses cache
        self.satisfied_clauses.clear()

    def _extract_model(self) -> List[int]:
        """Extract a DIMACS-format model from current assignment."""
        model = []
        for var in range(1, self.num_vars + 1):
            if self.assignment[var] is True:
                model.append(var)
            elif self.assignment[var] is False:
                model.append(-var)
            else:
                # Unassigned - can assign arbitrarily, choose positive
                model.append(var)
        return model

    def solve(self) -> Tuple[str, Optional[List[int]]]:
        """
        Main DPLL solver using iterative approach.
        Returns ("SAT", model) or ("UNSAT", None).
        """
        # Initial unit propagation
        if not self._propagate():
            return ("UNSAT", None)

        # Check if already satisfied
        if self._all_vars_assigned():
            return ("SAT", self._extract_model())

        # Iterative DPLL with explicit stack
        # Stack contains: (decision_literal, tried_negative)
        search_stack = []

        while True:
            # Try to propagate
            if not self._propagate():
                # Conflict - backtrack
                if not search_stack:
                    return ("UNSAT", None)

                # Backtrack to last decision
                while search_stack:
                    decision_lit, tried_negative = search_stack.pop()
                    decision_var = abs(decision_lit)
                    decision_level = len(search_stack)

                    # Backtrack to this level
                    self._backtrack(decision_level)
                    self.propagation_queue.clear()

                    if not tried_negative:
                        # Try the opposite value
                        search_stack.append((decision_lit, True))
                        self.decision_level = len(search_stack)
                        self.propagation_queue.append(-decision_lit)
                        break

                if not search_stack:
                    return ("UNSAT", None)

                continue

            # Check if all variables assigned (SAT)
            if self._all_vars_assigned():
                return ("SAT", self._extract_model())

            # Make a decision
            var = self._select_variable_dlis()
            if var is None:
                # No unassigned variables but not all assigned? Should not happen
                return ("SAT", self._extract_model())

            # Choose positive polarity first
            self.decision_level = len(search_stack) + 1
            search_stack.append((var, False))
            self.propagation_queue.append(var)


def solve_cnf(clauses: Iterable[Iterable[int]], num_vars: int) -> Tuple[str, List[int] | None]:
    """
    Solve a CNF formula.

    Args:
        clauses: Iterable of clauses, each clause is an iterable of ints
        num_vars: Total number of variables

    Returns:
        ("SAT", model) where model is a list of ints (DIMACS-style), or
        ("UNSAT", None)
    """
    # Handle edge cases
    clauses_list = list(clauses)

    # Check for empty formula
    if not clauses_list:
        # Empty formula is satisfiable
        model = list(range(1, num_vars + 1))
        return ("SAT", model)

    # Check for empty clause
    for clause in clauses_list:
        if len(list(clause)) == 0:
            return ("UNSAT", None)

    # Create solver and solve
    solver = SATSolver(clauses_list, num_vars)
    return solver.solve()
