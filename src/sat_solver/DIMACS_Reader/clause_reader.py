"""
clause_reader.py

This module provides the `ClauseReader` class for reading SAT problem clauses 
from a file in DIMACS format, commonly used in SATLIB and SAT Competitions.

Dependencies:
    - `ClausesModel`: A Pydantic model that validates and represents the structure of clauses and associated metadata.

Classes:
    ClauseReader:
        A utility class for reading and validating SAT problem clauses from a DIMACS file.
"""
from .clauses_model import ClausesModel

class ClauseReader:
    """
    A utility class for reading SAT problem clauses from a file in DIMACS format.

    Methods:
        read_file(filename: str) -> ClausesModel:
            Reads a DIMACS-formatted file and returns a validated ClausesModel instance.
    """
    @staticmethod
    def read_file(filename: str) -> ClausesModel:
        """
        Reads a DIMACS-formatted file and extracts clauses, the number of variables, and the number of clauses.

        The DIMACS format is structured as:
            - Lines starting with 'c' are comments and are ignored.
            - A line starting with 'p' declares the problem (e.g., 'p cnf <num_vars> <num_clauses>').
            - Subsequent lines specify clauses, where each clause is a list of integers ending with 0.
            - A line starting with '%' marks the end of the clauses.

        Args:
            filename (str): The path to the DIMACS file.

        Returns:
            ClausesModel: A validated ClausesModel instance containing the clauses, number of variables, 
            and number of clauses.

        Raises:
            ValueError: If the file format is invalid or contains errors, such as:
                - Missing or malformed problem line.
                - Unsupported format type (only 'cnf' is supported).
                - Invalid clause format (e.g., missing trailing 0).
        """
        clauses = []
        num_vars = 0
        num_clauses = 0
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('c'):  # Skip comments
                    continue
                if line.startswith('p'):  # Problem line
                    _, format_type, num_vars, num_clauses = line.split()
                    if format_type != "cnf":
                        raise ValueError("Unsupported format. Only CNF is allowed.")
                    num_vars = int(num_vars)
                    num_clauses = int(num_clauses)
                elif line.startswith('%'):  # End of problem definition
                    break
                else:
                    clause = list(map(int, line.split()))
                    clauses.append(clause)  
        return ClausesModel(clauses=clauses, num_vars=num_vars, num_clauses=num_clauses)
