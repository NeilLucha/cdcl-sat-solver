from solver.dimacs_parser import DIMACS_Parser, DIMACSParseError
from solver.dpll import DPLL

try:
    parser = DIMACS_Parser('tests/cnf_files/large_sat_test.cnf')
    cnf_formula = parser.cnf
    dpll_solver = DPLL(cnf_formula)
    is_sat = dpll_solver.solve()
    if is_sat:
        print("Satisfiable with assignment: ", is_sat)
        dpll_solver.assignments = {i:dpll_solver.assignments[i] for i in sorted(dpll_solver.assignments)}
        print("Satisfying assignment:", dpll_solver.assignments)
        print('Statistics:')
        print(f'  Number of decisions: {dpll_solver.num_decisions}')
        print(f'  Number of conflicts: {dpll_solver.num_conflicts}')
        print(f'  Number of propagations: {dpll_solver.num_propagations}')
        print(f'  Maximum decision level reached: {dpll_solver.max_depth}')
    else:
        print("Unsatisfiable")

except DIMACSParseError as e:
    print('DIMACS Parsing Error: ', e)