"""
cdcl_solver.py

This module implements the Conflict-Driven Clause Learning (CDCL) SAT solver algorithm,
building upon the DPLL algorithm. CDCL enhances the base DPLL by adding:
- Conflict analysis and clause learning for resolving conflicts.
- Non-chronological backtracking to improve efficiency.
- Use of an implication graph to manage dependencies between variable assignments.
"""
from pydantic import Field
from typing import Dict, List, Optional, Tuple, Literal
from .dpll_solver import DPLLSolver
from sat_solver.Loggers.graph_step_logger import GraphStepLogger

class CDCLSolver(DPLLSolver):
    """
    A class implementing the CDCL (Conflict-Driven Clause Learning) SAT solver algorithm, with features such as:
    - Support for various branching heuristics (e.g., DLCS, DLIS, MOMS).
    - Optimizations like Two Watched Literals (TWL).
    - Detailed logging of decision steps.

     Attributes:
        implication_graph (Dict[int, Dict[str, Optional[int]]): Tracks implications and decision levels.
        learned_clauses (List[List[int]]): List of learned clauses during the solving process.
        graph_step_logger (GraphStepLogger): Logger for the CDCL solving process.
        cutting_method (str): The method used to cut the learned clause (e.g., 1UIP, LUIP).

    Inherited Attributes from DPLLSolver:
        clauses_model (ClausesModel): The clauses model to be solved.
        problem (SATProblem): The SAT problem to be solved.
        use_logger (bool): Whether to log steps during the solving process.
        step_logger (StepLogger): A logger to track the solving process.
        decision_level (int): The current decision depth level.
        heuristic (str): The branching heuristic to use ('default', 'dlcs', 'dlis', 'rdlcs', 'rdlis', 'moms', 'rmoms').
        heuristic_function (Callable): The branching heuristic function to select decision literals.
        heuristic_name (str): The name of the heuristic currently in use.
        k (int): The value of k for the MOM's heuristic.
        twl (bool): Whether to use Two Watched Literals optimization.
        true_twl (bool): Whether to use True Two Watched Literals optimization (If a literal that is not watched becames True, 
            the clause is not satisfied).

    Methods:
        _analyze_conflict (conflict_clause: List[int]) -> Tuple[List[int], int]:
            Analyze the conflict clause to find the 1-UIP (Unique Implication Point).
        _backtrack (level: int) -> None:
            Backtrack to the specified decision level.
        print_implication_graph() -> None:
            Print the logged implication graph.
        get_graph_steps() -> List[dict]:
            Retrieves the logged implication graph steps from the solving process.

    Overrides:
        _unit_propagation_loop() -> Optional[List[int]]:
            Perform unit propagation using the implication graph.
        _make_decision() -> None:
            Make a new decision by selecting a branching literal and incrementing the decision level.
        solve() -> bool:
            Solve the SAT problem using the CDCL algorithm.

    Inherited Methods from DPLLSolver:
        initialize_computed_fields(values: Dict[str, any]) -> Dict[str, any]:
            Initializes computed fields like the heuristic function, problem type (SATProblem, TWLSATProblem, or TrueTWLSATProblem),
            and validates parameters.
        _unit_propagation() -> Tuple[bool, int, int]:
            Performs unit propagation on the current formula to simplify the problem.
        _choose_decision_literal() -> int:
            Chooses a literal for branching (currently a placeholder for future implementation).
        print_steps() -> None:
            Prints the logged decision steps in a tabular format.
        get_decision_steps() -> List[dict]:
            Retrieves the logged decision steps from the solving process.
    """

    implication_graph: Dict[int, Dict[str, Optional[int]]] = Field(default_factory=dict, title="Tracks implications and decision levels.")
    learned_clauses: List[List[int]] = Field(default_factory=list, title="List of learned clauses during the solving process.")
    graph_step_logger: GraphStepLogger = Field(default_factory=GraphStepLogger, title="Logger for the CDCL solving process.") 
    cutting_method: Literal['1UIP', 'LUIP'] = Field(default="1UIP", description="The method used to cut the learned clause (e.g., 1UIP, LUIP).")
    
    def _unit_propagation_loop(self) -> Optional[List[int]]:
        """
        Perform unit propagation using the implication graph.

        Returns:
            Optional[List[int]]: The conflict clause if a conflict is found, otherwise None.
        """
        while True:
            propagation_occurred, implied_literal, affected_clause = self._unit_propagation()
            if not propagation_occurred:
                break

            # Add implied literal to implication graph
            self.implication_graph[implied_literal] = {
                "decision_level": self.decision_level,
                "antecedent": affected_clause
            }

            self.problem.update_satisfaction_map(operation='new assignment', literal_to_assign=implied_literal) # Update satisfaction map
            if self.use_logger:
                self.step_logger.log_step(problem=self.problem, decision_level= self.decision_level, implied_literal=implied_literal, explanation="BCP " + str(affected_clause))
                self.graph_step_logger.log_step(decision_level=self.decision_level, decision_literal=None, implied_literal=implied_literal, implication_graph=self.implication_graph.copy(), learned_clause=None, cutting_method="1UIP")

            # Check for conflicts
            if self.problem.is_unsatisfiable():
                contradicted_clauses = self.problem.get_contradicited_clauses().copy().pop()
                if (not self.twl) and (not self.true_twl): 
                    return self.problem.clauses[contradicted_clauses]
                else:
                    return self.problem.original_clauses[contradicted_clauses]
        return None

    def _analyze_conflict(self, conflict_clause: List[int]) -> Tuple[List[int], int]:
        """
        Analyze the conflict clause to find the 1-UIP (Unique Implication Point).

        Args:
            conflict_clause (List[int]): The clause causing the conflict.

        Returns:
            Tuple[List[int], int]: The learned clause and the backtrack level.
        """
        learned_clause = set(conflict_clause)  # Start with the conflict clause
        seen_literals = set()  # Track seen literals to avoid infinite loops
        decision_level_literals: List[int] = []

        # Traverse the implication graph to find 1-UIP
        for literal in conflict_clause:
            info = self.implication_graph.get(-literal, {})
            if info.get("decision_level") == self.decision_level:
                decision_level_literals.append(literal)

        # Ensure 1-UIP
        while len(decision_level_literals) > 1:
            lit_to_remove = decision_level_literals.pop()
            if self.implication_graph[-lit_to_remove]["antecedent"] is None:
                new_decision_level_literals: List[int] = []
                new_decision_level_literals.append(lit_to_remove)
                for lit in decision_level_literals:
                    new_decision_level_literals.append(lit)
                decision_level_literals = new_decision_level_literals
                continue
            if (not self.twl) and (not self.true_twl):
                antecedent_clause = set(self.problem.clauses[self.implication_graph[-lit_to_remove]["antecedent"]])
                # keep only the literals that are not in seen_literals
                antecedent_clause = {lit for lit in antecedent_clause if abs(lit) not in seen_literals}
            else:
                antecedent_clause = set(self.problem.original_clauses[self.implication_graph[-lit_to_remove]["antecedent"]])
                # keep only the literals that are not in seen_literals
                antecedent_clause = {lit for lit in antecedent_clause if abs(lit) not in seen_literals}
            if antecedent_clause is not None:
                learned_clause.update(antecedent_clause)
                learned_clause.discard(-lit_to_remove)
                learned_clause.discard(lit_to_remove)
                seen_literals.add(abs(lit_to_remove))

            # Update decision level literals
            decision_level_literals = [
                lit for lit in learned_clause
                if self.implication_graph.get(-lit, {}).get("decision_level") == self.decision_level
            ]

        # Calculate the backtrack level
        backtrack_level = max(
            (self.implication_graph.get(-lit, {}).get("decision_level", 0)
             for lit in learned_clause if lit not in decision_level_literals),
            default=0
        )

        if self.use_logger:
            self.graph_step_logger.log_step(decision_level=self.decision_level, implication_graph=self.implication_graph.copy(), learned_clause=list(learned_clause), backtrack_level=backtrack_level, cutting_method="1UIP")

        return list(learned_clause), backtrack_level

    def _backtrack(self, level: int) -> None:
        """
        Backtrack to the specified decision level.

        Args:
            level (int): The decision level to backtrack to.
        """
        # Remove assignments and implications above the specified level
        for literal, info in list(self.implication_graph.items()):
            if info["decision_level"] > level:
                var = abs(literal)
                if var in self.problem.assignments:
                    del self.problem.assignments[var]
                    self.problem.update_satisfaction_map(operation='undo assignment', literals_to_unassign=[literal])
                del self.implication_graph[literal]
        self.decision_level = level

    def _make_decision(self) -> None:
        """
        Make a new decision by selecting a branching literal and incrementing the decision level.
        """
        decision_literal, abs_value = self._choose_decision_literal()
        self.problem.assignments[abs_value] = decision_literal > 0
        self.problem.update_satisfaction_map(operation='new assignment', literal_to_assign=decision_literal)
        self.implication_graph[decision_literal] = {
            "decision_level": self.decision_level,
            "antecedent": None
        }
        if self.use_logger:
            self.step_logger.log_step(problem=self.problem, decision_level= self.decision_level, decision_literal=(decision_literal), explanation="INC_DL " + self.heuristic_name)
            self.graph_step_logger.log_step(decision_level=self.decision_level, decision_literal=decision_literal, implied_literal=None, implication_graph=self.implication_graph.copy(), learned_clause=None, cutting_method="1UIP")

    def solve(self) -> bool:
        """
        Solve the SAT problem using the CDCL algorithm.

        Returns:
            bool: True if satisfiable, False otherwise.
        """
        while True:
            conflict_clause = self._unit_propagation_loop()
            if conflict_clause:
                if self.decision_level == 0:
                    return False  # Unsatisfiable
                learned_clause, backtrack_level = self._analyze_conflict(conflict_clause)
                self.learned_clauses.append(learned_clause)
                # self.problem.add_clause(learned_clause)  # Add learned clause to problem
                self._backtrack(backtrack_level)
                self.problem.add_clause(learned_clause)  # Add learned clause to problem
            elif self.problem.is_satisfied():
                return True  # Satisfiable
            else:
                self._make_decision()

    def print_implication_graph(self) -> None:
        """
        Print the logged implication graph.
        """
        self.graph_step_logger.print_step()

    def get_graph_steps(self) -> List[dict]:
        """
        Retrieves the logged implication graph steps from the solving process.

        Returns:
            List[dict]: The logged implication graph steps.
        """
        return self.graph_step_logger.steps
    