"""
moms_branching_heuristics.py

This module implements the MOM's (Maximum Occurrences on clauses of Minimum size) 
branching heuristic and its randomized variation (RMOM's). The heuristics are used to 
select a decision literal in the DPLL SAT solver, focusing on literals that appear most 
frequently in the smallest non-satisfied clauses.

The following heuristics are implemented:
- **MOM's**: Selects the variable that maximizes the function 
  (f(x) + f(¬x)) * 2^k + f(x) * f(¬x), where f(x) counts occurrences of the literal 
  in the smallest unsatisfied clauses.
- **RMOM's**: Randomized version of MOM's, where the chosen literal is randomly assigned 
  True or False, based on the result from MOM's heuristic.

Functions:
    - _count_occurrences_in_smallest_clauses(problem): Helper function to count literal occurrences 
      in the smallest unsatisfied clauses.
    - moms(problem, k=0): MOM's heuristic with a user-defined k value.
    - rmoms(problem, k=0): Randomized MOM's heuristic (RMOM's), randomly assigns True or False to the selected literal.
"""

import random

def _count_occurrences_in_smallest_clauses(problem):
    """
    Helper function to count occurrences of each literal in the smallest non-satisfied clauses.

    The function computes the size of the smallest clauses based on the number of unassigned literals 
    and then counts how many times each literal appears in these smallest clauses.

    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        dict: A dictionary where the keys are variable numbers (the literals) and the values are dictionaries 
              with the count of positive (1) and negative (-1) occurrences of the variable 
              in the smallest unsatisfied clauses.
    """
    # Find the smallest clause size among non-satisfied clauses
    min_clause_size = min(
            len([lit for lit in clause if abs(lit) not in problem.assignments]) 
            for i, clause in enumerate(problem.clauses) if not problem.satisfaction_map[i]
            )
    # Initialize a count dictionary
    literal_counts = {}
    for i, clause in enumerate(problem.clauses):
        if problem.satisfaction_map[i] or len([lit for lit in clause if abs(lit) not in problem.assignments]) != min_clause_size:
            continue  # Skip satisfied clauses and non-smallest clauses
        for lit in clause:
            var = abs(lit)
            if var not in literal_counts:
                literal_counts[var] = {1: 0, -1: 0}
            literal_counts[var][1 if lit > 0 else -1] += 1
    return literal_counts

def moms(problem, k=0):
    """
    MOM's Heuristic (Maximum Occurrences on clauses of Minimum size).
    Selects the variable that maximizes the function (f(x) + f(¬x)) * 2^k + f(x) * f(¬x),
    where f(x) is the count of literal occurrences in the smallest unsatisfied clauses.

    This heuristic prefers variables that appear most frequently in the smallest unsatisfied clauses 
    and assigns values based on the comparison of f(x) and f(¬x). 
    A large value of k increases the influence of almost-pure literals.
    A small value of k creates a more balanced tree.

    Args:
        problem (SATProblem): The SAT problem instance.
        k (int): The value of k for the heuristic formula. Defaults to 0.

    Returns:
        int: The literal to branch on, with positive for True and negative for False.
    """
    literal_counts = _count_occurrences_in_smallest_clauses(problem)
    best_var = None
    best_score = -1
    best_sign = 1

    for var, counts in literal_counts.items():
        score = (counts[1] + counts[-1]) * (2 ** k) + counts[1] * counts[-1]
        if score > best_score:
            best_score = score
            best_var = var
            best_sign = 1 if counts[1] >= counts[-1] else -1

    return best_var * best_sign

def rmoms(problem, k=0):
    """
    Randomized MOM's Heuristic (RMOM's).
    Selects the variable that would be selected by MOM's, but assigns it a random value (True or False).

    This function works similarly to the MOM's heuristic, but instead of deterministically assigning 
    True or False based on the comparison of f(x) and f(¬x), the value is randomly chosen.

    Args:
        problem (SATProblem): The SAT problem instance.
        k (int): The value of k for the heuristic formula, passed to the `moms` function.

    Returns:
        int: The literal to branch on, with positive for True and negative for False.
    """
    var = moms(problem, k)
    return var if random.choice([True, False]) else -var
