# CDCL SAT Solver

A from-scratch implementation of the Conflict-Driven Clause Learning (CDCL) algorithm for solving Satisfiability (SAT) problem, written in Python

NOTE: I have not tried testing the large_sat_test.cnf file to completion because I'm guessing it will take a VERY VERY large amount of time
However, judging from the fact that the number of learned clauses seems to be consistently growing, I would wager we can end up at a satisfying assignment if 
given enough time.

## Goals
- [x] Parsing DIMACS format
- [x] Implement a DPLL solver
- [x] Implement CDCL solver
- [ ] Try adding classical heuristics (like VSIDS) and other ML-based branching heuristics
- [ ] Evaluate performance

## To-Do List
- [x] Set up the Project
- [x] Start working on the code
- [x] Test DPLL
- [x] Debug DPLL code (if required)
- [x] Test CDCL
- [x] Debug CDCL

