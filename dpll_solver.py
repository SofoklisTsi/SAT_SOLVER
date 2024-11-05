from sat_problem import SATProblem

class DPLLSolver:
    """
    This class implements the DPLL (Davis-Putnam-Logemann-Loveland) SAT solver algorithm.
    
    Attributes:
        problem (SATProblem): The SAT problem to be solved.
        use_pure_literal (bool): Whether to use pure literal elimination.
        steps (list of dict): A list of dictionaries to log the steps of the solving process.
        decision_level (int): The current decision depth level.
    
    Methods:
        unit_propagation(): Perform unit propagation on the current formula.
        pure_literal_elimination(): Perform pure literal elimination on the current formula.
        choose_literal(): Choose a literal for branching.
        log_step(): Log the current state in the DPLL decision process.
        dpll_recursive_with_logging(): Recursive DPLL algorithm with logging at each step.
        solve(): The main DPLL solving function.
        print_steps(): Print the logged decision steps.
        get_decision_steps(): Retrieve the logged decision steps.
    """

    def __init__(self, problem, use_pure_literal=False):
        """
        Initialize the solver with a SATProblem instance.

        Args:
            problem (SATProblem): The SAT problem to be solved.
            use_pure_literal (bool): Whether to use pure literal elimination.

        Raises:
            TypeError: If `problem` is not an instance of SATProblem.
        """
        if not isinstance(problem, SATProblem):
            raise TypeError("problem must be an instance of SATProblem")
        self.problem = problem
        self.use_pure_literal = use_pure_literal
        self.steps = []  # Initialize an empty list for logging steps
        self.decision_level = 0  # Track the decision depth level
    
    def unit_propagation(self):
        """
        Perform unit propagation: If a clause becomes a unit clause (only one literal unassigned),
        assign that literal accordingly.
        
        Returns:
            tuple: (bool, int, int) - True if no conflicts, False if conflict occurred, 
                   the propagated literal, and the affected clause.
        """
        for i, clause in enumerate(self.problem.clauses):
            if not self.problem.satisfaction_map[i] and len([lit for lit in clause if abs(lit) not in self.problem.assignments]) == 1:
                # Identify the unit literal and propagate it
                unit_literal = next(lit for lit in clause if abs(lit) not in self.problem.assignments)
                var = abs(unit_literal)
                value = unit_literal > 0
                self.problem.assignments[var] = value
                self.problem.update_satisfaction_map()
                return True, unit_literal, i
        return False, None, None  # No unit clause found

    def pure_literal_elimination(self):
        """
        Perform pure literal elimination: If a literal appears only as positive or negative in the formula,
        assign it accordingly. For all pure literals.

        Returns:
            tuple: (bool, list) - True if any pure literals were eliminated, and a list of affected literals.
        """
        # Track if any changes occurred and the affected literals
        changed = False
        affected_literals = []

        # Gather all literals by their polarities
        literal_counts = {}
        
        for i, clause in enumerate(self.problem.clauses):
            if self.problem.satisfaction_map[i]:
                continue  # Skip already satisfied clauses

            for lit in clause:
                var = abs(lit)
                if var not in literal_counts:
                    literal_counts[var] = {1: 0, -1: 0}
                literal_counts[var][1 if lit > 0 else -1] += 1

        # Assign pure literals and update satisfaction
        for var, count in literal_counts.items():
            if count[1] > 0 and count[-1] == 0:
                # Pure positive literal
                self.problem.assignments[var] = True
                changed = True
                affected_literals.append(var)
            elif count[-1] > 0 and count[1] == 0:
                # Pure negative literal
                self.problem.assignments[var] = False
                changed = True
                affected_literals.append(-var)
        return changed, affected_literals

    def choose_literal(self):
        """
        Choose a literal from the formula for branching.
        
        Returns:
            int: The literal to branch on.
        """
        # Literal selection logic to be implemented here.
        pass
 
    def log_step(self, decision_literal=None, implied_literal=None, explanation=""):
        """
        Log the current state in the DPLL decision process.
        
        Args:
            decision_literal (int): The decision literal at the current step.
            implied_literal (int): The implied literal from unit propagation.
            explanation (str): Explanation of the current action.
        """
        # Partial assignment
        partial_assignment = "{" + ", ".join(str(var if value else -var) for var, value in self.problem.assignments.items()) + "}"
        
        # Satisfied and contradicted clauses
        satisfied_clauses = [i for i, satisfied in enumerate(self.problem.satisfaction_map) if satisfied]
        contradicted_clauses = [
            i for i, clause in enumerate(self.problem.clauses)
            if len([lit for lit in clause if abs(lit) not in self.problem.assignments]) == 0 
            and not self.problem.satisfaction_map[i]]
        
        # Unit clauses and pending clauses
        unit_clauses = [
            i for i, clause in enumerate(self.problem.clauses) 
            if len([lit for lit in clause if abs(lit) not in self.problem.assignments]) == 1 
            and not self.problem.satisfaction_map[i]]
        pending_clauses = [
            i for i, clause in enumerate(self.problem.clauses) 
            if len([lit for lit in clause if abs(lit) not in self.problem.assignments]) > 1 
            and not self.problem.satisfaction_map[i]]
        
        # Log entry
        self.steps.append({
            "Decision Level": self.decision_level,
            "Partial Assignment": partial_assignment,
            "Decision Literal": decision_literal,
            "Implied Literal": implied_literal,
            "Satisfied Clauses": satisfied_clauses,
            "Contradicted Clauses": contradicted_clauses,
            "Unit Clauses": unit_clauses,
            "Pending Clauses": pending_clauses,
            "Explanation": explanation
        })

    def dpll_recursive_with_logging(self):
        """
        Recursive DPLL algorithm with logging at each step.
        
        Returns:
            bool: True if the formula is satisfiable, False otherwise.
        """
        # Base cases
        if self.problem.is_satisfied():
            return True
        if self.problem.is_unsatisfiable():
            return False

        # Unit propagation loop - log each step and track assignments for backtracking
        propagated_literals = []  # Store implied literals to backtrack them later
        while True:
            propagation_occurred, implied_literal, affected_clause = self.unit_propagation()
            if not propagation_occurred:
                break
            propagated_literals.append(implied_literal)  # Track each implied literal
            self.log_step(implied_literal=implied_literal, explanation="BCP " + str(affected_clause))
            if self.problem.is_satisfied():
                return True
            if self.problem.is_unsatisfiable():
                # Backtrack unit propagation assignments if a conflict is found
                for lit in propagated_literals:
                    del self.problem.assignments[abs(lit)]
                return False

        # Choose a literal for branching and increment decision level
        unassigned_literals = [lit for i, clause in enumerate(self.problem.clauses) for lit in clause if abs(lit) not in self.problem.assignments
                               and not self.problem.satisfaction_map[i]]
        if not unassigned_literals:
            return self.problem.is_satisfied()

        # Increment decision level and assign the decision literal
        decision_literal = unassigned_literals[0]
        var = abs(decision_literal)
        self.decision_level += 1  # Increment decision level

        # Try assigning True to the literal
        self.problem.assignments[var] = True
        self.problem.update_satisfaction_map()
        self.log_step(decision_literal=(var), explanation="INC_DL")
        if self.dpll_recursive_with_logging():
            return True

        # Backtrack and try assigning False
        self.problem.assignments[var] = False
        self.problem.update_satisfaction_map()
        self.log_step(decision_literal=(-var), explanation="INC_DL")
        if self.dpll_recursive_with_logging():
            return True

        # Undo assignment and backtrack decision level if both branches fail
        del self.problem.assignments[var]
        for lit in propagated_literals:
            del self.problem.assignments[abs(lit)]
        self.problem.update_satisfaction_map()
        self.decision_level -= 1
        return False
    
    def solve(self):
        """
        Solve the SAT problem using the DPLL algorithm.

        Returns:
            bool: Satisfiability result (True if satisfiable, False otherwise).
        """
        if self.use_pure_literal:
            while True:
                elimination_occurred, affected_literals = self.pure_literal_elimination()
                if not elimination_occurred:
                    break
                self.problem.update_satisfaction_map()
                self.log_step(explanation="PLE " + ", ".join(str(lit) for lit in affected_literals))

        satisfiable = self.dpll_recursive_with_logging()
        return satisfiable
    
    def print_steps(self, table_format=True):
        """
        Print the logged decision steps.

        Args:
            table_format (bool): Whether to print the steps in a table format.
        """
        if table_format:
            # Print header row and title
            print("\nDecision Table:")
            header = [
                "DL", "Partial Assignment", "DLit", "IL",
                "Satisfied Clauses", "Contradicted Clauses", "Unit Clauses", "Pending Clauses", "Explanation"
            ]
            print("{:<3} {:<25} {:<5} {:<5} {:<25} {:<20} {:<25} {:<25} {:<20}".format(*header))

            # Print each step in a single row
            for step in self.steps:
                row = [
                    step["Decision Level"],
                    step["Partial Assignment"],
                    str(step["Decision Literal"]),
                    str(step["Implied Literal"]),
                    str(step["Satisfied Clauses"]),
                    str(step["Contradicted Clauses"]),
                    str(step["Unit Clauses"]),
                    str(step["Pending Clauses"]),
                    step["Explanation"]
                ]
                print("{:<3} {:<25} {:<5} {:<5} {:<25} {:<20} {:<25} {:<25} {:<20}".format(*row))

    def get_decision_steps(self):
        """
        Retrieve the decision steps logged during solving.

        Returns:
            list: The list of decision steps (each step is a dictionary).
        """
        return self.steps

