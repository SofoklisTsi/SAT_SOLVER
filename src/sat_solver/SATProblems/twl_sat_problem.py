"""
twl_sat_problem.py

This module defines the `TWLSATProblem` class, an extension of the SATProblem class
that incorporates the Two Watched Literals (TWL) technique. This class is the standard
implementation of the TWL, where a clause is satisfied if any of its literals is assigned to `True`.

Key Differences from TrueTWLSATProblem:
- TWLSATProblem considers a clause satisfied if any literal in the clause is assigned to `True`.
- TrueTWLSATProblem considers a clause satisfied only when a watched literal is assigned to `True`.

Features:
- Integration of Pydantic for enhanced data validation and type checking.
- Initialization of watched literals and dynamic updates during the SAT solving process.

Dependencies:
    - `Pydantic`: Provides robust data validation and parsing features.
"""

from typing import List, Dict
from pydantic import ConfigDict, Field, model_validator
from sat_solver.SATProblems.sat_problem import SATProblem
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel
from ordered_set import OrderedSet

class TWLSATProblem(SATProblem):
    """
    Extended SATProblem class that incorporates the Two Watched Literals (TWL) technique.
        The difference between this class and the TrueTWLSATProblem class is that the true TWL class considers
        a clause to be satisfied if a watched literal is assigned to True, while the TWLSATProblem class considers
        a clause to be satisfied if any literal in the clause is assigned to True.

    Attributes:
        original_clauses (List[List[int]]): The original SAT clauses, unchanged throughout execution.
        clauses_by_watched_literal (Dict[int, List[int]]): Mapping of watched literals to the indices
            of clauses where they are being watched. Enables efficient updates to watched literals.

    Inherited Attributes from SATProblem:
        clauses (List[List[int]]): Modified clauses where two watched literals are tracked per clause.
        clauses_by_literal (Dict[int, List[int]]): Mapping of literals to the indices of clauses where they appear.
        num_of_assigned_literals_that_satisfy_a_clause (List[int]): Tracks the count of assigned literals
            satisfying each clause.
        num_of_unassigned_literals_in_clause (List[int]): Tracks the count of unassigned literals in each clause.
        assignments (Dict[int, bool]): Current variable assignments.
        satisfaction_map (List[bool]): Indicates whether each clause is currently satisfied.

    Methods:
        _initialize_watched_literals(satisfaction_map, assignments):
            Initializes two watched literals for each clause.
        _update_watched_literals(clause_index, assigned_literal):
            Updates watched literals when one of the currently watched literals is assigned.
        _new_literal_assigned(assigned_literal):
            Updates satisfaction state and watched literals when a literal is assigned.
        _old_literal_unassigned(unassigned_literal):
            Updates satisfaction state and watched literals when a literal is unassigned.
        add_clause(clause):
            Adds a new clause to the SAT problem, updating the satisfaction map and watched literals.

    Inherited Methods from SATProblem:
        _build_clauses_by_literal(clauses):
            Create a mapping from each literal to the indices of the clauses it appears in.
        _initial_unit_clauses_check(clauses):
            Check for unit clauses in the initial clauses.
        update_satisfaction_map(operation, literal_to_assign=None, literals_to_unassign=None):
            Updates satisfaction and watched literal states based on specified operations.
        get_contradicited_clauses():
            Get the set of contradicted clauses.
        get_unitary_clauses():
            Get the set of unitary clauses.
        is_satisfied():
            Check if the SAT problem is satisfied.
        is_unsatisfiable():
            Check if the SAT problem is unsatisfiable.
    """

    original_clauses: List[List[int]] = Field(..., description="List of the original clauses, each containing literals")
    clauses_by_watched_literal: Dict[int, List[int]] = Field(default_factory=dict, description="Clauses indexed by watched literals")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def initialize_computed_fields(cls, values: Dict[str, any]) -> Dict[str, any]:
        """
        Initializes computed fields for the TWLSATProblem class, including watched literals, 
        satisfaction map, clauses by literal, and other internal state data.

        Args:
            values (dict): Dictionary of values passed to the model, including the clauses model and 
                           other fields related to the SAT problem.

        Returns:
            dict: Updated dictionary of values with initialized fields, such as the satisfaction map, 
                  clauses indexed by literals, and other computed fields.
        
        Raises:
            TypeError: If the provided 'clauses_model' is not an instance of ClausesModel.
            ValueError: If the 'clauses_model' does not contain valid clauses.
        """
        clauses_model = values.get("clauses_model")
        if not isinstance(clauses_model, ClausesModel):
            raise TypeError(f"Expected an instance of ClausesModel, but got {type(clauses_model)}")
        
        if clauses_model:
            # Initialize the fields based on clauses_model
            values["original_clauses"] = clauses_model.clauses
            values["number_of_clauses"] = clauses_model.num_clauses
            values["number_of_variables"] = clauses_model.num_vars
        
        original_clauses = values.get("original_clauses", [])

        if not original_clauses:
            raise ValueError("The provided clauses model does not contain valid clauses.")
        
        # Initialize watched literals for each clause
        clauses_with_twl = cls._initialize_watched_literals(values.get("original_clauses",[]))

        # Initialize the computed fields
        values["clauses"] = clauses_with_twl
        values["satisfaction_map"] = [False] * len(clauses_with_twl)
        values["clauses_by_literal"] = cls._build_clauses_by_literal(original_clauses)
        values["clauses_by_watched_literal"] = cls._build_clauses_by_literal(clauses_with_twl)
        values["num_of_assigned_literals_that_satisfy_a_clause"] = [0] * len(clauses_with_twl)
        values["num_of_unassigned_literals_in_clause"] = [len(clause) for clause in clauses_with_twl]
        values["unitary_clauses"] = cls._initial_unit_clauses_check(clauses_with_twl)
        # Initialize empty assignments and contradicted clauses
        values["assignments"] = {}
        values["contradicted_clauses"] = OrderedSet()
        
        return values

    @classmethod
    def _initialize_watched_literals(cls, original_clauses: List[List[int]]) -> List[List[int]]:
        """
        Initializes two watched literals for each clause. If a clause is satisfied, it remains unchanged.
        Otherwise, selects up to two unassigned literals in the clause as watched literals.

        Args:
            original_clauses (List[List[int]]): The original clauses to initialize watched literals for.

        Returns:
            List[List[int]]: Clauses with initial two watched literals set (or one for a unit clause).

        Raises:
            ValueError: If no unassigned literals are found in a clause.
        """
        clauses_with_twl = []
        for i, clause in enumerate(original_clauses):
            # Select up to two unassigned literals to watch.
            watched_literals = []
            for lit in clause:
                watched_literals.append(lit)
                if len(watched_literals) == 2:
                    break
            if not watched_literals:
                raise ValueError(f"No unassigned literals found in clause number {i} = {clause}")
            clauses_with_twl.append(watched_literals)
        return clauses_with_twl
    
    def _update_watched_literals(self, clause_index: int, assigned_literal: int) -> bool:
        """
        Updates the watched literals for a clause when one of its currently watched literals is assigned.

        Args:
            clause_index (int): The index of the clause to update.
            assigned_literal (int): The literal that has been assigned.

        Returns:
            bool: True if the watched literal was successfully updated, False otherwise.
        """
        if self.satisfaction_map[clause_index]:
            return False
        for lit in self.original_clauses[clause_index]:
            if lit in self.clauses[clause_index]:
                continue
            if abs(lit) not in self.assignments:
                self.clauses[clause_index].remove(-assigned_literal)    
                self.clauses_by_watched_literal[-assigned_literal].remove(clause_index)
                if lit not in self.clauses_by_watched_literal:
                    self.clauses_by_watched_literal[lit] = []
                self.clauses_by_watched_literal[lit].append(clause_index)
                self.clauses[clause_index].append(lit)
                return True
        return False

    def _new_literal_assigned(self, assigned_literal: int) -> None:
        """
        Updates satisfaction state and watched literals when a new literal is assigned.

        Args:
            assigned_literal (int): The literal that has been assigned.
        """
        if assigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[assigned_literal]:
                self.satisfaction_map[clause] = True
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] += 1   
                if assigned_literal in self.clauses[clause]:
                    self.num_of_unassigned_literals_in_clause[clause] -= 1
                    if clause in self.unitary_clauses: 
                        self.unitary_clauses.remove(clause) 
        if -assigned_literal in self.clauses_by_watched_literal:
            for clause in list(self.clauses_by_watched_literal[-assigned_literal]): # Use a copy for safe iteration
                if not self._update_watched_literals(clause, assigned_literal):
                    self.num_of_unassigned_literals_in_clause[clause] -= 1   
                    if self.num_of_unassigned_literals_in_clause[clause] == 0 and not self.satisfaction_map[clause]:
                        self.contradicted_clauses.add(clause)
                    elif self.num_of_unassigned_literals_in_clause[clause] == 1 and not self.satisfaction_map[clause]: 
                        self.unitary_clauses.add(clause) 

    def _old_literal_unassigned(self, unassigned_literal: int) -> None:
        """
        Updates satisfaction state and watched literals when a literal is unassigned.

        Args:
            unassigned_literal (int): The literal that is being unassigned.
        """
        if unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[unassigned_literal]:
                if unassigned_literal in self.clauses[clause]:
                    self.num_of_unassigned_literals_in_clause[clause] += 1
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] -= 1
                if self.num_of_assigned_literals_that_satisfy_a_clause[clause] == 0:
                    self.satisfaction_map[clause] = False
                    if self.num_of_unassigned_literals_in_clause[clause] == 1: 
                        self.unitary_clauses.add(clause) 
        if -unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[-unassigned_literal]:
                if -unassigned_literal in self.clauses[clause]:
                    if self.num_of_assigned_literals_that_satisfy_a_clause[clause] == 0 and not self.satisfaction_map[clause]:
                        if clause in self.contradicted_clauses:
                            self.contradicted_clauses.remove(clause)
                            self.unitary_clauses.add(clause) 
                    self.num_of_unassigned_literals_in_clause[clause] += 1
                    if clause in self.unitary_clauses and not self.satisfaction_map[clause]: 
                        if self.num_of_unassigned_literals_in_clause[clause] > 1: 
                            self.unitary_clauses.remove(clause)
                
    def add_clause(self, clause: List[int]) -> None:
        """
        Add a new clause to the SAT problem.
        do extra controls if the addition of the clause takes place after the initialization of the SATProblem.

        Args:
            clause (List[int]): The clause to add.
        """
        self.original_clauses.append(clause)
        self.number_of_clauses += 1
        clause_with_twl = self._initialize_watched_literals([clause])[0]
        self.clauses.append(clause_with_twl)
        self.satisfaction_map.append(False)
        self.num_of_assigned_literals_that_satisfy_a_clause.append(0)
        if len(clause_with_twl) == 1:
            self.unitary_clauses.add(self.number_of_clauses - 1)
            self.num_of_unassigned_literals_in_clause.append(1)
        else:
            self.num_of_unassigned_literals_in_clause.append(2)

        assignments_snapshot = self.assignments.copy()
        contradictions_snapshot = self.contradicted_clauses.copy()
        unitary_snapshot = self.unitary_clauses.copy()

        literals_to_unassign = []
        for lit in clause:
            if abs(lit) in self.assignments:
                if self.assignments[abs(lit)] == lit > 0:
                    literals_to_unassign.append(lit)
                else:
                    literals_to_unassign.append(-lit)
        self.update_satisfaction_map(operation="undo assignment", literal_to_assign=None, literals_to_unassign=literals_to_unassign)
        for lit in clause:
            if lit not in self.clauses_by_literal:
                self.clauses_by_literal[lit] = []
            self.clauses_by_literal[lit].append(self.number_of_clauses - 1)
        for lit in clause_with_twl:
            if lit not in self.clauses_by_watched_literal:
                self.clauses_by_watched_literal[lit] = []
            self.clauses_by_watched_literal[lit].append(self.number_of_clauses - 1)

        for lit in literals_to_unassign:
            self.update_satisfaction_map(operation="new assignment", literal_to_assign=lit, literals_to_unassign=None)

        self.assignments = assignments_snapshot

        if (self.number_of_clauses -1) in self.contradicted_clauses:
            self.contradicted_clauses = contradictions_snapshot.copy()
            self.contradicted_clauses.add(self.number_of_clauses - 1)
        else:
            self.contradicted_clauses = contradictions_snapshot.copy()

        if (self.number_of_clauses -1) in self.unitary_clauses:
            self.unitary_clauses = unitary_snapshot.copy()
            self.unitary_clauses.add(self.number_of_clauses - 1)
        else:
            self.unitary_clauses = unitary_snapshot.copy()

        