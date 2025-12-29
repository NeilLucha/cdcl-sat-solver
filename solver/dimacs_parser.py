from solver.cnf import CNFFormula, Clause

class DIMACSParseError(Exception):
    pass

class DIMACS_Parser:
    def __init__(self, filename):
        self.filename = filename
        self.clauses = []
        self.num_clauses = 0
        self.num_vars = 0
        self.satisfiable = None
        self.read_dimacs()
        self.sanity_check()
        self.cnf = self.to_cnf()

    def read_dimacs(self):
        with open(self.filename, 'r') as f:
            curr_clause = []
            for line in f:
                line = line.strip()
                if line.startswith('c'):
                    continue # Comment Line
                elif line.startswith('p'):  
                    info = line.split()
                    self.num_vars = int(info[2])
                    self.num_clauses = int(info[3])
                else:
                    literals = list(map(int, line.split()))
                    for lit in literals:
                        if lit == 0:
                            if curr_clause:
                                self.clauses.append(curr_clause)
                                curr_clause = []
                        else:
                            if abs(lit) > self.num_vars:
                                raise DIMACSParseError(f"Literal {lit} exceeds declared number of variables {self.num_vars}.")
                            curr_clause.append(lit)
            if curr_clause:
                self.satisfiable = False

    def sanity_check(self):
        if self.satisfiable is False:
            return
        assert len(self.clauses) == self.num_clauses, "Number of clauses does not match the header."
        for clause in self.clauses:
            assert len(clause) > 0, "Empty clause found."

    def to_cnf(self) -> CNFFormula:
        cnf = CNFFormula(self.num_vars)
        if self.satisfiable is not None:
            cnf.satisfiable = self.satisfiable
        for clause in self.clauses:
            cnf.add_clause(Clause(clause))
        return cnf