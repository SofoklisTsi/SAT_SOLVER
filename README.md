# SAT Solver

This project is an implementation of a SAT (Boolean Satisfiability) solver using the **DPLL (Davis-Putnam-Logemann-Loveland)** algorithm in Python.

## Project Structure

SAT_SOLVER/
├── Solver/
│   ├── dpll_solver.py                # DPLL algorithm implementation.
├── SATProblems/
│   ├── sat_problem.py                # SAT problem representation.
│   ├── twl_sat_problem.py            # Two Watched Literals (TWL) SAT problem representation.
├── Clause_Elimination_Methods/
│   └── clause_elimination_methods.py  # Clause elimination techniques (e.g., pure literal elimination).
├── Heuristics/
│   ├── literal_count_branching_heuristics.py  # Literal count heuristics (Default, DLCS, DLIS, RDLCS, RDLIS).
│   └── moms_branching_heuristics.py           # MOM’s and RMOM’s heuristics.
├── DIMACS_Reader/
│   └── clause_reader.py             # Logic for reading DIMACS CNF files.
├── DATA/
│   ├── Clauses_Files/
│   │   ├── Clauses_Files_Results/
│   │   │   ├── PDFS_Results/       # Results for the pdf problems.
│   │   │   └── TESTS_Results/      # Testing results.
│   │   ├── PDFS/                   # SAT problem files in CNF format from the university's PDFs.
│   │   └── TESTS/                  # Test files created to test different aspects of the project.
│   ├── SATLIB/                     # Standard SAT problem instances from https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html.
│   │   ├── uf100-430/              
│   │   ├── uf125-538/              # Each folder contains 10 .cnf problems.
│   │   ├── uf150-645/
│   │   ├── uf20-91/
│   │   ├── uf250-1065/
│   │   └── uf75-325/
├── Testers/
│   ├── profile_output.prof          # Profiling output that will be created by test_SATLIB.py.
│   ├── test_dpll_solver.py          # Unit tests for DPLL solver.
│   ├── test_SATLIB.py               # Unit tests for SATLIB instances and Profiling.
│   └── version_tester.py            # Version testing to ensure the functionality of the Solver after each change.
├── .gitignore                       # Git ignore configuration.
└── README.md                        # Project documentation. This very file!


## Features

- **DPLL Algorithm**: Implements the DPLL algorithm with optional pure literal elimination and unit propagation.
- **Logging and Decision Table**: Logs each decision step, including decision literals, implied literals, satisfied/contradicted clauses, and explanations.
- **Configurable Options**: Includes settings for using or skipping pure literal elimination.
- **Unit Tests**: Basic tests for the solver using `test_dpll_solver.py`.

### Phase 2.1: Literal Count Heuristics and Clause Elimination Preparation

- **Literal Count Heuristics**: Adds branching heuristics (DLCS, DLIS, RDLCS, RDLIS) based on literal counts to guide decision-making, improving solver efficiency.
- **Clause Elimination Preparation**: Moved `pure_literal_elimination` to `clause_elimination_methods.py`, establishing a modular structure for future clause elimination techniques.

### Phase 2.2: Add MOM’s Heuristics

- **MOM's Heuristic**: Implements the Maximum Occurrences on clauses of Minimum size (MOM's) heuristic, which selects literals based on their frequency in the smallest unsatisfied clauses. MOM's heuristic uses a formula to prioritize literals that occur frequently, controlled by the parameter `k`.
- **RMOM's Heuristic**: Randomized version of MOM's, assigning a randomly chosen truth value (True/False) to the selected literal.
- **Flexible `k` Parameter**: Allows the user to adjust the sensitivity of MOM's heuristic through the `k` parameter, which influences literal selection. 

### Phase 3.0: Two Watched Literals (TWL) Optimization

- **Two Watched Literals**: Implements the Two Watched Literals optimization to improve unit propagation efficiency. By monitoring only two literals in each clause, this approach minimizes the number of literals checked at each decision level, making the solver more efficient for larger problems.
- **Integration with DPLL**: When twl=True is enabled, the solver converts the SAT problem instance to use the Two Watched Literals technique, making it compatible with the existing DPLL logic.

### Phase 3.1: DIMACS Clause Form Compatibility and Code Refactoring

- **DIMACS Reader**: A class that processes DIMACS .cnf files, extracting the problem's clauses, the number of literals, and the number of clauses for use in the solver.
- **Performance Testing**: Utilized cProfile and SnakeViz to benchmark the solver's performance with various SATLIB problem instances. This phase helped identify performance bottlenecks and areas for optimization.
- **Code Refactoring**: Following the performance analysis, significant changes were made to the codebase to optimize the solver's efficiency. While these improvements enhanced performance, they resulted in a decrease in code readability. 
- **Enhanced Project Structure**: As the project expanded, the code was reorganized into dedicated directories and modules to maintain clarity and manageability. This restructuring ensures easier navigation and scalability for future development.
- **Decision Literal Bug Fixed**: A bug was identified where the decision literal printed in the 'decision literal' column of the 'steps' log had incorrect polarity when heuristics other than the 'default' were used. This issue has now been resolved.

## Requirements

- Python 3.6 or higher
- [Git](https://git-scm.com/) for version control

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/SofoklisTsi/SAT_SOLVER.git
    cd SAT_SOLVER
    ```

2. (Optional) Set up a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies (for performance testing):
    ```bash
    pip install snakeviz
    ```

## Usage

1. To solve a SAT problem:
    ```python
    from SATPRoblems.sat_problem import SATProblem
    from Solver.dpll_solver import DPLLSolver

    clauses = [[1, -3], [-2, 3], [2, 4], [-4]]  # Example problem
    problem = SATProblem(clauses)
    solver = DPLLSolver(problem, use_pure_literal=True, heuristic='moms', k=2, twl=True)

    is_satisfiable = solver.solve()
    print("Satisfiable:", is_satisfiable)

    # Print decision steps (optional)
    solver.print_steps()
    ```

2. **Selecting Heuristics**:
   The solver supports multiple heuristics, which can be set via the `heuristic` parameter in `DPLLSolver`. Options include:
   - `'default'`: A simple first unassigned literal heuristic.
   - `'dlcs'`, `'dlis'`, `'rdlcs'`, `'rdlis'`: Literal count-based heuristics.
   - `'moms'`: MOM’s heuristic, with configurable `k` (e.g., `heuristic='moms', k=2`).
   - `'rmoms'`: RMOM’s heuristic, which randomizes the truth value of the selected literal (e.g., `heuristic='rmoms', k=2`).

3. **Two Watched Literals (TWL)**:
    To enable Two Watched Literals, pass twl=True when initializing DPLLSolver.

4. **Testing**:
   Run tests to verify the solver works correctly:
   ```bash
   python testers/version_tester.py
   ```

5. **Performance Testing**:
   To test the solver's performance, use the test_SATLIB.py script. This will profile the solver's execution using cProfile, which can then be visualized with SnakeViz. To do so, run the following commands:
   ```bash
    python testers/test_SATLIB.py
    snakeviz testers/profile_output.prof  # This opens a visualization of the profiling data
   ```

## Acknowledgements
A special thanks to the creator of the Folder Mapper VSCode Extension. This extension has been incredibly helpful in organizing and visualizing the project structure, as well as in explaining it to AI tools. https://github.com/m0n0t0ny/Folder-Mapper-VSCode-Extension
