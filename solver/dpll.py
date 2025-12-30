from .cnf import CNFFormula, Clause
from typing import Optional
class DPLL:
    def __init__(self, clauses):
        self.clauses = CNFFormula(clauses)
        self.assignments = {} # Variable assignments
        
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
            unassigned = None
            satisfied = False
            for literal in clause.literals:
                status = self.literal_status(literal)
                if status is None:
                    if unassigned is None:
                        unassigned = literal
                    else:
                        break
                elif status:
                    satisfied = True
                    break
            if not satisfied and unassigned is not None:
                unit_literals.append(unassigned)
        return unit_literals
    
    
    def unit_propagate(self) -> bool:
        unit_literals = self.find_unit_literals()
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
        return True
    
    def solve(self) -> bool:
        valid = self.unit_propagate()
        if not valid:
            return False #Backtrack
        if len(self.assignments) == self.clauses.num_vars:
            return True #All variables assigned successfully
        
        # Choose a variable to branch on
        unassigned_vars = [v for v in range(1, self.clauses.num_vars + 1) if v not in self.assignments]
        for chosen_var in unassigned_vars:
            saved_assignments = self.assignments.copy()
            # Try assigning True
            self.assignments[chosen_var] = True
            if self.solve():
                return True
            # Backtrack and try False
            self.assignments = saved_assignments
            self.assignments[chosen_var] = False
            if self.solve():
                return True
            # Backtrack
            self.assignments = saved_assignments
        return False
