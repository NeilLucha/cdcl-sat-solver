from solver.dimacs_parser import DIMACS_Parser, DIMACSParseError
from solver.dpll import DPLL

parser = DIMACS_Parser('tests/cnf_files/sample_sat_1.cnf')
cnf_formula = parser.cnf
dpll_solver = DPLL(cnf_formula)
result = dpll_solver.solve()
if result is not None:
    print("Satisfiable with assignment:", result)
    print("Satisfying assignment:", dpll_solver.assignments())
else:
    print("Unsatisfiable")