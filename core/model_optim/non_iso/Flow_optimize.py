import pyomo.environ as pyo
from  collections import defaultdict
from typing import Dict
import sys, os
from pathlib import Path
# 采用等温混合的初值会导致传热为负数，致使计算错误

class Flow_optimaze:
    
    def __init__(self, zh, zc, temperature, q, hh, hc, fh, fc, aexp, acoeff, EMAT) -> None:
        
        self.zh, self.zc = zh, zc
        self.fh, self.fc = fh, fc
        self.hh, self.hc = hh, hc
        self.aexp = aexp
        self.acoeff = acoeff
        self.EMAT = EMAT
        
        self.model = pyo.ConcreteModel()
        
        # 初始化换热量参数
        self.model.q = pyo.Param(list(q.keys()), initialize = q, mutable=True)
        # 初始化温度参数
        self.model.temp_left = pyo.Param(list(temperature.keys()), initialize = {k:v[0] for k,v in temperature.items()}, mutable=True)
        self.model.temp_right = pyo.Param(list(temperature.keys()), initialize = {k:v[1] for k,v in temperature.items()}, mutable=True)
            
        # 变量初始化
        flow = list(self.model.q.keys()) + [(c,h) for h,c in self.model.q.keys()]
        self.model.flow = pyo.Var(flow, bounds = (1e-3, None))
        for h, c in self.model.q.keys():
            
            flow_h = self.fh[h]; flow_c = self.fc[c]
            
            self.model.flow[h,c].upper = flow_h
            self.model.flow[h,c].value = flow_h 
                        
            self.model.flow[c,h].upper = flow_c
            self.model.flow[c,h].value = flow_c 
        
        self.flow: Dict[str, list] = defaultdict(list)
        for st1, st2 in flow:
            self.flow[st1].append(st2)
            
        # 初始化值
        self.approach_temp = {key: self.approach_temperature(key) for key in self.model.q.keys()}   
        self.constrains()
        self.model.target = pyo.Objective(expr = self.target(self.hh, self.hc, self.aexp)) 
        #self.model.target.deactivate()
      
    def constrains(self):
        
        self.model.flow_balance = pyo.ConstraintList()
        self.model.approach_temp = pyo.ConstraintList()
        self.model.q_balance = pyo.ConstraintList()
        
        for st in self.flow.keys():
            
            if st[0] == "H":
                self.model.flow_balance.add(sum(self.model.flow[st, sst] for sst in self.flow[st]) == self.fh[st])
            else:
                self.model.flow_balance.add(sum(self.model.flow[st, sst] for sst in self.flow[st]) == self.fc[st])

        # 需要判断需不需要添加约束
        for hc in self.model.q.keys():

            self.model.approach_temp.add(self.approach_temp[hc][0] - self.EMAT >= 0)
            self.model.approach_temp.add(self.approach_temp[hc][1] - self.EMAT >= 0)
               
        return True
        
    def approach_temperature(self, key):
        
        h,c = key
        # 换热器左边热流股温度
        hot_left = self.model.temp_left[h]
      
        # 换热器右边热流股温度
        hot_right = (hot_left - self.model.q[h,c]/self.model.flow[h,c]) if len(self.flow[h]) != 1 else self.model.temp_right[h]
        
        # 冷流股温度，右边
        cool_right = self.model.temp_right[c]
        
        # 左边    
        cool_left = (cool_right + self.model.q[h,c]/self.model.flow[c,h]) if len(self.flow[c]) != 1 else self.model.temp_left[c]
        
        left, right = hot_left - cool_left, hot_right - cool_right
        delta_T = (2/3)*((left*right)**0.5) + left/6 + right/6  
        #delta_T = (left - right)/pyo.log(left/right)
        
        return left, right, delta_T
          
    def target(self, hh, hc, aexp):
        
        target = 0
        for (h,c), v in self.model.q.items():
            hcoeff = 1/hh[h] + 1/hc[c]
            target += (v * hcoeff / self.approach_temp[h,c][2])**aexp

        #print(target)
        return target
    
    # 以等温混合的分流量为初值进行优化，以等温混合的初值进行优化会碰到，初始流量太小造成的传热温差为负的情况
    def update(self, q: dict, temperature: dict, flow: dict):

        if q is not None:
            for key,val in q.items():
                self.model.q[key] = val  
                
            for key,val in temperature.items():
                self.model.temp_left[key] = val[0]
                self.model.temp_right[key] = val[1]
    
        if flow is not None: 
            for ma in flow.keys():
                self.model.flow[ma].value = flow[ma]

    def run(self, q = None, temperature = None, flow = None):
        
        #print('intial flow',flow)
        if q is not None or flow is not None:
            self.update(q, temperature, flow)
        
        #pyo.SolverFactory("gurobi", solver_io="python").solve(self.model, options = {'NonConvex' : 2})
        #a = time.time()
        path = Path(os.path.abspath(__file__)).parent.parent.parent.parent / "ipopt"
        if sys.platform == 'win32':
            path = path/ "ipopt.exe"
        else:
            path = path / "ipopt"
        try:
            results = pyo.SolverFactory('ipopt', executable=path).solve(self.model)
        except:
            results = pyo.SolverFactory("gams").solve(self.model, solver='baron', add_options=['option optcr=0.001', 'option reslim=1000'])#, tee = True) 
        #print(results)
        #print(flow)
        #print('solve_times: ',time.time() - a)
        TAC = self.model.target() * self.acoeff
        flow = {(st1,st2): self.model.flow[st1,st2]() for st1, sg in self.flow.items() for st2 in sg}
        
        #print({k: (pyo.value(v[0]), pyo.value(v[1]), pyo.value(v[2])) for k,v in self.approach_temp.items()})
        return TAC, flow


