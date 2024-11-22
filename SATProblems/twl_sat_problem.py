from SATProblems.sat_problem import SATProblem

class TWLSATProblem(SATProblem):
    """
    Extended SATProblem class that incorporates the Two Watched Literals (TWL) technique.

    Attributes:
        original_clauses (List[List[int]]): The original SAT clauses, unchanged throughout execution.

    Inherited Attributes from SATProblem:
        clauses (List[List[int]]): Modified clauses where two watched literals are tracked per clause.
        clauses_by_literal (Dict[int, List[int]]): Mapping of literals to the indices of clauses where they appear.
        num_of_assigned_literals_that_satisfy_a_clause (List[int]): Tracks the count of assigned literals
            satisfying each clause.
        assignments (Dict[int, bool]): Current variable assignments.
        satisfaction_map (List[bool]): Indicates whether each clause is currently satisfied.
    
    Methods:
        _initialize_watched_literals(satisfaction_map, assignments):
            Initializes two watched literals for each clause.
        update_watched_literals(assigned_literal):
            Updates the watched literals when a literal's assignment changes.
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
        self.clauses_by_literal = self.clauses_by_literal = sat_problem_instance.clauses_by_literal
        self.num_of_assigned_literals_that_satisfy_a_clause = sat_problem_instance.num_of_assigned_literals_that_satisfy_a_clause
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
    
    def update_watched_literals(self, assigned_literal):
        """
        Updates watched literals when a literal is assigned. If a watched literal becomes false,
        tries to find an alternative literal in the clause to watch. If no alternative is found,
        ensures that the clause has exactly two literals (unless it’s a unit clause).

        Args:
            assigned_literal (int): The literal that has been assigned a value.

        Raises:
            ValueError: If a clause (that was not a unit clause before) does not have exactly
                two literals after updating.
        """
        for i, clause in enumerate(self.clauses):
            if self.satisfaction_map[i]:
                continue
            if len(clause) == 1:
                continue
            if -assigned_literal in clause:
                for lit in self.original_clauses[i]:
                    if abs(lit) in self.assignments and self.assignments[abs(lit)] == (lit > 0):
                        self.clauses[i].remove(-assigned_literal)    
                        self.clauses[i].append(lit)
                        self.satisfaction_map[i] = True
                        break
                    if abs(lit) not in self.assignments and lit not in clause:
                        self.clauses[i].remove(-assigned_literal)    
                        self.clauses[i].append(lit)
                        break
            if len(self.clauses[i]) != 2:
                raise ValueError(f"clause {i} = {self.clauses[i]} has size {len(self.clauses[i])} and is not satisfied")
    