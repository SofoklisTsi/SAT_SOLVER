"""
This module contains the SATProblem class, which represents a SAT (Boolean Satisfiability) 
problem. It provides methods to manage clause satisfaction and assignments efficiently, 
as well as to integrate with the DPLL algorithm for solving the SAT problem.

The class uses the ClausesModel to handle the validation and structure of clauses, and it incorporates 
optimizations for clause satisfaction, unit clause detection, and contradicted clause management.

This version includes advanced logic for updating the satisfaction map, unit clauses, and contradictory clauses 
as literals are assigned and unassigned during the SAT-solving process.

It relies on the ClausesModel to handle the validation and structure of clauses.

Dependencies:
    - `Pydantic`: Provides robust data validation and parsing features.
"""

from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field, model_validator
from sat_solver.DIMACS_Reader.clauses_model import ClausesModel

class SATProblem(BaseModel):
    """
    This class represents a SAT (Boolean Satisfiability) problem, with utilities to manage
    clause satisfaction and assignments efficiently.
    
    Attributes:
        clauses_model (ClausesModel): The ClausesModel instance containing the clauses, number of variables,
            and number of clauses for the SAT problem.
        clauses (List[List[int]]): A list of clauses, where each clause is a list of integers
            representing literals. Positive integers represent the literal in true form, and
            negative integers represent the negated literal.
        number_of_clauses (int): The total number of clauses in the SAT problem, derived from the problem definition.
        number_of_variables (int): The total number of variables in the SAT problem, derived from the problem definition.
        assignments (Dict[int, bool]): A dictionary holding current variable assignments. Keys
            are variable identifiers, and values are boolean values representing the current 
            assignment (True or False).
        satisfaction_map (List[bool]): A list of booleans where each entry corresponds to a clause
            in `clauses`, indicating whether the clause is currently satisfied based on `assignments`.
        clauses_by_literal (Dict[int, List[int]]): A dictionary mapping each literal to the indices
            of the clauses it appears in. This enables efficient updates to satisfaction state.    
        num_of_assigned_literals_that_satisfy_a_clause (List[int]): A list where each index
            corresponds to the number of assigned literals satisfying the respective clause.
        num_of_unassigned_literals_in_clause (List[int]): A list where each index corresponds to 
            the number of unassigned literals remaining in the respective clause.
        contradicted_clauses (Set[int]): The set of contradicted clauses.
        unitary_clauses (Set[int]): The set of unitary clauses.

    Methods:
        _build_clauses_by_literal(clauses):
            Create a mapping from each literal to the indices of the clauses it appears in.
        _initial_unit_clauses_check(clauses):
            Check for unit clauses in the initial clauses.
        _new_literal_assigned(assigned_literal):
            Update clause satisfaction when a new literal is assigned.
        _old_literal_unassigned(unassigned_literal):
            Update clause satisfaction when a literal is unassigned.
        update_satisfaction_map(operation, literal_to_assign=None, literals_to_unassign=None):
            Update the satisfaction map based on a specified operation.
        get_contradicited_clauses():
            Get the set of contradicted clauses.
        get_unitary_clauses():
            Get the set of unitary clauses.
        is_satisfied():
            Check if the SAT problem is satisfied.
        is_unsatisfiable():
            Check if the SAT problem is unsatisfiable.
    """

    clauses_model: ClausesModel = Field(..., description="The ClausesModel instance containing the clauses, number of variables, and number of clauses for the SAT problem")
    clauses: List[List[int]] = Field(..., description="List of clauses, each containing literals")
    number_of_clauses: int = Field(..., description="Number of clauses in the SAT problem")
    number_of_variables: int = Field(..., description="Number of variables in the SAT problem")
    assignments: Dict[int, bool] = Field(default_factory=dict, description="Assignments of literals")
    satisfaction_map: List[bool] = Field(default_factory=list, description="Satisfaction map of clauses")
    clauses_by_literal: Dict[int, List[int]] = Field(default_factory=dict, description="Clauses indexed by literals")
    num_of_assigned_literals_that_satisfy_a_clause: List[int] = Field(default_factory=list, description="Count of assigned literals that satisfy each clause")
    num_of_unassigned_literals_in_clause: List[int] = Field(default_factory=list, description="Count of unassigned literals in each clause")
    contradicted_clauses: Set[int] = Field(default_factory=set, description="Set of unsatisfied clauses")
    unitary_clauses: Set[int] = Field(default_factory=set, description="Set of unitary clauses")

    @model_validator(mode="before")
    @classmethod
    def initialize_computed_fields(cls, values: Dict[str, any]) -> Dict[str, any]:
        """
        Initialize the computed fields of the SATProblem model based on the ClausesModel.
        
        Args:
            values (dict): Dictionary of values passed to the model. This includes the clauses_model 
                           (ClausesModel instance) and other fields related to the SAT problem.
        
        Returns:
            dict: Updated dictionary of values with initialized computed fields, including the satisfaction map, 
                  clauses indexed by literals, and other internal data structures.

        Raises:
            TypeError: If the provided 'clauses_model' is not an instance of ClausesModel.
            ValueError: If the 'clauses_model' does not contain valid clauses.
        """
        clauses_model = values.get("clauses_model")
        if not isinstance(clauses_model, ClausesModel):
            raise TypeError(f"Expected an instance of ClausesModel, but got {type(clauses_model)}")
        
        if clauses_model:
            # Initialize the fields based on clauses_model
            values["clauses"] = clauses_model.clauses
            values["number_of_clauses"] = clauses_model.num_clauses
            values["number_of_variables"] = clauses_model.num_vars
        
        clauses = values.get("clauses", [])

        if not clauses:
            raise ValueError("The provided clauses model does not contain valid clauses.")
        
        # Initialize the computed fields
        values["satisfaction_map"] = [False] * len(clauses)
        values["clauses_by_literal"] = cls._build_clauses_by_literal(clauses)
        values["num_of_assigned_literals_that_satisfy_a_clause"] = [0] * len(clauses)
        values["num_of_unassigned_literals_in_clause"] = [len(clause) for clause in clauses]
        values["unitary_clauses"] = cls._initial_unit_clauses_check(clauses)
        # Initialize empty assignments and contradicted clauses
        values["assignments"] = {}
        values["contradicted_clauses"] = set()

        return values

    @classmethod
    def _build_clauses_by_literal(cls, clauses: List[List[int]]) -> Dict[int, List[int]]:
        """
        Create a mapping from each literal to the indices of the clauses it appears in.

        Args:
            clauses (List[List[int]]): The list of clauses.

        Returns:
            Dict[int, List[int]]: A dictionary mapping each literal to the indices of clauses
            where it appears.
        """
        clauses_by_literal = {}
        for i, clause in enumerate(clauses):
            for lit in clause:
                if lit not in clauses_by_literal:
                    clauses_by_literal[lit] = []
                clauses_by_literal[lit].append(i)
        return clauses_by_literal

    @classmethod
    def _initial_unit_clauses_check(cls, clauses: List[List[int]]) -> Set[int]:
        """
        Check for unit clauses in the initial clauses.

        Args:
            clauses (List[List[int]]): The list of clauses.

        Returns:
            set: The set of indices of unit clauses.
        """
        unitary_clauses = set()
        for i, clause in enumerate(clauses):
            if len(clause) == 1:
                unitary_clauses.add(i)
        return unitary_clauses

    def _new_literal_assigned(self, assigned_literal: int) -> None:
        """
        Update clause satisfaction when a new literal is assigned.

        Args:
            assigned_literal (int): The literal being assigned.
        """
        if assigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[assigned_literal]:
                self.satisfaction_map[clause] = True
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] += 1   
                self.num_of_unassigned_literals_in_clause[clause] -= 1
                if clause in self.unitary_clauses: 
                    self.unitary_clauses.remove(clause) 
        if -assigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[-assigned_literal]:
                self.num_of_unassigned_literals_in_clause[clause] -= 1     
                if self.num_of_unassigned_literals_in_clause[clause] == 0 and not self.satisfaction_map[clause]:
                    self.contradicted_clauses.add(clause)
                elif self.num_of_unassigned_literals_in_clause[clause] == 1 and not self.satisfaction_map[clause]: 
                    self.unitary_clauses.add(clause) 

    def _old_literal_unassigned(self, unassigned_literal: int) -> None:
        """
        Update clause satisfaction when a literal is unassigned.

        Args:
            unassigned_literal (int): The literal being unassigned.
        """
        if unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[unassigned_literal]:
                self.num_of_unassigned_literals_in_clause[clause] += 1
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] -= 1
                if self.num_of_assigned_literals_that_satisfy_a_clause[clause] == 0:
                    self.satisfaction_map[clause] = False
                    if self.num_of_unassigned_literals_in_clause[clause] == 1: 
                        self.unitary_clauses.add(clause) 
                
        if -unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[-unassigned_literal]:
                if self.num_of_assigned_literals_that_satisfy_a_clause[clause] == 0 and not self.satisfaction_map[clause]:
                    if clause in self.contradicted_clauses:
                        self.contradicted_clauses.remove(clause)
                        self.unitary_clauses.add(clause) 
                self.num_of_unassigned_literals_in_clause[clause] += 1
                if clause in self.unitary_clauses and not self.satisfaction_map[clause]: 
                    if self.num_of_unassigned_literals_in_clause[clause] > 1:
                        self.unitary_clauses.remove(clause) 
    
    def update_satisfaction_map(self, operation: str, literal_to_assign: Optional[int] = None, literals_to_unassign: Optional[List[int]] = None) -> None:
        """
        Update the satisfaction map based on the specified operation.

        Args:
            operation (str): The type of operation to perform. Options are:
                - 'new assignment': Assign a new literal.
                - 'undo assignment': Undo the assignment of one or more literals.
                - 'change assignment': Change the assignment of a literal.
            literal_to_assign (int, optional): The literal to assign. Required for 'new assignment'
                and 'change assignment' operations.
            literals_to_unassign (List[int], optional): The literals to unassign. Required for
                'undo assignment' operation.
        """
        if operation == 'new assignment':
            self._new_literal_assigned(literal_to_assign)
        elif operation == 'undo assignment':
            for literal_to_unassign in literals_to_unassign:
                self._old_literal_unassigned(literal_to_unassign)
        elif operation == 'change assignment':
            self._old_literal_unassigned(-literal_to_assign)
            self._new_literal_assigned(literal_to_assign) 

    def get_contradicited_clauses(self) -> Set[int]:
        """
        Get the set of contradicted clauses.

        Returns:
            set: The set of indices of contradicted clauses.
        """
        return self.contradicted_clauses
    
    def get_unitary_clauses(self) -> Set[int]:
        """
        Get the set of unitary clauses.

        Returns:
            set: The set of indices of unitary clauses.
        """
        return self.unitary_clauses
    
    def is_satisfied(self) -> bool:
        """
        Check if the SAT problem is satisfied.

        Returns:
            bool: True if all clauses are satisfied, else False.
        """
        return all(self.satisfaction_map)

    def is_unsatisfiable(self) -> bool:
        """
        Check if the SAT problem is unsatisfiable.

        Returns:
            bool: True if any clause is contradicted (unsatisfiable), else False.
        """
        return len(self.contradicted_clauses) >= 1
   