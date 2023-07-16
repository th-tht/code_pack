from typing import Dict, Tuple, Optional
import pyomo.environ as pyo 
from itertools import chain
from . import mytyping, Unpack_data , pinch_energy

class Transshipment(Unpack_data):
    
    def __init__(self, data) -> None:
        
        self.data = data
        super(Transshipment, self).__init__(data)

        self.idx_i = self.thin.keys()
        self.idx_j = self.tcin.keys()   
        
        self.qhmin, self.qhmax, self.qcmin, self.qcmax = \
        self.plm_cal(self.thin, self.thout, self.fh, self.tcin, self.tcout, self.fc, self.HRAT_MIN, self.HRAT_MAX, self.Max_Energy)
        #print(self.qhmin, self.qhmax, self.qcmin, self.qcmax)
        self.ech = {i: self.fh[i] * (self.thin[i] - self.thout[i]) for i in self.idx_i}
        self.ecc = {j: self.fc[j] * (self.tcout[j] - self.tcin[j]) for j in self.idx_j}
        
        self.T_inter_d = [self.thin[i] for i in self.idx_i] + [self.thout[i] for i in self.idx_i] \
            + [self.tcin[j] + self.EMAT for j in self.idx_j] \
            + [self.tcout[j] + self.EMAT for j in self.idx_j] + [self.thuin, self.tcuin + self.EMAT]
        
        self.T_inter_d = list(set(self.T_inter_d))
        thuout_d, tcuout_d = self.thuout, self.tcuout
        if self.thuin == self.thuout: thuout_d = self.thuin - 1 # If The inlet and outlet temperatures of HU/CU are in the same, a small temperature difference is assumed.
        if self.tcuin == self.tcuout: tcuout_d = self.tcuin + 1
        self.T_inter_d += [thuout_d, tcuout_d + self.EMAT]
        self.T_inter_d.sort(reverse = True)
        
        self.idx_inter_loca = [i for i in range(1, len(self.T_inter_d) + 1)]
        self.idx_inter = self.idx_inter_loca[:-1]
        
        # Parameters
        # The heat duty of each stream in different intervals.
        self.Qtrans_H = {(i,inter): 0 for inter in self.idx_inter for i in self.idx_i}
        self.Qtrans_C = {(j,inter): 0 for inter in self.idx_inter for j in self.idx_j} 

        # If the stream go through the interval, it has a heat duty in this interval.
        for inter in self.idx_inter: 
            for i in self.idx_i:
                if self.thin[i] >= self.T_inter_d[inter - 1] and self.thout[i] <= self.T_inter_d[inter]:
                    self.Qtrans_H[i, inter] = self.fh[i] * (self.T_inter_d[inter - 1] - self.T_inter_d[inter])
            for j in self.idx_j:
                if self.tcout[j] + self.EMAT >= self.T_inter_d[inter - 1] and self.tcin[j] + self.EMAT <= self.T_inter_d[inter]:
                    self.Qtrans_C[j, inter] = self.fc[j] * (self.T_inter_d[inter - 1] - self.T_inter_d[inter])
        
        self.model = self.transship_model()
        # fix_set
        self.fix_set = dict()

    @staticmethod     
    def plm_cal(thin: Dict, thout, fh, tcin: Dict, tcout, fc, HRAT_MIN: int, HRAT_MAX = -1, Max_Energy = -1) -> Tuple[int]:

        # pinch candidate
        # lower bound
        qhmin, qcmin = pinch_energy(thin, thout, fh, tcin, tcout, fc, HRAT_MIN)
        
        #HRAT_MAX = -1
        
        if HRAT_MAX != -1:
            qhmax, qcmax = pinch_energy(thin, thout, fh, tcin, tcout, fc, HRAT_MAX)
            
        elif Max_Energy != -1:
            qhmax = Max_Energy
            qcmax = Max_Energy + sum(fh[i] * (thin[i] - thout[i]) for i in thin) \
                - sum(fc[j] * (tcout[j] - tcin[j]) for j in tcin)     
        else:
            qhmax = sum(fc[j] * (tcout[j] - tcin[j]) for j in tcin)
            qcmax = sum(fh[i] * (thin[i] - thout[i]) for i in thin)

        #print(qhmax,qcmax)
        return qhmin, qhmax, qcmin, qcmax
   
    def __getstate__(self):
        return {"data": self.data}

    def __setstate__(self, state):
        self.data = state["data"]
        self.__init__(self.data)

    # 初始化部分模型，如热残留量，即流股在不同温度区间的焓变
    def transship_model(self) -> pyo.ConcreteModel:
        
        # 初始化部分模型
        idx_inter_loca = self.idx_inter_loca 
        idx_inter = self.idx_inter
        
        # Variables
        model = pyo.ConcreteModel()
        model.rt_energy = pyo.Var(idx_inter_loca, domain = pyo.NonNegativeReals) 
        model.r_energy = pyo.Var(self.idx_i, idx_inter_loca, domain =pyo.NonNegativeReals)
        model.r_energy_hu = pyo.Var(idx_inter_loca, domain = pyo.NonNegativeReals, bounds = (0, self.qhmax))
        
        model.qtrans_HU = pyo.Var(idx_inter, bounds = (0,self.qhmax))
        model.qtrans_CU = pyo.Var(idx_inter, bounds = (0,self.qcmax))        
        model.tot_energy_balance = pyo.ConstraintList()
        model.Emin = pyo.ConstraintList()
        model.Emax = pyo.ConstraintList()
                
        # 总能量约束
        for inter in idx_inter:
            model.tot_energy_balance.add(model.rt_energy[inter] + sum(self.Qtrans_H[i, inter] for i in self.idx_i) 
                                         + model.qtrans_HU[inter] == model.rt_energy[inter + 1] 
                                         + sum(self.Qtrans_C[j, inter] for j in self.idx_j) + model.qtrans_CU[inter])
            
        model.Emin.add(sum(model.qtrans_HU[inter] for inter in idx_inter) >= self.qhmin)
        model.Emax.add(sum(model.qtrans_HU[inter] for inter in idx_inter) <= self.qhmax)
        # 能量进出口热量固定值
        model.rt_energy[1].fix(0)
        model.rt_energy[idx_inter_loca[-1]].fix(0)
        for i in self.idx_i:
            model.r_energy[i, 1].fix(0)
            model.r_energy[i, idx_inter_loca[-1]].fix(0)
        model.r_energy_hu[1].fix(0)
        model.r_energy_hu[idx_inter_loca[-1]].fix(0)

        # 单独热量衡算
        def qxtrans_bounds(model, i, j, inter):
            return (0, min(self.ech[i], self.ecc[j]))
        def qxtrans_CU_bounds(model, i, inter):
            return (0, self.ech[i])	     
        def qxtrans_HU_bounds(model, j, inter):
            return (0, self.ecc[j])           
        model.qxtrans = pyo.Var(self.idx_i, self.idx_j, self.idx_inter, bounds = qxtrans_bounds)  # Heat exchanged between streams i and j in interval *inter*
        model.qxtrans_CU = pyo.Var(self.idx_i, idx_inter, bounds = qxtrans_CU_bounds) # Heat exchanged between stream i and the CU stream
        model.qxtrans_HU = pyo.Var(self.idx_j, idx_inter, bounds = qxtrans_HU_bounds) # Heat exchanged between stream j and the HU stre

        model.i_energy_balance = pyo.ConstraintList()
        model.hu_energy_balance = pyo.ConstraintList()
        model.j_energy_balance = pyo.ConstraintList()
        model.cu_energy_balance = pyo.ConstraintList()
    
        for inter in idx_inter:
            for i in self.idx_i:
                model.i_energy_balance.add(model.r_energy[i, inter] + self.Qtrans_H[i, inter] \
                    == model.r_energy[i, inter + 1] + sum(model.qxtrans[i, j, inter] for j in self.idx_j) 
                    + model.qxtrans_CU[i, inter])
            
            for j in self.idx_j:
                model.j_energy_balance.add(sum(model.qxtrans[i, j, inter] for i in self.idx_i) 
                                            + model.qxtrans_HU[j, inter] == self.Qtrans_C[j, inter])
            
            model.hu_energy_balance.add(model.r_energy_hu[inter] + model.qtrans_HU[inter] \
                    == model.r_energy_hu[inter + 1] + sum(model.qxtrans_HU[j, inter] for j in self.idx_j))
            model.cu_energy_balance.add(sum(model.qxtrans_CU[i, inter] for i in self.idx_i) == model.qtrans_CU[inter])
    
        # 逻辑约束
        model.ytrans = pyo.Var(self.idx_i, self.idx_j, domain = pyo.Binary) # = 1 when the streams i and j match
        model.ytrans_HU = pyo.Var(self.idx_j, domain = pyo.Binary) # = 1 when the streams j and the HU stream match
        model.ytrans_CU = pyo.Var(self.idx_i, domain = pyo.Binary) # = 1 when the streams i and the CU stream match
    
        model.logic = pyo.ConstraintList()
        model.logic_CU = pyo.ConstraintList()
        model.logic_HU = pyo.ConstraintList()
        
        for i in self.idx_i:
            for j in self.idx_j:
                model.logic.add(sum(model.qxtrans[i, j, inter] for inter in idx_inter) 
                                <= min(self.ech[i], self.ecc[j]) * model.ytrans[i,j])
        for i in self.idx_i:
            model.logic_CU.add(sum(model.qxtrans_CU[i, inter] for inter in idx_inter) 
                               <= self.ech[i] * model.ytrans_CU[i])
        for j in self.idx_j:
            model.logic_HU.add(sum(model.qxtrans_HU[j, inter] for inter in idx_inter) 
                               <= self.ecc[j] * model.ytrans_HU[j])
         
        model.Nmin_cons = pyo.Constraint(expr = 
                  sum(model.ytrans[i, j] for i in self.idx_i for j in self.idx_j) 
                + sum(model.ytrans_CU[i] for i in self.idx_i)\
                + sum(model.ytrans_HU[j] for j in self.idx_j) <= self.Nmin_max)
             
        #heat_cross = sum(model.rt_energy[inter] for inter in self.idx_inter)
    
        model.obj = pyo.Objective(expr = sum(model.qxtrans_HU[j, inter] for j in self.idx_j for inter in idx_inter))
        
        model.obj1 = pyo.Objective(expr = sum(model.qxtrans_HU[j, inter] for j in self.idx_j for inter in idx_inter), 
                                   sense = pyo.maximize)
        model.obj1.deactivate()
        
        qh, _ = pinch_energy(self.thin, self.thout, self.fh, self.tcin, self.tcout, self.fc, self.HRAT_MAX)
        model.max_hu = pyo.Constraint(expr = sum(model.qtrans_HU[inter] for inter in self.idx_inter) <= qh)
        model.max_hu.deactivate()
        
        return model
                  
    def fix(self, match: mytyping.match, value: int) -> None:
        h,c = match
        if h == 'HU':
            self.model.ytrans_HU[c].fix(value)
        elif c == 'CU':
            self.model.ytrans_CU[h].fix(value)
        else:
            self.model.ytrans[h,c].fix(value)
        
        self.fix_set[match] = value

    def unfix(self, match: mytyping.match) -> None:
        h,c = match
        if h == 'HU':
            self.model.ytrans_HU[c].unfix()
        elif c == 'CU':
            self.model.ytrans_CU[h].unfix()
        else:
            self.model.ytrans[h,c].unfix()
        
        del self.fix_set[match]

    def c_Nmin(self, pn: mytyping.Proto_network) -> bool:
        
        def find(key):
            father = key
            while unit[father] != -1:
                father = unit[father]
            if key != father: unit[key] = father
            return father

        def add(key1, key2):
            key1 = find(key1)
            key2 = find(key2)
            if key1 != key2:
                unit[key2] = key1
                
        unit = {key : -1 for key in chain(self.idx_i, self.idx_j, ['HU','CU'])}
        for k1, k2 in pn:
            add(k1, k2)
        
        return len(pn) == len(unit) - sum(1 for v in unit.values() if v == -1)   

    def exclude(self, *pn: mytyping.Proto_network) -> Optional[mytyping.Proto_network]:
                
        def add_cut(model, pn):
            
            pn, expr = set(pn), 0
            for h in self.idx_i:
                for c in self.idx_j:
                    expr += 1 - model.ytrans[h,c] if (h,c) in pn else model.ytrans[h,c]
                    
                expr += 1 - model.ytrans_CU[h] if (h,"CU") in pn else model.ytrans_CU[h]
            
            for c in self.idx_j:
                expr += 1 - model.ytrans_HU[c] if ("HU",c) in pn else model.ytrans_HU[c] 
            
            temp_model.exclude.add(expr >= 1)
            
        temp_model = self.transship_model()
        temp_model.exclude = pyo.ConstraintList()
        
        for (h, c),value in self.fix_set.items():
            if h == 'HU':
                temp_model.ytrans_HU[c].fix(value)
            elif c == 'CU':
                temp_model.ytrans_CU[h].fix(value)
            else:
                temp_model.ytrans[h,c].fix(value)
        
        for p in pn:
            add_cut(temp_model, p)

        results = self.solve(temp_model)
        #results = pyo.SolverFactory("gurobi", solver_io="python").solve(temp_model, options = {'NonConvex' : 2})
        
        while results.solver.termination_condition == pyo.TerminationCondition.optimal:
            
            pn = []
            for h in self.idx_i:
                for c in self.idx_j:
                    if temp_model.ytrans[h,c]() > 0:
                        pn.append((h,c))
                if temp_model.ytrans_CU[h]() > 0:
                    pn.append((h,'CU'))
            for c in self.idx_j:
                if temp_model.ytrans_HU[c]() > 0:
                    pn.append(('HU',c))
            
            if self.c_Nmin(pn):
                return pn, temp_model.obj()
            
            add_cut(temp_model, pn)
            results = self.solve(temp_model)
        
        return None
            
    def is_feasible(self) -> Optional[mytyping.Proto_network]:
        
        results = self.solve(self.model)
        
        if results is not None and results.solver.status == pyo.SolverStatus.ok and results.solver.termination_condition == pyo.TerminationCondition.optimal:
            pn = []
            for h in self.idx_i:
                for c in self.idx_j:
                    if self.model.ytrans[h,c]() > 0:
                        pn.append((h,c))
                if self.model.ytrans_CU[h]() > 0:
                    pn.append((h,'CU'))
            for c in self.idx_j:
                if self.model.ytrans_HU[c]() > 0:
                    pn.append(('HU',c))
                    
            #if self.c_Nmin(pn):
                
            return pn, self.model.obj()
            
            #return self.exclude(pn)
            
        return None
    
    def Larger(self) -> mytyping.Loads:
        
        self.model.obj.deactivate()
        self.model.obj1.activate()
        
        self.model.max_hu.activate()
        
        self.solve(self.model)
        
        self.model.max_hu.deactivate()
        
        loads = dict()
        for h in self.idx_i:
            for c in self.idx_j:
                if self.model.ytrans[h,c]() > 0:
                    loads[h,c] = sum(self.model.qxtrans[h,c,itv]() for itv in self.idx_inter)
            if self.model.ytrans_CU[h]() > 0:
                loads[h,'CU'] = sum(self.model.qxtrans_CU[h,itv]() for itv in self.idx_inter)
        for c in self.idx_j:
            if self.model.ytrans_HU[c]() > 0:
                loads['HU',c] = sum(self.model.qxtrans_HU[c,itv]() for itv in self.idx_inter)
                        
        self.model.obj1.deactivate()
        self.model.obj.activate()
        
        return loads
        
    def solve(self, model):
        
        try:
            #results = pyo.SolverFactory('gams').solve(model, solver = 'cplex')
            results = pyo.SolverFactory("gurobi", solver_io="python").solve(model, options = {'NonConvex' : 2})
        except:
            #model.display()
            #print(results)
            #exit()
            return None

        return results
            
    
        
        
    





