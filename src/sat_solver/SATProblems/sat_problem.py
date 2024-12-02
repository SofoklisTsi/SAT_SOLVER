class SATProblem:
    """
    This class represents a SAT (Boolean Satisfiability) problem, with utilities to manage
    clause satisfaction and assignments efficiently.
    
    Attributes:
        clauses (List[List[int]]): A list of clauses, where each clause is a list of integers
            representing literals. Positive integers represent the literal in true form, and
            negative integers represent the negated literal.
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

    Methods:
        __init__(clauses):
            Initialize the SAT problem with a set of clauses.
        _build_clauses_by_literal(clauses):
            Create a mapping from each literal to the indices of the clauses it appears in.
        _new_literal_assigned(assigned_literal):
            Update clause satisfaction when a new literal is assigned.
        _old_literal_unassigned(unassigned_literal):
            Update clause satisfaction when a literal is unassigned.
        update_satisfaction_map_after_clause_elimination(literals_to_assign):
            Update the satisfaction map after clause elimination by assigning new literals.
        update_satisfaction_map(operation, literal_to_assign=None, literals_to_unassign=None):
            Update the satisfaction map based on a specified operation.
        is_satisfied():
            Check if the SAT problem is satisfied.
        is_unsatisfiable():
            Check if the SAT problem is unsatisfiable.
    """
    def __init__(self, clauses):
        """
        Initialize the SAT problem with a set of clauses.

        Args:
            clauses (List[List[int]]): A list of clauses, where each clause is a list of literals.
        """
        self.clauses = clauses
        self.assignments = {}
        self.satisfaction_map = [False] * len(clauses) 
        self.clauses_by_literal = self._build_clauses_by_literal(clauses)
        self.num_of_assigned_literals_that_satisfy_a_clause = [0] * len(clauses)
        self.num_of_unassigned_literals_in_clause = [len(clause) for clause in clauses] # New attribute

    def _build_clauses_by_literal(self, clauses):
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

    def _new_literal_assigned(self, assigned_literal):
        """
        Update clause satisfaction when a new literal is assigned.

        Args:
            assigned_literal (int): The literal being assigned.
        """
        if assigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[assigned_literal]:
                self.satisfaction_map[clause] = True
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] += 1   
                self.num_of_unassigned_literals_in_clause[clause] -= 1 # NEW CODE
        if -assigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[-assigned_literal]:
                self.num_of_unassigned_literals_in_clause[clause] -= 1 # END NEW CODE      
     

    def _old_literal_unassigned(self, unassigned_literal):
        """
        Update clause satisfaction when a literal is unassigned.

        Args:
            unassigned_literal (int): The literal being unassigned.
        """
        if unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[unassigned_literal]:
                self.num_of_unassigned_literals_in_clause[clause] += 1
                if not self.satisfaction_map[clause]:
                    continue
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] -= 1
                if self.num_of_assigned_literals_that_satisfy_a_clause[clause] == 0:
                    self.satisfaction_map[clause] = False
        if -unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[-unassigned_literal]:
                self.num_of_unassigned_literals_in_clause[clause] += 1

    def update_satisfaction_map_after_clause_elimination(self, literals_to_assign):
        """
        Update the satisfaction map after clause elimination by assigning the new literals.

        Args:
            literals_to_assign (List[int]): The list of literals to assign.
        """
        for lit in literals_to_assign:
            self._new_literal_assigned(lit)
    
    def update_satisfaction_map(self, operation, literal_to_assign = None, literals_to_unassign = None):
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

    def is_satisfied(self):
        """
        Check if the SAT problem is satisfied.

        Returns:
            bool: True if all clauses are satisfied, else False.
        """
        return all(self.satisfaction_map)

    def is_unsatisfiable(self):
        """
        Check if the SAT problem is unsatisfiable.

        Returns:
            bool: True if any clause is contradicted (unsatisfiable), else False.
        """
        for i, clause in enumerate(self.clauses):
            if self.satisfaction_map[i]:
                continue
            if self.num_of_unassigned_literals_in_clause[i] == 0:
                return True
        return False

    