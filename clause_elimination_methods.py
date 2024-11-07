"""
    clause_elimination_methods.py

    This module contains methods for eliminating clauses and literals from a SAT problem instance.

    Functions:
        - pure_literal_elimination(problem): Performs pure literal elimination on the SAT problem instance.
"""

def pure_literal_elimination(problem):
    """
    Performs pure literal elimination: If a literal appears only as positive or negative in the formula,
    assign it accordingly. For all pure literals.

    Args:
        problem (SATProblem): The SAT problem instance.

    Returns:
        tuple: (bool, list) - True if any pure literals were eliminated, and a list of affected literals.
    """
    # Track if any changes occurred and the affected literals
    changed = False
    affected_literals = []

    # Gather all literals by their polarities
    literal_counts = {}
    
    for i, clause in enumerate(problem.clauses):
        if problem.satisfaction_map[i]:
            continue  # Skip already satisfied clauses

        for lit in clause:
            var = abs(lit)
            if var not in literal_counts:
                literal_counts[var] = {1: 0, -1: 0}
            literal_counts[var][1 if lit > 0 else -1] += 1

    # Assign pure literals and update satisfaction
    for var, count in literal_counts.items():
        if count[1] > 0 and count[-1] == 0:
            # Pure positive literal
            problem.assignments[var] = True
            changed = True
            affected_literals.append(var)
        elif count[-1] > 0 and count[1] == 0:
            # Pure negative literal
            problem.assignments[var] = False
            changed = True
            affected_literals.append(-var)
    return changed, affected_literals
