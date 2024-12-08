"""
clauses_model.py

This module defines the `ClausesModel` class, a Pydantic model for representing 
and validating SAT problem clauses along with metadata.

Dependencies:
    - `Pydantic`: Provides robust data validation and parsing features.
"""

from typing import List
from pydantic import BaseModel, Field, field_validator

class ClausesModel(BaseModel):
    """
    A Pydantic model that represents the structure of SAT problem clauses and associated metadata.

    Attributes:
        clauses (List[List[int]]): A list of clauses, where each clause is a list of integers (literals).
        num_vars (int): The declared number of variables in the SAT problem.
        num_clauses (int): The declared number of clauses in the SAT problem.

    Validators:
        validate_clauses:
            Ensures clauses are non-empty, contain only integers, and end with a trailing 0 (removes the trailing 0).
        validate_num_clauses:
            Verifies the declared number of clauses matches the actual count of clauses.
        validate_num_vars:
            Ensures the number of declared variables matches the count of unique literals in the clauses.
    """
    clauses: List[List[int]] = Field(..., description="List of clauses, each containing literals")
    num_vars: int = Field(..., description="Number of variables in the SAT problem")
    num_clauses: int = Field(..., description="Number of clauses in the SAT problem")

    @field_validator('clauses')
    def validate_clauses(cls, clauses: List[List[int]]) -> List[List[int]]:
        """
        Validates that all clauses are non-empty, contain only integers, and end with a trailing 0.
        The trailing 0 is stripped from each clause.

        Args:
            clauses (List[List[int]]): The list of clauses to validate.

        Returns:
            List[List[int]]: The validated and cleaned list of clauses.

        Raises:
            ValueError: If any clause is empty, contains non-integer literals, or lacks a trailing 0.
        """
        for clause in clauses:
            if not clause:
                raise ValueError("Clauses cannot be empty.")
            if not all(isinstance(lit, int) for lit in clause):
                raise ValueError("All literals in clauses must be integers.")
            if not clause or clause[-1] != 0:
                raise ValueError(f"Invalid clause format. Each clause must end with 0. Clause: {clause}")
        return [clause[:-1] for clause in clauses]  # Strip the trailing 0
    
    @field_validator('num_clauses')
    def validate_num_clauses(cls, num_clauses: int, info: dict) -> int:
        """
        Validates that the number of clauses matches the declared count.

        Args:
            num_clauses (int): The declared number of clauses.
            info: Pydantic's FieldValidator data context.

        Returns:
            int: The validated number of clauses.

        Raises:
            ValueError: If the declared number of clauses does not match the actual count.
        """
        clauses = info.data.get('clauses')
        if 'clauses' and num_clauses != len(clauses):
            raise ValueError("Number of clauses does not match the declared value.")
        return num_clauses

    @field_validator('num_vars')
    def validate_num_vars(cls, num_vars: int, info: dict) -> int:
        """
        Validates that the number of variables matches the number of unique literals.

        Args:
            num_vars (int): The declared number of variables.
            info: Pydantic's FieldValidator data context.

        Returns:
            int: The validated number of variables.

        Raises:
            ValueError: If the number of unique literals does not match the declared variable count.
        """
        clauses = info.data.get('clauses')
        if 'clauses':
            unique_literals = set(abs(lit) for clause in clauses for lit in clause)
            if len(unique_literals) != num_vars:
                raise ValueError("Number of unique literals does not match the declared number of variables.")
        return num_vars



