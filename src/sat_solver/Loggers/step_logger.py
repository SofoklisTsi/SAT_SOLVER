"""
step_logger.py

This module contains the StepLogger class, which is used to log the solving steps of the SAT solver.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field, BaseModel
from sat_solver.SATProblems.sat_problem import SATProblem

class StepLogger(BaseModel):
    """
    Class to log the solving steps of the SAT solver.

    Attributes:
        steps (List[Dict[str, Any]]): List of steps logged during the solving process.

    Methods:
        log_step(problem, decision_level, decision_literal, implied_literal, explanation): Log the current state in the DPLL decision process.
        print_steps(table_format): Print the logged decision steps, optionally in a tabular format.
    """
    steps: List[Dict[str, Any]] = Field(default_factory=list, title="List of steps logged during the solving process.")

    def log_step(self, problem: SATProblem, decision_level: int, decision_literal: Optional[int] = None, implied_literal : Optional[int] = None, explanation: str = "") -> None:
        """
        Log the current state in the DPLL decision process, including key details like:
        - Partial assignments
        - Satisfied, contradicted, unit, and pending clauses
        - Decision and implied literals

        Args:
            problem (SATProblem): The SAT problem instance.
            decision_level (int): The current decision level.
            decision_literal (int): The decision literal at the current step.
            implied_literal (int): The implied literal from unit propagation.
            explanation (str): A textual explanation of the current action.
        """
        # Partial assignment
        partial_assignment = "{" + ", ".join(str(var if value else -var) for var, value in problem.assignments.items()) + "}"
        
        # Satisfied clauses, Contradicted clauses, Unit clauses and Pending clauses
        satisfied_clauses = []
        contradicted_clauses = []
        unit_clauses = []
        pending_clauses = []
        for i, clause in enumerate(problem.clauses):
            if problem.satisfaction_map[i]:
                satisfied_clauses.append(i)
                continue
            else:
                length = problem.num_of_unassigned_literals_in_clause[i] 
                if length == 0:
                    contradicted_clauses.append(i)
                elif length == 1:
                    unit_clauses.append(i)
                else:
                    pending_clauses.append(i)
        # Log entry
        self.steps.append({
            "Decision Level": decision_level,
            "Partial Assignment": partial_assignment,
            "Decision Literal": decision_literal,
            "Implied Literal": implied_literal,
            "Satisfied Clauses": satisfied_clauses,
            "Contradicted Clauses": contradicted_clauses,
            "Unit Clauses": unit_clauses,
            "Pending Clauses": pending_clauses,
            "Explanation": explanation
        })

    def print_steps(self, table_format: bool = True) -> None:
        """
        Print the logged decision steps, optionally in a tabular format.

        Args:
            table_format (bool): Whether to print the steps in a table format. Defaults to True.
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