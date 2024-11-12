from sat_problem import SATProblem

class TWLSATProblem(SATProblem):
    """
    Extended SATProblem class that incorporates the Two Watched Literals (TWL) technique.

    Attributes:
        original_clauses (List[List[int]]): The original SAT clauses.
        The rest of the attributes are inherited from the SATProblem class.
    
    Methods:
        _initialize_watched_literals(): Sets up two watched literals for each clause.
        update_watched_literals(): Updates watched literals when a literal's assignment changes.
        The rest of the methods are inherited from the SATProblem class.
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
        clauses_with_twl = self._initialize_watched_literals(sat_problem_instance.satisfaction_map, sat_problem_instance.assignments)
        super().__init__(clauses_with_twl)
        self.assignments = sat_problem_instance.assignments
        self.satisfaction_map = sat_problem_instance.satisfaction_map

    def _initialize_watched_literals(self, satisfaction_map, assignments):
        """
        Initialize watched literals for each clause.

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
                # Watch the first two literals in each clause by default
                # Collect up to two unassigned literals in the clause
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
        Updates watched literals when an assignment is made. 
        If a watched literal in a clause becomes false, tries to find an alternative literal 
        in the clause to watch.

        Args:
            assigned_literal (int): The literal that has been assigned a value.

        Raises:
            ValueError: If a clause (that was not unit clause before) does not have exactly two literals after updating.
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
    