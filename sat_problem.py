class SATProblem:
    """
    This class represents a SAT (Boolean Satisfiability) problem.
    
    Attributes:
        clauses (List[List[int]]): A list of clauses, where each clause is a list of integers
            representing literals. Positive integers represent the literal in true form, and
            negative integers represent the negated literal.
        assignments (Dict[int, bool]): A dictionary holding current variable assignments. Keys
            are variable identifiers, and values are boolean values representing the current 
            assignment (True or False).
        satisfaction_map (List[bool]): A list of booleans where each entry corresponds to a clause
            in `clauses`, indicating whether the clause is currently satisfied based on `assignments`.
    """

    def __init__(self, clauses):
        """
        Initialize the SAT problem with a set of clauses.
        
        Args:
            clauses (list of lists of ints): A list of clauses, where each clause is a list of literals.
        """
        self.clauses = clauses
        self.assignments = {}
        self.satisfaction_map = [False] * len(clauses) 

    def update_satisfaction_map(self):
        """ Update satisfaction map based on current assignments. """
        for i, clause in enumerate(self.clauses):
            self.satisfaction_map[i] = any(
                abs(lit) in self.assignments and self.assignments[abs(lit)] == (lit > 0)
                for lit in clause
            )

    def is_satisfied(self):
        """ Return True if all clauses are satisfied, else False. """
        return all(self.satisfaction_map)

    def is_unsatisfiable(self):
        """ Return True if any clause is contradicted, else False. """
        return any(len([lit for lit in clause if abs(lit) not in self.assignments]) == 0 
            and not self.satisfaction_map[i] 
            for i, clause in enumerate(self.clauses))