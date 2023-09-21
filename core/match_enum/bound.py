from itertools import product, chain
from math import inf
from typing import Dict
from .import mytyping, Unpack_data

class Bound(Unpack_data):
    
    def __init__(self, data) -> None:
        
        super().__init__(data)
        
        self.alpha = 0.9
        self.idx_i = list(self.thin.keys())
        self.idx_j = list(self.tcin.keys())
        self.length = len(self.idx_i) + len(self.idx_j) + 1

        self.scores = self.scored()      # 计算个匹配的初始分数, 以及是最后需要枚举的节点
        self.match_idx = {}         
        self.idx_match = []     
        
        """initial match idx"""
        
        self.UB_TAC = mytyping.inf
        self.stream_idx = {s : i for i,s in enumerate(chain(self.idx_i, self.idx_j, ['HU','CU']))}
        self.area_cost = self.Area_supertarget(self.HRAT_MAX)
              
    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)
       
    def scored(self) -> Dict[mytyping.match, float]:
        
        def cal(h: str, c: str) -> int:
            if h != 'HU' and c != 'CU':
                if self.tcin[c] + self.EMAT >= self.thin[h]:
                    return inf
                if self.thout[h] >= self.tcout[c]:
                    return round((self.tcout[c] - self.thout[h]), 3) # * (self.alpha + (ch if (ch := self.fh[h] / self.fc[c]) < 1 else 1/ch)),3)
                else:
                    return round((min(self.tcout[c],self.thin[h]) - max(self.tcin[c],self.thout[h])),3) # * (self.alpha + (ch if (ch := self.fh[h] / self.fc[c]) < 1 else 1/ch)),3)
            elif h == 'HU':
                if self.tcin[c] + self.EMAT >= self.thuin:
                    return inf               
                return (self.tcout[c] - self.thuout) # * (1 + self.alpha)
            else:
                if self.tcuin + self.EMAT >= self.thin[h]:
                    return inf
                return (self.tcuout - self.thout[h]) # * (1 + self.alpha)
                
        matches = {(a,b): None for a,b in product(chain(self.idx_i,['HU']), chain(self.idx_j,['CU']))}
        del matches['HU','CU']
        
        for h,c in matches:
            matches[h,c] = cal(h,c)
        
        return matches
       
    def score_adjust(self, match: int):
        #return
        for key,val in self.scores.items():
            if (1 << self.match_idx[key]) & match == 0: 
                
                if val > 0:
                    self.scores[key] = val / self.alpha
                elif val < 0:
                    if val > self.EMAT:
                        self.scores[key] = -val
                    else:
                        self.scores[key] = -val * self.alpha
                else:
                    self.scores[key] = self.EMAT  
              
    def valid(self, nodes: int, max_num: int):
        
        # 根据剩余的点数，查看还要多少节点能够满足每条流股至少有一个换热, 
        need = 0
        for idx,k in enumerate(chain(self.idx_i, self.idx_j)):
            if nodes & (1 << idx) == 0:
                need |= 1 << self.stream_idx[k]
        
        op, cache = 0, 0
        for h,c in self.scores:
            if (1 << self.stream_idx[h]) & need and (1 << self.stream_idx[c]) & need:    
                need &= ~(1 << self.stream_idx[h]) & ~(1 << self.stream_idx[c])
                op += 1
                if cache & (1 << self.stream_idx[h]):
                    op -= 1
                if cache & (1 << self.stream_idx[c]):
                    op -= 1
                cache &= ~(1 << self.stream_idx[h]) & ~(1 << self.stream_idx[c])
                
            elif (1 << self.stream_idx[h]) & need and cache & (1 << self.stream_idx[h]) == 0:
                op += 1
                cache |= (1 << self.stream_idx[h])
                
            elif (1 << self.stream_idx[c]) & need and cache & (1 << self.stream_idx[c]) == 0:
                op += 1
                cache |= (1 << self.stream_idx[c])
    
        return need == cache and op <= max_num

    def select_match(self) -> mytyping.match:
        
        match = max(self.scores, key = self.scores.get) 
        del self.scores[match]
        
        return match      # 选出最不可行的节点进行枚举 
                
    def update_ub(self, ub):
        # undate the upper bound of TAC 
        #print("New UB: ",ub)
        self.UB_TAC = ub
           
    def is_larger(self, pn: mytyping.Proto_network, hu_min: float) -> bool:
        
        """下界计算"""
        
        cumin = hu_min + self.heat_overflow
        op_cost = hu_min * self.hucost + cumin * self.cucost
        
        tac = op_cost + len(pn) * self.unitc + self.area_cost 
        
        #print("NLB: ", tac, tac >= self.UB_TAC)
        #print(f"hu = {hu_min}, LB = {tac}, ub = {self.UB_TAC}")
        #print(pn, op_cost, len(pn) * self.unitc, tac, self.UB_TAC)
        #print(tac >= self.UB_TAC)
        return tac >= self.UB_TAC
         
    def _utility_cal(self, HRAT):
        # calculate the usage of hot utilities according HRAT_MAX
        tpinch = [self.thin[i] for i in self.idx_i] + [self.tcin[j] + HRAT for j in self.idx_j]
        qsoa = qsia = zph = 0.0
        for x in range(len(tpinch)):
            qsoa = qsia = 0
            for i in self.idx_i:
                qsoa += self.fh[i] * (max(0, self.thin[i] - tpinch[x]) - max(0, self.thout[i] - tpinch[x]))
            for j in self.idx_j:
                qsia += self.fc[j] * (max(0, self.tcout[j] + HRAT - tpinch[x]) - max(0, self.tcin[j] + HRAT -tpinch[x]))
            zph = max(qsia - qsoa, zph)
        qh = zph
        q_surplus = sum(self.fh[i] * (self.thin[i] - self.thout[i]) for i in self.idx_i) \
            - sum(self.fc[j] * (self.tcout[j] - self.tcin[j]) for j in self.idx_j)
        qc = qh + q_surplus

        return qh, qc
    
    def _compose_curve(self, qh, qc):
        
        # obtain the compose curve by fix utilities    
        hot_itv = set([self.thin[i] for i in self.idx_i] + [self.thout[i] for i in self.idx_i])
        cold_itv = set([self.tcin[j] for j in self.idx_j] + [self.tcout[j] for j in self.idx_j]) 
        ## add the utilities
        thuin_d, thuout_d = self.thuin, self.thuout
        if thuin_d == thuout_d:
            thuout_d -= 1e-5
        hot_itv.update([thuin_d, thuout_d])
        
        tcuin_d, tcuout_d = self.tcuin, self.tcuout
        if tcuin_d == tcuout_d:
            tcuin_d -= 1e-5
        cold_itv.update([tcuin_d, tcuout_d])
        
        hot_itv = sorted(hot_itv)
        cold_itv = sorted(cold_itv)
        
        hot_capacity_flow = [0] * (len(hot_itv) - 1)
        cold_capacity_flow = [0] * (len(cold_itv) - 1)
        
        UH = [0] * (len(hot_itv) - 1)
        UC = [0] * (len(cold_itv) -1)
        
        ## the slope of compose curve
        for h in self.idx_i:
            for itv in range(len(hot_itv) - 1):
                if self.thin[h] >= hot_itv[itv + 1] and self.thout[h] <= hot_itv[itv]:
                    hot_capacity_flow[itv] += self.fh[h]
                    UH[itv] = max(UH[itv], self.hh[h])
                    
        ### hot utilities
        for itv in range(len(hot_itv) - 1):
            if thuin_d >= hot_itv[itv + 1] and thuout_d <= hot_itv[itv]:
                hot_capacity_flow[itv] += qh / abs(thuin_d - thuout_d)
                UH[itv] = max(UH[itv], self.hhu)
    
        for c in self.idx_j:
            for itv in range(len(cold_itv) - 1):
                if self.tcout[c] >= cold_itv[itv + 1] and self.tcin[c] <= cold_itv[itv]:
                    cold_capacity_flow[itv] += self.fc[c]
                    UC[itv] = max(UC[itv], self.hc[c])

        ### cold utilities
        for itv in range(len(cold_itv) - 1):
            if tcuout_d >= cold_itv[itv + 1] and tcuin_d <= cold_itv[itv]:
                cold_capacity_flow[itv] += qc / abs(tcuout_d - tcuin_d)
                UC[itv] = max(UC[itv], self.hcu)
        
        return hot_itv, cold_itv, hot_capacity_flow, cold_capacity_flow, UH, UC

    def Area_supertarget(self, HRAT_MAX):
        
        self.heat_overflow = sum((self.thin[h] - self.thout[h])*self.fh[h] for h in self.idx_i) \
            - sum((self.tcout[c] - self.tcin[c])*self.fc[c] for c in self.idx_j)
        
        # calculate the usage of hot utilities according HRAT_MAX
        qhmax, qcmax = self._utility_cal(HRAT_MAX)
        
        hot_itv, cold_itv, hot_capacity_flow, cold_capacity_flow, UH, UC = self._compose_curve(qhmax, qcmax)

        # calculate the area using area target
        Area = 0
        itv_h, itv_c = len(hot_itv) - 2, len(cold_itv) - 2  # interval 
        tempe_h, tempe_c = hot_itv[-1], cold_itv[-1]        # temperature at now
        
        while itv_h >= 0 and itv_c >= 0:
            
            thr, tcr = tempe_h, tempe_c
            thl, tcl = hot_itv[itv_h], cold_itv[itv_c]
            
            h_load = (thr - thl) * hot_capacity_flow[itv_h]
            c_load = (tcr - tcl) * cold_capacity_flow[itv_c]
            
            U = 1 / UH[itv_h]  + 1 / UC[itv_c]
            
            load = min(h_load, c_load)
            if h_load - c_load >= 1e-5:
                thl = thr - c_load / hot_capacity_flow[itv_h]
                itv_c -= 1
                        
            elif h_load - c_load <= -1e-5:
                tcl = tcr - h_load / cold_capacity_flow[itv_c]
                itv_h -= 1
                   
            else:
                itv_h -= 1
                itv_c -= 1
                
            tempe_h, tempe_c = thl, tcl
            
            if UH[itv_h] == 0:            # no heat interval
                itv_h -= 1       
                tempe_h = hot_itv[itv_h + 1]
            if UC[itv_c] == 0: 
                itv_c -= 1
                tempe_c = cold_itv[itv_c + 1]
            
            dt1, dt2 = thr - tcr, thl - tcl
            
            if abs(dt1 - dt1) < 1e-3:
                delta_T = (dt1 + dt2) / 2
            else:
                delta_T = ((thr - tcr) - (thl - tcl)) / (1e-3 + mytyping.log((thr - tcr) / (thl - tcl)))
        
            Area += load * U / delta_T
    
        assert itv_h <= 0 and itv_c <= 0
        assert abs(tempe_h - hot_itv[0]) <= 1e-3 and abs(tempe_c - cold_itv[0]) <= 1e-3
        
        return self.acoeff * (Area ** self.aexp)
    
    def Area_cost(self, loads: mytyping.Loads) -> float:
        
        area_cost = 0
        
        for (h,c), q in loads.items():
            
            if h == "HU":
                U = 1/self.hhu + 1/self.hc[c]
                hr, hl = self.thuin, self.thuin
                cr, cl = self.tcout[c], self.tcout[c] - q / self.fc[c]            
            elif c == "CU":
                U = 1/self.hcu + 1/self.hh[h]
                hr, hl = self.thout[h] + q / self.fh[h], self.thout[h]
                cr,cl = self.tcuin, self.tcuin
            else:
                U = 1/self.hh[h] + 1/self.hc[c]
                hr, hl = self.thin[h], self.thin[h] - q / self.fh[h]
                cr, cl = self.tcin[c] + q / self.fc[c], self.tcin[c]
            
            l, r = hl - cl, hr - cr     
            if l <= self.EMAT - 1e-5 or r <= self.EMAT - 1e-5:     # 理论上来说应该不会有问题的, 可能是
                return True
            
            if abs(r - l) <= 1e-5:
                lmtd = (l + r)/2
            else:
                lmtd = abs(r - l) / abs(1e-5 + mytyping.log(r/l))
            
            #print("sum:", self.acoeff * (q * U / lmtd)**self.aexp)
            area_cost += self.acoeff * (q * U / lmtd)**self.aexp       
        
        #print("area_cost: " ,area_cost)
        return area_cost

