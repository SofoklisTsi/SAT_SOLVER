"""
literal_count_branching_heuristics.py

This module provides several branching heuristics for use in a SAT solver based on
the DPLL (Davis-Putnam-Logemann-Loveland) algorithm. The heuristics determine the
decision literal to branch on at each step, optimizing the SAT solver's efficiency
in finding a solution.

Each heuristic is designed to assess unresolved clauses in the SAT problem instance
and select the next literal to branch on according to different strategies. Available
heuristics include:

- **DLCS**: Dynamic Largest Combined Sum of literals.
- **DLIS**: Dynamic Largest Individual Sum of literals.
- **RDLCS**: Randomized DLCS, with random value assignment.
- **RDLIS**: Randomized DLIS, with random value assignment.
- **Default**: A simple heuristic that selects the first unassigned literal and assigns it True.

Functions:
    - dlcs(problem): Dynamic Largest Combined Sum of literals heuristic.
    - dlis(problem): Dynamic Largest Individual Sum of literals heuristic.
    - rdlcs(problem): Randomized DLCS heuristic.
    - rdlis(problem): Randomized DLIS heuristic.
    - default_heuristic(problem): Selects the first unassigned literal and assigns it True.
    - _count_literals(problem): Helper function to count literals in unresolved clauses.
"""

import random

def dlcs(problem):
    """
    Dynamic Largest Combined Sum (DLCS) heuristic.
    Selects the variable with the largest sum of CP and CN (occurrences of
    the variable as positive and negative literals in unresolved clauses).   

    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        int: The literal to branch on (positive for True, negative for False).
    """
    # Use helper function to count literals in unresolved clauses
    literal_counts = _count_literals(problem) 
    # Compute CP + CN and select variable with largest sum
    best_var = None
    best_sum = -1
    best_sign = 1
    for var, counts in literal_counts.items():
        combined_sum = counts[1] + counts[-1]
        if combined_sum > best_sum:
            best_sum = combined_sum
            best_var = var
            best_sign = 1 if counts[1] >= counts[-1] else -1
    return best_var * best_sign

def dlis(problem):
    """
    Dynamic Largest Individual Sum (DLIS) heuristic.
    Selects the variable with the largest individual count of CP or CN
    (the count of occurrences as positive or negative literals, respectively, in unresolved clauses).
    
    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        int: The literal to branch on (positive for True, negative for False).
    """
    # Use helper function to count literals in unresolved clauses
    literal_counts = _count_literals(problem) 
    # Compute max of CP and CN individually and select variable with largest count
    best_var = None
    best_count = -1
    best_sign = 1
    for var, counts in literal_counts.items():
        if counts[1] > best_count:
            best_var, best_count, best_sign = var, counts[1], 1
        if counts[-1] > best_count:
            best_var, best_count, best_sign = var, counts[-1], -1
    return best_var * best_sign

def rdlcs(problem):
    """
    Randomized Dynamic Largest Combined Sum (RDLCS) heuristic.
    Selects the variable with the largest sum of CP and CN, as in DLCS,
    but assigns it a random value.
    
    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        int: The literal to branch on (positive for True, negative for False).
    """
    var = dlcs(problem)
    # Randomly select the sign
    return var if random.choice([True, False]) else -var

def rdlis(problem):
    """
    Randomized Dynamic Largest Individual Sum (RDLIS) heuristic.
    Selects the variable with the largest individual count of CP or CN, as in DLIS,
    but assigns it a random value rather than basing it on CP vs CN.
    
    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        int: The literal to branch on (positive for True, negative for False).
    """
    var = dlis(problem)
    # Randomly select the sign
    return var if random.choice([True, False]) else -var

def default_heuristic(problem):
    """
    A simple default heuristic that selects the first unassigned literal
    and assigns it True.

    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        int: The literal to branch on (positive for True).
    """
    unassigned_literals = [lit for i, clause in enumerate(problem.clauses) for lit in clause if abs(lit) not in problem.assignments
                        and not problem.satisfaction_map[i]]
    return abs(unassigned_literals[0]) if unassigned_literals else None

def _count_literals(problem):
    """
    Count the occurrences of each literal in unresolved clauses, providing
    a count of each variable's appearances as positive and negative literals.
    
    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        dict: A dictionary where keys are variable numbers and values are dictionaries
              with counts of positive (1) and negative (-1) occurrences.
    """
    literal_counts = {}
    for i, clause in enumerate(problem.clauses):
        if problem.satisfaction_map[i]:
            continue  # Skip already satisfied clauses
        for lit in clause:
            if abs(lit) in problem.assignments:
                continue
            var = abs(lit)
            if var not in literal_counts:
                literal_counts[var] = {1: 0, -1: 0}
            literal_counts[var][1 if lit > 0 else -1] += 1
    return literal_counts
