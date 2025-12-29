from .cnf import CNFFormula, Clause
from .dimacs_parser import DIMACS_Parser, DIMACSParseError

def main():
    filename = 'tests/dimacs_parsing/basic.cnf'  # Replace with your DIMACS file path
    try:
        parser = DIMACS_Parser(filename)
        cnf_formula: CNFFormula = parser.cnf
        print(f"Parsed CNF Formula: {cnf_formula}")
        if cnf_formula.satisfiable is True:
            print("The formula is satisfiable.")
        elif cnf_formula.satisfiable is False:
            print("The formula is unsatisfiable.")
        else:
            print("The satisfiability of the formula is unknown.")
        
        print("CNF in DIMACS format:")
        print(cnf_formula.to_dimacs())
    except DIMACSParseError as e:
        print(f"Error parsing DIMACS file: {e}")

main()