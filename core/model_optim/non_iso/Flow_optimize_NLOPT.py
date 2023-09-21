import numpy as np
from typing import Dict
import math
import nlopt 

# 采用等温混合的初值会导致传热为负数，致使计算错误

class Flow_optimize:
    
    """
    type:
    zh, zc:  (h,c): k, (c,h): k
    q: (h,c): value
    temp_left: h: value, c:value
    temp_right: h: value, c:value
    """        
    def __init__(self, zh, zc, temperature, q, hh, hc, fh, fc, aexp, acoeff, EMAT) -> None:
        
        self.zz: dict = zh; self.zz.update(zc)
        self.ff: dict = fh; self.ff.update(fc)
        self.hh: dict = hh; self.hh.update(hc)
        
        self.aexp = aexp
        self.acoeff = acoeff
        self.EMAT = EMAT
        
        self.q, self.temp_left, self.temp_right = dict(), dict(), dict()
        self.update(q, temperature)    
         
        self.match_set: Dict[str, list] = dict()
        for h,c in self.q:
            if h not in self.match_set:
                self.match_set[h] = []
            if c not in self.match_set:
                self.match_set[c] = []
                
            self.match_set[h].append(c)
            self.match_set[c].append(h)
        
        self.flow = {(h,c): -1 for h,c in self.q.keys()}
        self.flow.update({(c,h): -1 for h,c in self.q.keys()})
        self.flow_low_bound = self.flow.copy()
        
        for st, ls in list(self.match_set.items()):
            if len(ls) == 1:
                self.flow[st, ls[0]] = self.ff[st]
                del self.match_set[st]
        
        self.x = [] #[match for match, v in self.flow.items() if v == -1]
        for st, g in self.match_set.items():
            for sst in g[:-1]:
                self.x.append((st, sst))
        
        self.idx_x = {match: idx for idx, match in enumerate(self.x)}
        
        self.match_st = list(self.match_set.keys())
        self.idx_match_st  = {st: idx for idx, st in enumerate(self.match_st, len(self.x))}
    
    @staticmethod
    def swap(st, sst):
        if st[0] == "H":
            return st, sst
        else:
            return sst, st
    
    def initial(self):    
        
        # 以分流为单位进行递归
        def cal_flow(st1: str, st2: int, status: int):
            
            if status == 1: 
                return self.ff[st1] - sum(cal_flow(st1, stc, 0) for stc in self.match_set[st1] if stc != st2) 
            
            else:
                if st1.startswith('H'):
                    h,c = st1, st2
                    tin = self.temp_left[h]
                    thr = self.temp_right[c] + self.EMAT
                    ff = self.q[h,c] / (tin - thr)         
                    
                else:
                    h,c = st2, st1
                    tin = self.temp_right[c]
                    tcl = self.temp_left[h] - self.EMAT
                    ff = self.q[h,c] / (tcl - tin) 
                    
                return ff
            
        flow = self.x
        
        x_initial = [0] * len(self.x)
        lb = [0] * len(self.x)
        ub = [0] * len(self.x)
        
        flow_b = {(st1, st2): (cal_flow(st1, st2, 0), cal_flow(st1, st2, 1)) for st1, g in self.match_set.items() for st2 in g}

        for i, (st1, st2) in enumerate(flow):
            
            lb[i], ub[i] = flow_b[st1, st2]
            #lb[i] = cal_flow(st1, st2, 0)
            #ub[i
            # ] = cal_flow(st1, st2, 1)
        stream_load = {st: sum(self.q[self.swap(st, sst)] for sst in g) for st, g in self.match_set.items()}
        for i, (st,sst) in enumerate(self.x):
            
            x_initial[i] = self.q[self.swap(st, sst)] / stream_load[st]  * self.ff[st]
            if abs(x_initial[i] - lb[i]) < 1e-2:
                x_initial[i] = lb[i]
            if abs(x_initial[i] - ub[i]) < 1e-2:
                x_initial[i] = ub[i]
        
        """print(self.x)
        print(lb)
        print(x_initial)
        print(ub)"""
        
        for idx, (i,j) in enumerate(zip(lb, ub)):
            if abs(i - j) < 1e-2 or self.q[self.swap(*self.x[idx])] / stream_load[self.x[idx][0]] <= 1e-2:
                
                lb[idx] = ub[idx] = x_initial[idx]

        return x_initial, lb, ub
    
    def optimize(self, x_initial, lb, ub):
        
        #x_initial += [0] * len(self.match_set)
        #lb += [0] * len(self.match_set)
        #ub += [None] * len(self.match_set)
        opt = nlopt.opt(nlopt.GN_DIRECT, len(x_initial))

        opt.set_min_objective(self.cal_AC)
        
        #opt.set_xtol_rel(1e-3)
        opt.set_ftol_rel(1e-8)
        opt.set_maxtime(1)
        
        opt.set_lower_bounds(lb)
        opt.set_upper_bounds(ub)
        x_opt = opt.optimize(x_initial)
        
        ac = opt.last_optimum_value()

        flow = self.flow
        for i, value in enumerate(x_opt):
            flow[self.x[i]] = value
        
        for st, g in self.match_set.items():
            flow[st, g[-1]] = self.ff[st] - sum(flow[st,sst] for sst in g[:-1])
  
        return flow, ac
         
    def cal_AC(self, x, grad):
         
        for i in range(len(self.x)):
            self.flow[self.x[i]] = x[i]
        
        for st, g in self.match_set.items():
            self.flow[st, g[-1]] = self.ff[st] - sum(self.flow[st,sst] for sst in g[:-1])

            if self.flow[st, g[-1]] <= 0:
                return 1e9
        
        ac = 0
        for (h,c), load in self.q.items():
            
            t_left = self.temp_left[h] - self.temp_right[c] - load / self.flow[c,h]
            t_right = self.temp_left[h] - load / self.flow[h,c] - self.temp_right[c]
            
            
            #print(t_left, t_right)
            if t_left < self.EMAT - 1e-3  or t_right < self.EMAT - 1e-3:
                #print(t_left, t_right)
                return 1e9
            
            if abs(t_left - t_right) < 1e-3:
                lmtd = (t_left + t_right) / 2
            else:
                lmtd = (t_left - t_right) / math.log(t_left / t_right)
            u = 1 / self.hh[h] + 1 / self.hh[c]
            
            ac += (u * load / lmtd) ** self.aexp
            
        #print(self.flow, ac * self.acoeff)
        #if self.num >= 10000:
        #    exit()
        #self.num += 1
        #lag = 0
        #for st,g in self.match_set.items():
        #    lag +=  abs(sum(x[self.idx_x[st, st1]] for st1 in g) - self.ff[st]) * 1e4
        
        #print(x, ac * self.acoeff)
        return ac * self.acoeff #+ lag
                    
    def update(self, q: dict, temperature: dict):

        if q is not None:
            for key,val in q.items():
                self.q[key] = val  
                
            for key,val in temperature.items():
                self.temp_left[key] = val[0]
                self.temp_right[key] = val[1]

    def run(self, q = None, temperature = None):
        
        if q is not None:
            self.update(q, temperature)
        self.num  = 0
        flow, AC = self.optimize(*self.initial())
        #print({k: (pyo.value(v[0]), pyo.value(v[1]), pyo.value(v[2])) for k,v in self.approach_temp.items()})
        return AC, flow


