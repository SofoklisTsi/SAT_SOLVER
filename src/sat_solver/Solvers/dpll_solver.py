"""
dpll_solver.py

This module implements the DPLL (Davis-Putnam-Logemann-Loveland) SAT solver algorithm, which is enhanced with various optimizations such as:
- Branching heuristics for variable selection (including DLCS, DLIS, and MOM's heuristics).
- Two Watched Literals (TWL) optimization.
- Support for logging the decision process step-by-step.

The `DPLLSolver` class is the core solver that applies the DPLL algorithm, allowing users to solve SAT problems using different heuristics and optimizations.
"""

from pydantic import BaseModel, Field, model_validator
from typing import Callable, Dict, List, Literal, Optional, Tuple
from sat_solver.Loggers.step_logger import StepLogger
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel
from sat_solver.SATProblems.sat_problem import SATProblem
from sat_solver.SATProblems.twl_sat_problem import TWLSATProblem
from sat_solver.SATProblems.true_twl_sat_problem import TrueTWLSATProblem
from sat_solver.Heuristics.literal_count_branching_heuristics import dlcs, dlis, rdlcs, rdlis, default_heuristic
from sat_solver.Heuristics.moms_branching_heuristics import moms, rmoms

class DPLLSolver(BaseModel):
    """
    A class implementing the DPLL (Davis-Putnam-Logemann-Loveland) SAT solver algorithm, with features such as:
    - Support for various branching heuristics (e.g., DLCS, DLIS, MOMS).
    - Optimizations like Two Watched Literals (TWL).
    - Detailed logging of decision steps.

    Attributes:
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
        initialize_computed_fields(values: Dict[str, any]) -> Dict[str, any]:
            Initializes computed fields like the heuristic function, problem type (SATProblem, TWLSATProblem, or TrueTWLSATProblem),
            and validates parameters.
        _unit_propagation() -> Tuple[bool, int, int]:
            Performs unit propagation on the current formula to simplify the problem.
        _unit_propagation_loop() -> Tuple[Optional[bool], Optional[List[int]]]:
            Performs unit propagation loop to simplify the formula and track assignments for backtracking.
        _choose_decision_literal() -> int:
            Chooses a literal for branching (currently a placeholder for future implementation).
        _make_decision(decision_literal: int, var: int, first_branch: bool) -> None:
            Assigns a literal to the formula and updates the satisfaction map.
        _undo_assignments(decision_literal: int, var: int, propagated_literals: List[int]) -> None:
            Undoes the assignment of the decision literal and any propagated literals.
        _dpll_recursive() -> bool:
            Recursively solves the SAT problem using the DPLL algorithm.
        solve() -> bool:
            The main method to solve the SAT problem.
        print_steps() -> None:
            Prints the logged decision steps in a tabular format.
        get_decision_steps() -> List[dict]:
            Retrieves the logged decision steps from the solving process.
    """
    clauses_model: ClausesModel = Field(..., title="The clauses model to be solved.")
    problem: SATProblem = Field(..., title="The SAT problem to be solved.")
    use_logger: bool = Field(default=False, title="Whether to log steps during the solving process.")
    step_logger: StepLogger = Field(default_factory=StepLogger, title="A logger to track the solving process.")
    decision_level: int = Field(default=0, title="The current decision depth level.")
    heuristic: Literal['default', 'dlcs', 'dlis', 'rdlcs', 'rdlis', 'moms', 'rmoms'] = Field(default="default", description="Branching heuristic to use.")
    heuristic_function: Callable = Field(default=default_heuristic, title="The branching heuristic function used to select decision literals.")
    heuristic_name: str = Field(default='default', title="The name of the current heuristic being used.")
    k: int = Field(default=0, title="The value of k for the MOM's heuristic.")
    twl: bool = Field(default=False, title="Whether to use Two Watched Literals optimization.")
    true_twl: bool = Field(default=False, title="Whether to use True Two Watched Literals optimization.")

    @model_validator(mode='before')
    @classmethod
    def initialize_computed_fields(cls, values: Dict[str, any]) -> Dict[str, any]:
        """
        Perform initial validation and compute derived attributes before constructing the model.

        This method initializes the fields based on the provided `values`, including:
        - Setting the `problem` attribute to the correct type (`SATProblem`, `TWLSATProblem`, or `TrueTWLSATProblem`).
        - Mapping the provided heuristic string to the corresponding heuristic function.

        Args:
            values (Dict[str, any]): The field values to initialize.

        Returns:
            Dict[str, any]: Updated field values after initialization.

        Raises:
            - `TypeError`: If the `clauses_model` field is not an instance of `ClausesModel`.
                - This is raised when the `clauses_model` provided is not of the expected type, which is necessary to solve the SAT problem.
            - `ValueError`: If the provided heuristic is not one of the recognized values (`'default'`, `'dlcs'`, `'dlis'`, `'rdlcs'`, `'rdlis'`, `'moms'`, `'rmoms'`).
                - This is raised when the `heuristic` field contains an unsupported value, preventing the selection of an unknown heuristic.
        """
        clauses_model = values['clauses_model']
        if not isinstance(clauses_model, ClausesModel):
            raise TypeError(f"Expected an instance of ClausesModel, but got {type(clauses_model)}")
        
        # Initialize the problem based on twl/true_twl settings
        if values.get('twl'):
            values['problem'] = TWLSATProblem(clauses_model=clauses_model)
        elif values.get('true_twl'):
            values['problem'] = TrueTWLSATProblem(clauses_model=clauses_model)
        else:
            values['problem'] = SATProblem(clauses_model=clauses_model)

        # Map heuristic names to functions
        heuristic_map = {
            'default': default_heuristic,
            'dlcs': dlcs,
            'dlis': dlis,
            'rdlcs': rdlcs,
            'rdlis': rdlis,
            'moms': lambda problem: moms(problem, k=values.get('k', 0)),
            'rmoms': lambda problem: rmoms(problem, k=values.get('k', 0))
        }
        heuristic = values.get('heuristic', 'default')
        if heuristic not in heuristic_map:
            raise ValueError(f"Unknown heuristic '{heuristic}'. Must be one of {list(heuristic_map.keys())}.")
        
        values['heuristic_function'] = heuristic_map[heuristic]
        values['heuristic_name'] = heuristic

        # Update heuristic name for twl/true_twl
        if values.get('twl'):
            values['heuristic_name'] += ' twl'
        elif values.get('true_twl'):
            values['heuristic_name'] += ' true_twl'

        # Initialize the step logger if logging is enabled
        if values.get('use_logger'):
            values['step_logger'] = StepLogger()

        return values
    
    def _unit_propagation(self) -> Tuple[bool, int, int]: 
        """
        Perform unit propagation (also known as Boolean Constraint Propagation - BCP):
        - If a clause becomes a unit clause (only one unassigned literal), assign that literal.

        Returns:
            tuple: (bool, int, int) -
                - True if propagation succeeded, False if a conflict occurred.
                - The propagated literal.
                - The index of the clause where propagation occurred.
        """
        if self.problem.get_unitary_clauses():
            for i in self.problem.get_unitary_clauses():
                # Identify the unit literal and propagate it
                unit_literal = next(lit for lit in self.problem.clauses[i] if abs(lit) not in self.problem.assignments)
                var = abs(unit_literal)
                value = unit_literal > 0
                self.problem.assignments[var] = value
                return True, unit_literal, i
        return False, None, None  # No unit clause found

    def _unit_propagation_loop(self) -> Tuple[Optional[bool], Optional[List[int]]]:
        """
        Perform unit propagation loop to simplify the formula and track assignments for backtracking.

        Returns:
            tuple: (Optional[bool], Optional[List[int]]) -
                - True if the formula is satisfiable, False if unsatisfiable, None if no conclusion.
                - A list of propagated literals to backtrack if needed.
        """
        # Unit propagation loop - log each step and track assignments for backtracking
        propagated_literals: List[int] = []  # Store implied literals to backtrack them later
        while True:
            propagation_occurred, implied_literal, affected_clause = self._unit_propagation()
            if not propagation_occurred:
                return None, propagated_literals
            propagated_literals.append(implied_literal)  # Track each implied literal
            self.problem.update_satisfaction_map(operation='new assignment', literal_to_assign=implied_literal) # Update satisfaction map
            if self.use_logger:
                self.step_logger.log_step(problem=self.problem, decision_level= self.decision_level, implied_literal=implied_literal, explanation="BCP " + str(affected_clause))
            if self.problem.is_satisfied():
                return True, None
            if self.problem.is_unsatisfiable():
                # Backtrack unit propagation assignments if a conflict is found
                for lit in propagated_literals:
                    del self.problem.assignments[abs(lit)]
                self.problem.update_satisfaction_map(operation='undo assignment', literals_to_unassign=propagated_literals)
                return False, None   

    def _choose_decision_literal(self) -> Tuple[int, int]:
        """
        Choose a literal from the formula for branching based on the branching heuristic and increment the decision level.
        
        Returns:
            tuple: (int, int) - The decision literal and its absolute value.
        """
        decision_literal = self.heuristic_function(self.problem)
        abs_value = abs(decision_literal)
        self.decision_level += 1  # Increment decision level
        return decision_literal, abs_value 
    
    def _make_decision(self, decision_literal: int, abs_value: int, first_branch: bool) -> None:
        """
        Make a decision by assigning a literal to the formula and updating the satisfaction map.

        Args:
            decision_literal (int): The literal to assign.
            var (int): The absolute value of the literal.
        """
        self.problem.assignments[abs_value] = True if decision_literal > 0 else False
        if first_branch:
            self.problem.update_satisfaction_map(operation='new assignment', literal_to_assign=decision_literal)
        else:
            self.problem.update_satisfaction_map(operation='change assignment', literal_to_assign=decision_literal)
        if self.use_logger:
            self.step_logger.log_step(problem=self.problem, decision_level= self.decision_level, decision_literal=(decision_literal), explanation="INC_DL " + self.heuristic_name)
    
    def _undo_assignments(self, decision_literal: int, abs_value: int, propagated_literals: List[int]) -> None:
        """
        Undo the assignment of the decision literal and any propagated literals.

        Args:
            decision_literal (int): The literal to unassign.
            var (int): The absolute value of the literal.
            propagated_literals (List[int]): The list of literals to unassign.
        """
        del self.problem.assignments[abs_value]
        for lit in propagated_literals:
            del self.problem.assignments[abs(lit)]
        affected_literals = [-decision_literal] + propagated_literals
        self.problem.update_satisfaction_map(operation='undo assignment', literals_to_unassign=affected_literals)
    
    def _dpll_recursive(self) -> bool:
        """
        Recursive implementation of the DPLL algorithm with optional detailed logging.

        Returns:
            bool: True if the formula is satisfiable, False otherwise.
        """
        # Base cases
        if self.problem.is_satisfied():
            return True
        if self.problem.is_unsatisfiable():
            return False

        # Unit propagation 
        BCP_result, propagated_literals = self._unit_propagation_loop()
        if BCP_result is not None:
            return BCP_result

        # Call the heuristic function to choose the decision literal and increment the decision level
        decision_literal, abs_value = self._choose_decision_literal()

        # Try assigning True to the literal
        self._make_decision(decision_literal, abs_value, first_branch=True)
        if self._dpll_recursive():
            return True

        # Backtrack and try assigning False
        self._make_decision(-decision_literal, abs_value, first_branch=False)
        if self._dpll_recursive():
            return True

        # Undo assignments and backtrack decision level if both branches fail
        self._undo_assignments(decision_literal, abs_value, propagated_literals)
        self.decision_level -= 1

        return False
    
    def solve(self) -> bool:
        """
        Solve the SAT problem using the DPLL algorithm.
        
        Returns:
            bool: True if the problem is satisfiable, False otherwise.
        """
        satisfiable = self._dpll_recursive()
        return satisfiable
    
    def print_steps(self) -> None:
        """
        Print the logged decision steps.
        """
        self.step_logger.print_steps()

    def get_decision_steps(self) -> List[dict]:
        """
        Retrieve the logged decision steps from the solving process.

        Returns:
            list: A list of dictionaries, where each dictionary represents a logged step.
        """
        return self.step_logger.steps
