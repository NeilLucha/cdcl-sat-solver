from .cnf import CNFFormula, Clause
from typing import Optional
class DPLL:
    def __init__(self, formula: CNFFormula):
        self.clauses = formula
        self.assignments = {} # Variable assignments
        self.calls = 0

        
    def literal_status(self, literal) -> Optional[bool]:
        if abs(literal) in self.assignments:
            value = self.assignments[abs(literal)]
            if (literal > 0 and value) or (literal < 0 and not value):
                return True
            else:
                return False
        return None

    def clause_status(self, clause: Clause) -> Optional[bool]:
        num_assigned = 0
        for literal in clause.literals:
            if abs(literal) in self.assignments:
                num_assigned += 1
                if self.literal_status(literal):
                    return True
        if num_assigned == len(clause):
            return False
        return None # Undecided
    
    def formula_status(self) -> Optional[bool]:
        num_satisfied = 0
        for clause in self.clauses:
            status = self.clause_status(clause)
            if status is True:
                num_satisfied += 1
            elif status is False:
                return False
        if num_satisfied == len(self.clauses):
            return True
        return None # Undecided

    def find_unit_literals(self):
        unit_literals = []

        for clause in self.clauses:
            unassigned_literal = None
            all_other_false = True

            for literal in clause.literals:
                status = self.literal_status(literal)

                if status is True:
                    all_other_false = False
                    break

                if status is None:
                    if unassigned_literal is None:
                        unassigned_literal = literal
                    else:
                        all_other_false = False
                        break

            if unassigned_literal is not None and all_other_false:
                unit_literals.append(unassigned_literal)

        return unit_literals

    
    
    def unit_propagate(self) -> bool:
        
        unit_literals = self.find_unit_literals()
        # print('unit literals: ', unit_literals)
        # print('assignments: ', self.assignments)
        while unit_literals:
            for lit in unit_literals:
                var = abs(lit)
                status = self.literal_status(lit)
                if status == False:
                    return False
                elif status == None:
                    self.assignments[var] = (lit>0)
                else:
                    continue
            
            unit_literals = self.find_unit_literals()
        # print('unit literals: ', unit_literals)
        # print('assignments: ', self.assignments)
        return True
    
    def solve(self) -> bool:
        
        self.calls += 1
        if self.calls % 100_000 == 0:
            print("Calls:", self.calls)

        
        if not self.unit_propagate():
            return False

        status = self.formula_status()
        if status is not None:
            return status

        # Choose ONE decision variable
        for var in range(1, self.clauses.num_vars + 1):
            if var not in self.assignments:
                chosen_var = var
                break

        saved = self.assignments.copy()

        # Try True
        self.assignments[chosen_var] = True
        if self.solve():
            return True

        # Backtrack, try False
        self.assignments = saved.copy()
        self.assignments[chosen_var] = False
        if self.solve():
            return True

        # Backtrack
        self.assignments = saved
        return False

