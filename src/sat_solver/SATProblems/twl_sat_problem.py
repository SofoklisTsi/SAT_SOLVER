from SATProblems.sat_problem import SATProblem

class TWLSATProblem(SATProblem):
    """
    Extended SATProblem class that incorporates the Two Watched Literals (TWL) technique.
        The difference between this class and the TrueTWLSATProblem class is that the true TWL class considers
        a clause to be satisfied if a watched literal is assigned to True, while the TWLSATProblem class considers
        a clause to be satisfied if any literal in the clause is assigned to True.

    Attributes:
        original_clauses (List[List[int]]): The original SAT clauses, unchanged throughout execution.
        clauses_by_watched_literal (Dict[int, List[int]]): Mapping of watched literals to the indices
            of clauses where they are being watched. Enables efficient updates to watched literals.

    Inherited Attributes from SATProblem:
        clauses (List[List[int]]): Modified clauses where two watched literals are tracked per clause.
        clauses_by_literal (Dict[int, List[int]]): Mapping of literals to the indices of clauses where they appear.
        num_of_assigned_literals_that_satisfy_a_clause (List[int]): Tracks the count of assigned literals
            satisfying each clause.
        num_of_unassigned_literals_in_clause (List[int]): Tracks the count of unassigned literals in each clause.
        assignments (Dict[int, bool]): Current variable assignments.
        satisfaction_map (List[bool]): Indicates whether each clause is currently satisfied.

    Methods:
        _initialize_watched_literals(satisfaction_map, assignments):
            Initializes two watched literals for each clause.
        _update_watched_literals(clause_index, assigned_literal):
            Updates watched literals when one of the currently watched literals is assigned.
        _new_literal_assigned(assigned_literal):
            Updates satisfaction state and watched literals when a literal is assigned.
        _old_literal_unassigned(unassigned_literal):
            Updates satisfaction state and watched literals when a literal is unassigned.
        update_satisfaction_map(operation, literal_to_assign=None, literals_to_unassign=None):
            Updates satisfaction and watched literal states based on specified operations.
    """

    def __init__(self, sat_problem_instance):
        """
        Initialize the TWLSATProblem with the Two-Watched Literals technique.

        Args:
            sat_problem_instance (SATProblem): An instance of SATProblem containing the 
                initial problem setup, assignments, and satisfaction map.
        
        Raises:
            TypeError: If the provided instance is not of type SATProblem.
        """
        if not isinstance(sat_problem_instance, SATProblem):
            raise TypeError("Problem must be an instance of SATProblem")
        self.original_clauses = sat_problem_instance.clauses
        self.clauses = self._initialize_watched_literals(sat_problem_instance.satisfaction_map, sat_problem_instance.assignments)
        self.clauses_by_literal = sat_problem_instance.clauses_by_literal
        self.clauses_by_watched_literal = self._build_clauses_by_literal(self.clauses) # New new attribute
        self.num_of_assigned_literals_that_satisfy_a_clause = sat_problem_instance.num_of_assigned_literals_that_satisfy_a_clause
        self.num_of_unassigned_literals_in_clause = [len(clause) for clause in self.clauses] # New new attribute
        self.assignments = sat_problem_instance.assignments
        self.satisfaction_map = sat_problem_instance.satisfaction_map

    def _initialize_watched_literals(self, satisfaction_map, assignments):
        """
        Initializes two watched literals for each clause. If a clause is satisfied, it remains unchanged.
        Otherwise, selects up to two unassigned literals in the clause as watched literals.

        Args:
            satisfaction_map (List[bool]): Indicates if each clause is currently satisfied.
            assignments (Dict[int, bool]): Current variable assignments.

        Returns:
            List[List[int]]: Clauses with initial two watched literals set (or one for a unit clause).

        Raises:
            ValueError: If no unassigned literals are found in a clause and the clause is not satisfied.
        """
        clauses_with_twl = []
        for i, clause in enumerate(self.original_clauses):
            if satisfaction_map[i]: 
                # If the clause is satisfied, add the original clause to clauses_with_twl
                clauses_with_twl.append(clause)
            else:
                # Select up to two unassigned literals to watch.
                watched_literals = []
                for lit in clause:
                    if abs(lit) not in assignments:
                        watched_literals.append(lit)
                    if len(watched_literals) == 2:
                        break
                if not watched_literals:
                    raise ValueError(f"No unassigned literals found in clause number {i} = {clause}")
                clauses_with_twl.append(watched_literals)
        return clauses_with_twl
    
    def _update_watched_literals(self, clause_index, assigned_literal):
        """
        Updates the watched literals for a clause when one of its currently watched literals is assigned.

        Args:
            clause_index (int): The index of the clause to update.
            assigned_literal (int): The literal that has been assigned.

        Returns:
            bool: True if the watched literal was successfully updated, False otherwise.
        """
        if self.satisfaction_map[clause_index]:
            return False
        for lit in self.original_clauses[clause_index]:
            if lit in self.clauses[clause_index]:
                continue
            if abs(lit) not in self.assignments:
                self.clauses[clause_index].remove(-assigned_literal)    
                self.clauses_by_watched_literal[-assigned_literal].remove(clause_index)
                if lit not in self.clauses_by_watched_literal:
                    self.clauses_by_watched_literal[lit] = []
                self.clauses_by_watched_literal[lit].append(clause_index)
                self.clauses[clause_index].append(lit)
                return True
        return False

    def _new_literal_assigned(self, assigned_literal):
        """
        Updates satisfaction state and watched literals when a new literal is assigned.

        Args:
            assigned_literal (int): The literal that has been assigned.
        """
        if assigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[assigned_literal]:
                self.satisfaction_map[clause] = True
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] += 1   
                if assigned_literal in self.clauses[clause]:
                    self.num_of_unassigned_literals_in_clause[clause] -= 1
        if -assigned_literal in self.clauses_by_watched_literal:
            for clause in list(self.clauses_by_watched_literal[-assigned_literal]): # Use a copy for safe iteration
                if not self._update_watched_literals(clause, assigned_literal):
                    self.num_of_unassigned_literals_in_clause[clause] -= 1      

    def _old_literal_unassigned(self, unassigned_literal):
        """
        Updates satisfaction state and watched literals when a literal is unassigned.

        Args:
            unassigned_literal (int): The literal that is being unassigned.
        """
        if unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[unassigned_literal]:
                if unassigned_literal in self.clauses[clause]:
                    self.num_of_unassigned_literals_in_clause[clause] += 1
                if not self.satisfaction_map[clause]:
                    continue
                self.num_of_assigned_literals_that_satisfy_a_clause[clause] -= 1
                if self.num_of_assigned_literals_that_satisfy_a_clause[clause] == 0:
                    self.satisfaction_map[clause] = False
        if -unassigned_literal in self.clauses_by_literal:
            for clause in self.clauses_by_literal[-unassigned_literal]:
                if -unassigned_literal in self.clauses[clause]:
                    self.num_of_unassigned_literals_in_clause[clause] += 1

    def update_satisfaction_map(self, operation, literal_to_assign = None, literals_to_unassign = None):
        """
        Updates the satisfaction state and watched literals based on the specified operation.

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