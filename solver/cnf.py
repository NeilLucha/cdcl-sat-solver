from typing import List

# Define Clauses as objects
class Clause:
    def __init__(self, literals: List[int]):
        self.literals = literals

    def __len__(self):
        return len(self.literals)

    def __repr__(self):
        return f"Clause({self.literals})"


# Define CNF formulae as lists of 'Clause' class objects
class CNFFormula:
    def __init__(self, num_vars: int):
        self.num_vars = num_vars
        self.clauses: List[Clause] = []
        self.satisfiable: bool = None #None = unknown, True = satisfiable, False = unsatisfiable


    
    
    def add_clause(self, clause: Clause):
        self.clauses.append(clause)
        
    # Convert CNF to DIMACS format
    def to_dimacs(self) -> str:
        lines = [f"p cnf {self.num_vars} {len(self.clauses)}"]
        for clause in self.clauses:
            line = ' '.join(map(str, clause.literals)) + ' 0'
            lines.append(line)
        return '\n'.join(lines)

    def __len__(self):
        return len(self.clauses)

    def __repr__(self):
        return f"CNF(num_vars={self.num_vars}, clauses={len(self.clauses)})"
    
    def __iter__(self):
        return iter(self.clauses)
