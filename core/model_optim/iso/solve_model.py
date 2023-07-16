from itertools import chain
import numpy as np
import pyomo.environ as pyo
import sympy as sym
from ..model import model


class Heat_exchanger_network(model): 
    
    def __init__(self, data) -> None:
        
        super(Heat_exchanger_network, self).__init__(data)
            
    # 通过求解线性方程组得到个换热器流量
    def heat_load_solve(self):
    
        # 初始化需要计算的流股
        def Generate_stream_idx(match) -> dict:
            
            def dfs(h,c):
                if (h,c) in vis:
                    return
                vis.add((h,c))
                t.append((h,c))
                for cc in self.heat_match[h]:
                    dfs(h,cc)
                for hh in self.heat_match[c]:
                    dfs(hh,c)
            
            vis,parts = set(), []
            for h,c in match:
                if (h,c) in vis: continue
                t = []
                dfs(h,c)
                parts.append(t)
            
            idx = []
            #print(parts)
            for part in parts:
                t = set()
                for h,c in part:
                    t.add(h); t.add(c)
                if len(t) > len(part) and 'CU' in t:
                    t.discard('CU')
                    idx.append(list(t))
                else:
                    idx.append(list(t)[:-1])
            return {st : i for i,st in enumerate(chain(*idx))}
            
        self.stream_idx = Generate_stream_idx(self.q.keys())
        
        length = len(self.q_idx)
        self.A = np.zeros((length, length))
        
        for st, idx in self.stream_idx.items():
            if st[0] == 'H':
                for c in self.heat_match[st]:
                    self.A[idx][self.q_idx[st,c]] = 1
            else:
                for h in self.heat_match[st]:
                    self.A[idx][self.q_idx[h,st]] = 1
        
        self.C = np.zeros(length)
        for h in self.thin.keys():
            if h in self.stream_idx:
                self.C[self.stream_idx[h]] = (self.thin[h] - self.thout[h])*self.fh[h]
        for c in self.tcin.keys():
            if c in self.stream_idx:
                self.C[self.stream_idx[c]] = (self.tcout[c] - self.tcin[c])*self.fc[c]
            
        self.D = np.zeros(length, dtype = sym.Symbol)
        for h in self.thin.keys():
            if h in self.stream_idx:
                self.D[self.stream_idx[h]] = sym.Float((self.thin[h] - self.thout[h])*self.fh[h])
        for c in self.tcin.keys():
            if c in self.stream_idx:
                self.D[self.stream_idx[c]] = sym.Float((self.tcout[c] - self.tcin[c])*self.fc[c])
                   
    def update_and_solve(self, hu):

        if 'HU' in self.stream_idx:
            self.C[self.stream_idx['HU']] = hu
        q = np.linalg.solve(self.A, self.C)
        for key in self.q_idx.keys():
            self.q[key] = q[self.q_idx[key]]
            
        # 更新各级温度
        return self.cal_TAC()
                  
    def bounder_solve(self, model = None, maxi = False):
        
        if maxi:
            model.obj_min.deactivate()
            model.obj_max.activate()
            #results = pyo.SolverFactory('gams').solve(model, solver = 'baron',  add_options=['option optcr=0.001'])
            results = pyo.SolverFactory("gurobi", solver_io="python").solve(model, options = {'NonConvex' : 2})#,tee = True)
            
            if results.solver.termination_condition != pyo.TerminationCondition.infeasible:
                return model.hu()
            return None
        
        else:
            model.obj_max.deactivate()
            model.obj_min.activate()
            
            #results = pyo.SolverFactory('gams').solve(model, solver = 'baron',add_options=['option optcr=0.001'])
            results = pyo.SolverFactory("gurobi", solver_io="python").solve(model, options = {'NonConvex' : 2})#,tee = True)
            
            if results.solver.termination_condition != pyo.TerminationCondition.infeasible:
                
                for key in self.q_idx.keys():
                    self.q[key] = model.q[key]()
                
                return model.hu()
            
            return None
            
    def bounder_model(self):
              
        model = pyo.ConcreteModel()
        
        idx_i,idx_j = list(self.thin.keys()), list(self.tcin.keys())
        hk = [(h,i) for h in idx_i for i in range(1, len(self.gather_split[h]) + 2)] 
        ck = [(c,j) for c in idx_j for j in range(1, len(self.gather_split[c]) + 2)] 
        
        hl = {h : len(self.gather_split[h]) + 1 for h in idx_i}
        cl = {c : len(self.gather_split[c]) + 1 for c in idx_j}
    
        # variable
        model.th = pyo.Var(hk, domain = pyo.PositiveReals)
        model.tc = pyo.Var(ck, domain = pyo.PositiveReals)
        
        heat_match = self.heat_match
        model.hu = pyo.Var(domain = pyo.NonNegativeReals)
        CU = sum(self.fh[i]*(self.thin[i]-self.thout[i]) for i in self.thin.keys()) \
            + sum(self.fc[j]*(self.tcin[j]-self.tcout[j]) for j in self.tcin.keys()) + model.hu
        
        model.q = pyo.Var(list(self.q_idx.keys()), bounds = (0.01, None))
        
        # l流股总热量平衡
        model.q_equations = pyo.ConstraintList()
        for i in idx_i:
            model.q_equations.add(sum(model.q[i,j] for j in heat_match[i]) - self.fh[i]*(self.thin[i] - self.thout[i]) == 0)
        for j in idx_j:
            model.q_equations.add(sum(model.q[i,j] for i in heat_match[j]) - self.fc[j]*(self.tcout[j] - self.tcin[j]) == 0)
        model.q_equations.add(sum(model.q['HU',j] for j in heat_match['HU']) - model.hu == 0)
        model.q_equations.add(sum(model.q[i,'CU'] for i in heat_match['CU']) - CU == 0)
        

        # 每级温度
        model.t_equations = pyo.ConstraintList()
        for h in idx_i:
            
            model.th[h,1].fix(self.thin[h])
            for k, g in enumerate(self.gather_split[h], 1):
                model.t_equations.add(self.fh[h]*(model.th[h,k] - model.th[h,k+1]) - sum(model.q[h,c] for c in g) == 0)
            
            if (h,'CU') in self.q:
                model.t_equations.add(self.fh[h]*(model.th[h, hl[h]] - self.thout[h]) - model.q[h,'CU'] == 0)
            else:
                model.t_equations.add(model.th[h, hl[h]] - self.thout[h] == 0)
        
        for c in idx_j:
            
            model.tc[c, cl[c]].fix(self.tcin[c])
            
            if ('HU',c) in self.q:
                model.t_equations.add(self.fc[c]*(self.tcout[c] - model.tc[c,1]) - model.q['HU',c] == 0)
            else:
                model.t_equations.add(self.tcout[c] - model.tc[c,1] == 0)
                
            for k, g in enumerate(self.gather_split[c], 1):
                model.t_equations.add(self.fc[c]*(model.tc[c,k] - model.tc[c,k+1]) - sum(model.q[h,c] for h in g) == 0)
                    
        # 传热温差约束
        model.t_diff = pyo.ConstraintList()
        for h,c in self.q.keys():
            
            if h == "HU":
                #model.t_diff.add(self.thuin - self.tcout[c] >= self.EMAT)
                model.t_diff.add(self.thuout - model.tc[c,1] >= self.EMAT)
            
            elif c == "CU":
                
                #model.t_diff.add(self.tcuin - self.thout[h] >= self.EMAT)
                model.t_diff.add(model.th[h,hl[h]] - self.tcuout >= self.EMAT)
            
            else:       
                model.t_diff.add(model.th[h, self.zh[h,c]] - model.tc[c, self.zc[c,h]] >= self.EMAT)
                model.t_diff.add(model.th[h, self.zh[h,c] + 1] - model.tc[c, self.zc[c,h] + 1] >= self.EMAT)
        
        
        model.obj_max = pyo.Objective(expr = model.hu, sense = pyo.maximize)
        model.obj_min = pyo.Objective(expr = model.hu) #, sense = pyo.maximize)
        
        return model
             
    def bounder(self):
        
        model = self.bounder_model()
        ub =  self.bounder_solve(model, maxi = True)
        if ub is None:
            return False
        
        if ub == 0:
            return 0, 0
        
        return self.bounder_solve(model), ub
          
