# SAT Solver

This project is an implementation of a SAT (Boolean Satisfiability) solver using the **DPLL (Davis-Putnam-Logemann-Loveland)** algorithm in Python.

## Project Structure

SAT SOLVER 
├── dpll_solver.py # DPLL algorithm implementation 
├── sat_problem.py # SAT problem representation 
├── clause_elimination_methods.py # Clause elimination techniques, e.g., pure literal elimination 
├── literal_count_branching_heuristics.py # Literal count heuristics (DLCS, DLIS, RDLCS, RDLIS) 
├── moms_branching_heuristics.py # MOM’s and RMOM’s heuristics
├── twl_sat_problem.py # Two Watched Literals (TWL) SAT problem representation
├── pdf_clauses_and_results.txt # Input file for testing 
├── test_dpll_solver.py # Unit tests for DPLL solver 
└── README.md # Project documentation


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

3. Install dependencies if any (e.g., if you add any for testing).

## Usage

1. To solve a SAT problem:
    ```python
    from sat_problem import SATProblem
    from dpll_solver import DPLLSolver

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
   python test_dpll_solver.py
   ```
