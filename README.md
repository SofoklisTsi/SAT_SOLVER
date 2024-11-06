# SAT Solver

This project is an implementation of a SAT (Boolean Satisfiability) solver using the **DPLL (Davis-Putnam-Logemann-Loveland)** algorithm in Python.

## Project Structure

SAT SOLVER 
├── dpll_solver.py # DPLL algorithm implementation 
├── sat_problem.py # SAT problem representation 
├── pdf_clauses_and_results.txt # Input file for testing 
├── test_dpll_solver.py # Unit tests for DPLL solver 
└── README.md # Project documentation


## Features

- **DPLL Algorithm**: Implements the DPLL algorithm with optional pure literal elimination and unit propagation.
- **Logging and Decision Table**: Logs each decision step, including decision literals, implied literals, satisfied/contradicted clauses, and explanations.
- **Configurable Options**: Includes settings for using or skipping pure literal elimination.
- **Unit Tests**: Basic tests for the solver using `test_dpll_solver.py`.

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
    solver = DPLLSolver(problem, use_pure_literal=True)

    is_satisfiable = solver.solve(log_steps=True)
    print("Satisfiable:", is_satisfiable)

    # Print decision steps (optional)
    solver.print_steps()
    ```

2. **Testing**:
   Run tests to verify the solver works correctly:
   ```bash
   python test_dpll_solver.py
   ```
