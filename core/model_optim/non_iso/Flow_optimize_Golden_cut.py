from collections import defaultdict, deque
from typing import Dict
import math
from .. import Golden_cut

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
        
        self.flow_initial = {(h,c): -2 for h,c in self.q.keys()}
        self.flow_initial.update({(c,h): -2 for h,c in self.q.keys()})
        
        for st, ls in list(self.match_set.items()):
            if len(ls) == 1:
                self.flow_initial[st, ls[0]] = self.ff[st]
                del self.match_set[st]

        start = min(self.match_set.keys(), key = lambda x: len(self.match_set[x]))
        dq = deque([(start, self.match_set[start][0])])
        
        self.flow_initial[dq[0]] = -1
        self.hex_order = []
        while dq:
            st1, st2 = dq.popleft()
            self.hex_order.append((st1, st2))
             # 添加接下来求解的搜索的变量
            for stc in self.match_set[st1]:
                if stc != st2 and self.flow_initial[st1, stc] == -2:
                    dq.append((st1, stc))
                    self.flow_initial[st1, stc] = -1
            if self.flow_initial[st2, st1] == -2:
                dq.append((st2, st1))
                self.flow_initial[st2, st1] = -1

        self.hex_idx = {k: idx for idx, k in enumerate(self.hex_order)}
        self.variable_num = sum(len(v) - 1 for v in self.match_set.values())
        
    def update(self, q: dict, temperature: dict):

        if q is not None:
            for key,val in q.items():
                self.q[key] = val  
                
            for key,val in temperature.items():
                self.temp_left[key] = val[0]
                self.temp_right[key] = val[1]
    
    def cal_temp(self, st: str, sst: str, flow_rate):
        
        if st.startswith('H'):
            h,c = st, sst
            tl = self.temp_left[st]
            tr = tl - self.q[h,c] / flow_rate
            
        else:
            c,h = st, sst
            tr = self.temp_right[st]
            tl = tr + self.q[h,c] / flow_rate
            
        return tl, tr
        
    def flow_bound(self, idx):    
        
        st1, st2 = self.hex_order[idx]
        
        for stc in self.match_set[st1]:
            if self.hex_idx[st1, stc] > idx:
                break
        else:
            lb = ub = self.ff[st1] - sum(self.flow[st1, stc] for stc in self.match_set[st1] if stc != st2)
            return lb, ub

        # 以分流为单位进行递归
        def cal_flow(st1: str, st2: int, status: int):

            if flow[st1, st2] is not None:
                return flow[st1, st2]
            
            elif status == 1: 
                
                return self.ff[st1] - sum(cal_flow(st1, stc, 0) for stc in self.match_set[st1] if stc != st2) 
            
            else:
                
                if flow[st2, st1] is None:
                    opposite_flow = cal_flow(st2, st1, 1)
                else:
                    opposite_flow= flow[st2, st1]

                if st1.startswith('H'):
                    h,c = st1, st2
                    tin = self.temp_left[h]
                    tcl, tcr = self.cal_temp(c, h, opposite_flow)
                    thl,thr = tcl + self.EMAT, tcr + self.EMAT
                    ff = self.q[h,c] / (tin - thr) + 1e-3           
                    
                else:
                    h,c = st2, st1
                    tin = self.temp_right[c]
                    thl, thr = self.cal_temp(h, c, opposite_flow)
                    tcl,tcr = thl - self.EMAT, thr - self.EMAT
                    ff = self.q[h,c] / (tcl - tin) + 1e-3
                    
                return ff
            
       
        flow = {(a,b): None for a,b in self.flow}
        for a,b in self.flow:
            if (a,b) not in self.hex_idx or self.hex_idx[a,b] < idx:
                flow[a,b] = self.flow[a,b]
        
        lb = cal_flow(st1, st2, 0)
        ub = cal_flow(st1, st2, 1)
        
        return lb, ub

    def pack_golden(self, idx):
        
        st, sst = self.hex_order[idx]
        
        def pack(flow_rate):
            
            self.flow[st, sst] = flow_rate
            return self.optimize(idx + 1)
        
        return pack
        
    def optimize(self, idx):
        
        st1, st2 = self.hex_order[idx]
        
        if idx == len(self.hex_order) - 1:
            self.flow[st1, st2] = self.ff[st1] - sum(self.flow[st1, stc] for stc in self.match_set[st1] if stc != st2)

            return self.cal_AC()
        
        lb, ub = self.flow_bound(idx)
        if self.variable_num <= 3:
            self.flow[st1, st2] = Golden_cut(lb, ub, self.pack_golden(idx))
        else: 
            self.flow[st1, st2] = (lb + ub) / 2
        
        return self.optimize(idx + 1)
    
    def cal_AC(self):
        
        ac = 0
        for (h,c), load in self.q.items():
            
            t_left = self.temp_left[h] - self.temp_right[c] - load / self.flow[c,h]
            t_right = self.temp_left[h] - load / self.flow[h,c] - self.temp_right[c]
            
            if abs(t_left - t_right) < 1e-3:
                lmtd = (t_left + t_right) / 2
            else:
                lmtd = (t_left - t_right) / math.log(t_left / t_right)
            u = 1 / self.hh[h] + 1 / self.hh[c]
            
            ac += (u * load / lmtd) ** self.aexp

        return ac * self.acoeff
        
    def run(self, q = None, temperature = None):
        
        self.flow = self.flow_initial.copy()
        
        if q is not None:
            self.update(q, temperature)
        
        AC = self.optimize(0)
        
        #print({k: (pyo.value(v[0]), pyo.value(v[1]), pyo.value(v[2])) for k,v in self.approach_temp.items()})
        return AC, self.flow


