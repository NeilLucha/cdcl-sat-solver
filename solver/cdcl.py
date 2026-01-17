from .cnf import CNFFormula, Clause
from typing import Optional, List, Tuple, Dict

class CDCL:
    def __init__(self, cnf: CNFFormula):
        self.cnf = cnf
        self.assignments: Dict[int, bool] = {}
        self.trail: List[int] = [] # List of (literal, decision_level, antecedent_clause)
        self.decision_level = 0
        self.tried_phase: Dict[int, bool] = {}
        self.vsids_scores: Dict[int, float] = {i: 0.0 for i in range(1, cnf.num_vars + 1)}
        self.decay_factor: float = 0.95  # or 0.95–0.99
        self.num_decisions = 0
        self.num_conflicts = 0
        self.num_propagations = 0
        self.num_learned_clauses = 0
        self.max_decision_level = 0


        
        

    def literal_status(self, literal: int) -> Optional[bool]:
        var = abs(literal)
        if var not in self.assignments:
            return None
        value = self.assignments[var]
        return value if literal > 0 else not value
    
    def clause_status(self, clause: Clause) -> Optional[bool]:
        has_unassigned = False
        for lit in clause.literals:
            status = self.literal_status(lit)
            if status is True:
                return True
            if status is None:
                has_unassigned = True
        
        if has_unassigned:
            return None
        return False
    
    def find_unit_clauses(self):
        '''
        Clause is unit iff clause is NOT satisfied, exactly 1 literal unassigned and all other literals False
        
        Returns list of (unit_literal, clause) pairs
        '''
        units = []
        for clause in self.cnf.clauses:
            unassigned_lit = None
            all_false = True
            
            for lit in clause.literals:
                status = self.literal_status(lit)
                if status == True: # Not unit clause (Clause already True)
                    all_false = False
                    break
                if status is None:
                    if unassigned_lit == None:
                        unassigned_lit = lit
                    else: # Not unit clause (Multiple Unassigned literals)
                        all_false = False
                        break
            if all_false and unassigned_lit is not None:
                units.append((unassigned_lit, clause))
        return units
    
    def assign(self, literal: int, antecedent: Optional[Clause] = None):
        '''
        Assigns a literal at the current decision level.
        Returns False if a conflict arises, else True
        '''
        var = abs(literal)
        value = literal > 0
        if var in self.assignments:
            if self.assignments[var] != value:
                return False  # Conflict
            return True  # Already assigned consistently
        
        self.assignments[var] = value
        self.trail.append((literal, self.decision_level, antecedent))
        if antecedent is not None:
            self.num_propagations += 1
        return True
    
    def unit_propagate(self):
        while True:
            units = self.find_unit_clauses()
            if not units:
                return None

            for lit, clause in units:
                status = self.clause_status(clause)
                if status is False:
                    # print(f"Conflict detected in unit_propagate! Clause: {clause.literals}")
                    return clause
                if status is None:
                    # print(f"Unit propagate assigning literal {lit} from clause {clause.literals}")
                    check = self.assign(lit, clause)
                    
                    if not check:
                        # print(f"Conflict during assignment of literal {lit}")
                        return clause


    
    def decide(self):
        """
        Makes a decision assignment at a new decision level using VSIDS.
        """
        unassigned_vars = [v for v in range(1, self.cnf.num_vars + 1) if v not in self.assignments]
        if not unassigned_vars:
            return  # Nothing to decide
        
        # Pick the variable with the highest VSIDS score
        var = max(unassigned_vars, key=lambda v: self.vsids_scores[v])
        
        self.decision_level += 1
        self.num_decisions += 1
        self.max_decision_level = max(self.max_decision_level, self.decision_level)
        # Flip phase if we've tried True before
        value = True
        if var in self.tried_phase:
            value = not self.tried_phase[var]
        self.tried_phase[var] = value
        literal = var if value else -var
        check = self.assign(literal)
        assert check, "Conflict on decision assignment"

        
    def find_conflict(self) -> Optional[Clause]:
        '''
        Checks for conflicts in the current assignments
        Returns the first conflicting clause found, else None
        '''
        for clause in self.cnf.clauses:
            status = self.clause_status(clause)
            if status == False:
                return clause
        return None
    
    def backjump(self, level: int):
        # print(f"Backjumping from level {self.decision_level} to level {level}")
        new_trail = []
        new_assignments = {}
        for lit, dl, antecedent in self.trail:
            if dl <= level:
                new_trail.append((lit, dl, antecedent))
                new_assignments[abs(lit)] = lit > 0
        self.trail = new_trail
        self.assignments = new_assignments
        self.decision_level = level

        
    def trail_level(self, var: int) -> int:
        '''
        Returns the decision level at which the variable was assigned
        '''
        for lit, dl, _ in reversed(self.trail):
            if abs(lit) == var:
                return dl
        return -1  # Variable not assigned

    def resolve(self, clause1: List[int], clause2: List[int], literal: int) -> List[int]:
        '''
        Resolves two clauses on the given pivot literal
        Returns the resulting clause as a list of literals
        '''
        resolvent = set()
        for lit in clause1:
            if abs(lit) != abs(literal):
                resolvent.add(lit)
        for lit in clause2:
            if abs(lit) != abs(literal):
                resolvent.add(lit)
        return list(resolvent)
    
    def analyze_conflict(self, conflict_clause: Clause):
        '''
        Performs conflict analysis and learns a new clause and backjump level
        '''
        self.num_conflicts += 1
        learned = conflict_clause.literals.copy()
        while True:
            level_count = sum(1 for lit in learned if self.trail_level(abs(lit)) == self.decision_level)
            if level_count <= 1:
                break
            # print('HERE')
            for lit, dl, antecedent in reversed(self.trail):
                # print('ANALYZE LOOP ', learned, lit, dl)
                if abs(lit) in [abs(l) for l in learned] and dl == self.decision_level:
                    if antecedent is not None:
                        # print('TEST RESOLVE ENTER')
                        learned = self.resolve(learned, antecedent.literals, abs(lit))
                    break
        backjump_level = max((self.trail_level(abs(lit)) for lit in learned if self.trail_level(abs(lit)) < self.decision_level), default=0)
        return learned, backjump_level
    
    def bump_vsids(self, clause_literals: List[int], constant: float = 1.0):
        for lit in clause_literals:
            var = abs(lit)
            self.vsids_scores[var] += constant  # or some constant increment

    def decay_vsids(self):
        for var in self.vsids_scores:
            self.vsids_scores[var] *= self.decay_factor

    def solve(self) -> bool:
        """
        CDCL Solver main loop with sparse debug prints.
        Returns True if satisfiable, False if unsatisfiable.
        """
        iteration = 0

        while True:
            iteration += 1

            # Sparse debug prints (every 100 iterations)
            # if iteration % 100 == 0:
            #     print(f"\n--- ITERATION {iteration} ---")
            #     print(f"Decision Level: {self.decision_level}")
            #     print(f"Assignments: {len(self.assignments)} variables assigned")
            #     print(f"Trail length: {len(self.trail)}")
            #     print(f'------------------------ Number of Clauses: {len(self.cnf.clauses)} ------------------------')

            # --- Unit Propagation ---
            conflict = self.unit_propagate()

            if conflict is None:
                conflict = self.find_conflict()

            if conflict is not None:
                if self.decision_level == 0:
                    self.cnf.satisfiable = False
                    return False

                learned_clause, backjump_level = self.analyze_conflict(conflict)
                self.bump_vsids(learned_clause)
                self.decay_vsids()
                self.backjump(backjump_level)
                self.cnf.add_clause(Clause(learned_clause))
                self.num_learned_clauses += 1
                continue

            
            if conflict is not None:
                if self.decision_level == 0:
                    self.cnf.satisfiable = False
                    # print("Conflict at level 0 → UNSAT")
                    return False  # Unsatisfiable
                
                # Analyze conflict, backjump, learn clause
                learned_clause, backjump_level = self.analyze_conflict(conflict)
                self.bump_vsids(learned_clause)
                self.decay_vsids()
                # print(f"Learned clause: {learned_clause}, backjump to level {backjump_level}")

                # if iteration % 10000 == 0:
                #     print(f"Conflict detected! Learned clause: {learned_clause}, backjumping to level {backjump_level}")
                self.backjump(backjump_level)
                self.cnf.add_clause(Clause(learned_clause))
                self.num_learned_clauses += 1
                continue

            # --- Check if all variables are assigned ---
            if len(self.assignments) == self.cnf.num_vars:
                # Verify all clauses are satisfied
                all_satisfied = True
                for clause in self.cnf.clauses:
                    status = self.clause_status(clause)
                    if status is not True:
                        all_satisfied = False
                        # Treat this as a conflict
                        conflict_clause = clause
                        break

                if all_satisfied:
                    self.cnf.satisfiable = True
                    # print("All variables assigned → SATISFIABLE!")
                    return True
                else:
                    # This should never happen if propagation is correct
                    raise RuntimeError(
                        "All variables assigned but formula unsatisfied — "
                        "conflict should have been detected during propagation"
                    )


            # --- Make a decision for the next unassigned variable ---
            self.decide()

