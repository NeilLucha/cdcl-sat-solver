from solver.dimacs_parser import DIMACS_Parser, DIMACSParseError
from solver.cdcl import CDCL

try:
    parser = DIMACS_Parser('tests/cnf_files/large_sat_test.cnf')
    cnf_formula = parser.cnf
    cdcl_solver = CDCL(cnf_formula)
    is_sat = cdcl_solver.solve()
    if is_sat:
        print("Satisfiable with assignment: ", is_sat)
        cdcl_solver.assignments = {i:cdcl_solver.assignments[i] for i in sorted(cdcl_solver.assignments)}
        print("Satisfying assignment:", cdcl_solver.assignments)
    else:
        print("Unsatisfiable")

except DIMACSParseError as e:
    print('DIMACS Parsing Error: ', e)