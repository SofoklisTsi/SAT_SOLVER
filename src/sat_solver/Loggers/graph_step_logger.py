"""
cdcl_logger.py

This module contains the GraphStepLogger class, which is used to log the solving steps of the CDCL SAT solver.
"""

from typing import Dict, List, Optional
from .step_logger import StepLogger

class GraphStepLogger(StepLogger):
    """
    Class to log the solving steps of the SAT solver.
    Subclass of StepLogger.

    Inherited Attributes:
        steps (List[Dict[str, Any]]): List of steps logged during the solving process.

    Methods:
        _change_node_names(last_node): Make the implication graph's last node's names shorter for better readability of the log.
    
    Overridden Methods:
        log_step(problem, decision_level, decision_literal, implied_literal, explanation): Log the current state in the DPLL decision process.
        print_steps(table_format): Print the logged decision steps, optionally in a tabular format.

    Inherited Methods:
        create_json_file(directory, filename): Create a JSON file containing the logged decision steps.
    """

    def _change_node_names(self, last_node: Dict[str, Optional[int]]) -> Dict[str, Optional[int]]:
        """
        Make the implication graph's last node's names shorter for better readability of the log.

        Args:
            last_node (Dict[str, Optional[int]]): The last node of the implication graph.

        Returns:
            Dict[str, Optional[int]]: The updated node.
        """
        updated_node = {}
        for key, value in last_node.items():
            if key == "decision_level":
                updated_node["DL"] = value
            elif key == "antecedent":
                updated_node["Ante"] = value
        return updated_node
    
    def log_step(self, decision_level: int, implication_graph: Dict[int, Dict[str, Optional[int]]], decision_literal: Optional[int] = None, implied_literal : Optional[int] = None,  learned_clause: Optional[List[int]] = None, backtrack_level: Optional[int] = None, cutting_method: str = "") -> None:
        """
        Log the current state in the CDCL decision process, including key details like:
        - Decision and implied literals
        - Implication graph
        - Learned clause
        - Cut method used

        Args:
            decision_level (int): The current decision level.
            decision_literal (int): The decision literal at the current step.
            implied_literal (int): The implied literal from unit propagation.
            implication_graph (Dict[int, Dict[str, Optional[int]]]): The implication graph at the current step.
            learned_clause (Optional[List[int]]): The learned clause at the current step.
            cut_method (str): The cut method used to learn the clause.
        """

        if decision_literal is not None:
            last_node = self._change_node_names(implication_graph[decision_literal])
        elif implied_literal is not None:
            last_node = self._change_node_names(implication_graph[implied_literal])
        else:
            last_node = None
        # Log entry
        self.steps.append({
            "Decision Level": decision_level,
            "Decision Literal": decision_literal,
            "Implied Literal": implied_literal,
            "Implication Graph": last_node,
            "Learned Clause": learned_clause,
            "Backtrack Level": backtrack_level,
            "Cut Method": cutting_method
        })

    def print_step(self) -> None:
        """
        Print the logged decision steps, optionally in a tabular format.
        """
        # Print header row and title
        print("\nDecision Graph:")
        header = [
            "DL", "DLit", "IL", "Implication Graph", "Learned Clause", "Backtrack Level", "Cut Method"
        ]
        print("{:<3} {:<5} {:<5} {:<30} {:<25} {:<20} {:<20}".format(*header))

        # Print each step in a single row
        for step in self.steps:
            row = [
                step["Decision Level"],
                str(step["Decision Literal"]),
                str(step["Implied Literal"]),
                str(step["Implication Graph"]),
                str(step["Learned Clause"]),
                str(step["Backtrack Level"]),
                step["Cut Method"]
            ]  
            print("{:<3} {:<5} {:<5} {:<30} {:<25} {:<20} {:<20}".format(*row))  
