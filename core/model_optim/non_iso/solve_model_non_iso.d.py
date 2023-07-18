from collections import deque
from typing import List, Dict
import math, copy

from core.model_optim import Structure_Data
from .Flow_optimize import Flow_optimize
from ..model import model
from .. import Numeric


class Heat_exchanger_network(model): 
    
    def __init__(self, data):
            
        super(Heat_exchanger_network, self).__init__(data)
        
    def update_struct(self, zh: Dict, zc: Dict, zhu: Dict, zcu: Dict):
        
        super().update_struct(zh, zc, zhu, zcu)
        
        self.gathered = self._gathered()
        
        self.flow_idx = dict()
        self.flow_initial = dict()
        
        gather_length = len(self.gathered)
        for idx, gather in enumerate(self.gathered):
            d = {(h,c): 0 for h,c in gather}
            d.update({(c,h): 0 for h,c in gather})
            self.flow_initial[idx] = d

        self.stream_temp = dict() # stream stemperature
        self.flow = dict()         # 优化得到的流量
        self.approach_temperature = dict()
        self.model_sets = [None]*(gather_length)
        self.flow_opt = [None]*(gather_length)
        
    @staticmethod
    def update_bound(Iterator, bound):
        
        for val in Iterator:
            if type(val) == Numeric:
                value, st = val.solve()
                if st == "r":
                    bound[1] = min(value, bound[1])
                else:
                    bound[0] = max(value, bound[0])
            else:
                if val + 1e-5 < 0:
                    return False
            
            if bound[0] - bound[1] > 1e-5:
                return False
        
        return bound
    
    #TODO
    def bounder(self):
        # TODO
        # 根据loadfunc 计算热公用工程用量边界
        if "HU" not in self.matches:
            bound = [0,0]
        else:
            u = sum(self.loadfunc["HU",c] for c in self.matches["HU"])
            if type(u) != Numeric:
                bound = [u,u]
            else:
                bound = [0, sum(self.fc[c] * (self.tcout[c] - self.tcin[c]) for c in self.matches["HU"])]
        
        bound = self.update_bound([v - 0.1 for v in self.loadfunc.values()], bound)
        
        if not bound:
            return False
        
        # 根据传热温差计算热公用工程用量边界
        stream_temp = self.stream_temperature(q = self.loadfunc)
        approach = []
        
        for h,c in self.loadfunc.keys():
            
            if h == "HU":
                left = self.thuin - stream_temp[c][0]
                right = self.thuout - stream_temp[c][1]
            elif c == "CU":
                left = stream_temp[h][-2] - self.tcuout
                right = stream_temp[h][-1] - self.tcuin
            else:
                left = stream_temp[h][self.zh[h,c]] - stream_temp[c][self.zc[c,h]]
                right = stream_temp[h][self.zh[h,c]+1] - stream_temp[c][self.zc[c,h]+1]

            approach.append(left - self.EMAT)
            approach.append(right - self.EMAT)
        
        bound = self.update_bound(approach, bound)
        
        return bound

        # !将对应的换热匹配聚集为同一级, 注意没有和其他流股换热的  
    
    def _gathered(self):    
        # 将分流相互影响的换热器聚集
        
        def dfs(h : str, l: list):
            
            if (h, l[0]) in visited:
                return
            
            for c in l:
                ky.add((h,c))
                visited.add((h,c))
            
            for c in l:
                if len(self.gather_split[c][self.zc[c,h] - 1]) > 1:
                    for hh in self.gather_split[c][self.zc[c,h] - 1]:
                        dfs(hh, self.gather_split[hh][self.zh[hh,c] - 1])
                            
        gathered = []; visited = set()
        for s1 in self.thin.keys():
            for s2 in self.gather_split[s1]:
                ky = set()
                dfs(s1, s2)
                if ky: gathered.append(list(ky))

        return gathered
    
    def feasiblel_judge(self, gathered_idx):
        
        def cal_temp(st: str, sst: str):
            
            if st.startswith('H'):
                h,c = st, sst
                tl = self.stream_temp[st][self.zh[h,c]]
                tr = tl - self.q[h,c] / flow[h,c]
                
            else:
                c,h = st, sst
                tr = self.stream_temp[st][self.zc[c,h] + 1]
                tl = tr + self.q[h,c] / flow[c,h]
                
            return tl, tr
                
        # 以分流为单位进行递归
        def cal_minnum_flow(st1: str, st2: int, status: int):
            '''
            计算部分可直接获得的流股流量, 主要test2的另外两条分流类似
            对于只有无分流的情况无需考虑传热温差，因为有分流的会考虑，也不会有只有一个换热器的情况,
            热量传递路径只有一条, 对于此分流而言, 入口温度以及里面的换热器与HU无关则此分流与HU无关。
            此时只需保证无关分流流量最小，此时计算得到的边界则是最后边界,
            status 代表求大还是求小
            '''
            if flow[st1, st2] is not None:
                return True
            
            if len(self.gather_split[st1][stage[st1] - 1]) <= 1:
                flow[st1, st2] = residual[st1]
            
            elif status == 1: 
                for sst2 in self.gather_split[st1][stage[st1] - 1]:
                    if sst2 != st2:
                        if not cal_minnum_flow(st1, sst2, 0):
                            return False       
                flow[st1, st2] = residual[st1]
                return True
            
            else:
                
                if flow[st2, st1] is None:
                    cal_minnum_flow(st2, st1, 1)

                if st1.startswith('H'):
                    h,c = st1, st2
                    tin = self.stream_temp[h][stage[h]]
                    tcl,tcr = cal_temp(c, h)
                    thl,thr = tcl + self.EMAT, tcr + self.EMAT
                    ff = self.q[h,c] / (tin - thr) + 1e-3           
                    
                else:
                    h,c = st2, st1
                    tin = self.stream_temp[c][stage[c]+1]
                    thl, thr = cal_temp(h, c)
                    tcl,tcr = thl - self.EMAT, thr - self.EMAT
                    ff = self.q[h,c] / (tcl - tin) + 1e-3
                    
                residual[st1] -= ff
                flow[st1, st2] = ff
            
            return True
        
            
        flow = {(a,b): None for a,b in self.flow_initial[gathered_idx]}
        stage, residual = dict(), dict()
        
        for h,c in self.gathered[gathered_idx]:
            residual[h] = self.fh[h]
            residual[c] = self.fc[c]
            stage[h] = self.zh[h,c]
            stage[c] = self.zc[c,h]
            
        for a,b in flow.keys():
            cal_minnum_flow(a, b, 1)
            
        self.flow_initial[gathered_idx] = flow
        
        return True
 
    #对流量需要进行优化的进行优化
    def cal_TAC(self):
        
        self.stream_temp = self.stream_temperature()
        # 对每个部分求得初值
        for gathered_idx in range(len(self.gathered)):
            if not self.feasiblel_judge(gathered_idx):    # 采用贪心算法生成初始值以及判断是否可行
                return None
        TAC = 0
        # 不同部分的流量
        for gathered_idx in range(len(self.gathered)):
            
            # 判断是否需要建立优化实例
            if len(self.gathered[gathered_idx]) > 1 and self.flow_opt[gathered_idx] is None:
                zh,zc = dict(),dict()
                temperature = dict()
                q = dict()
                stage = dict()           # 不存在能量回路，每条流股最多一级参与优化
                for h,c in self.gathered[gathered_idx]:
                    
                    zh[h,c] = self.zh[h,c]
                    zc[c,h] = self.zc[c,h]  
                    q[h,c] = self.q[h,c]
                    
                    stage[h] = self.zh[h,c]
                    stage[c] = self.zc[c,h]
                    
                    temperature[h] = [self.stream_temp[h][stage[h]], self.stream_temp[h][stage[h] + 1]]
                    temperature[c] = [self.stream_temp[c][stage[c]], self.stream_temp[c][stage[c] + 1]]
                
                self.flow_opt[gathered_idx] = Flow_optimize(zh, zc, temperature, q, self.hh, self.hc, self.fh, self.fc, self.aexp, self.acoeff, self.EMAT)
                
                # 初始化
                t, flow = self.flow_opt[gathered_idx].run(flow = self.flow_initial[gathered_idx])  # 传入初始化流量
                TAC += t
                # 保存流量优化后数据
                self.flow.update(flow)
                  
            elif len(self.gathered[gathered_idx]) == 1:
                
                h,c = self.gathered[gathered_idx][0]
                self.flow[h,c] = self.fh[h]
                self.flow[c,h] = self.fc[c]
                # 传热温差,计算TAC
                
                t_left = self.stream_temp[h][self.zh[h,c]] - self.stream_temp[c][self.zc[c,h]]
                t_right = self.stream_temp[h][self.zh[h,c] + 1] - self.stream_temp[c][self.zc[c,h] + 1]
                delta_T = (2/3)*((t_left * t_right)**0.5) + t_left/6 + t_right/6
                hcoeff = 1/self.hh[h] + 1/self.hc[c]
                TAC += ((self.q[h,c] * hcoeff / delta_T) ** self.aexp) * self.acoeff
                
            else:
                temperature = dict()
                q = dict()
                stage = {}
                for h,c in self.gathered[gathered_idx]:
                    q[h,c] = self.q[h,c]
                    stage[h] = self.zh[h,c]
                    stage[c] = self.zc[c,h]
                    
                    temperature[h] = [self.stream_temp[h][self.zh[h,c]], self.stream_temp[h][self.zh[h,c] + 1]]
                    temperature[c] = [self.stream_temp[c][self.zc[c,h]], self.stream_temp[c][self.zc[c,h] + 1]]
                
                t,flow = self.flow_opt[gathered_idx].run(q, temperature, self.flow_initial[gathered_idx]) # 更新的参数
                TAC += t
                self.flow.update(flow)
        
        # TODO 公用工程
        for h,c in self.q.keys():
            if h == 'HU':
                t_left = self.thuin - self.stream_temp[c][0]
                t_right = self.thuout - self.stream_temp[c][1]
                hcoeff = 1/self.hc[c] + 1/self.hhu

                delta_T = (2/3)*((t_left * t_right)**0.5) + t_left/6 + t_right/6
                
                TAC += ((self.q[h,c] * hcoeff / delta_T) ** self.aexp) * self.acoeff + self.q[h,c] * self.hucost
            elif c == 'CU':
                t_left = self.stream_temp[h][-2] - self.tcuout
                t_right = self.stream_temp[h][-1] - self.tcuin
                hcoeff = 1/self.hh[h] + 1/self.hcu
                
                delta_T = (2/3)*((t_left * t_right)**0.5) + t_left/6 + t_right/6
                TAC += ((self.q[h,c] * hcoeff / delta_T) ** self.aexp) * self.acoeff + self.q[h,c] * self.cucost
        return TAC
    
    # 重新计算计算TAC，以及数据打包
    def Data_pack(self) -> Structure_Data:
        
        hot_temp,cool_temp = dict(),dict()
        area,q = dict(),dict()
        fh,fc = dict(),dict()
        TAC = len(self.q) * self.unitc       # 固定费用
        
        zh, zc, zhu, zcu = {}, {}, {}, {}
        HU, Area  = 0, 0
        
        for h,c in self.zh.keys():
            fh[h,c] = self.flow[h,c]
        
        for c,h in self.zc.keys():
            fc[c,h] = self.flow[c,h]
            
        # 数据重新计算
        q = self.q
        for h,c in self.q:
            
            if h == 'HU':
                U = 1/self.hhu + 1/self.hc[c]
                TAC += self.q[h,c] * self.hucost         # 公用工程费用
                
                hot_temp[h,c]  = [self.thuin, self.thuout]
                cool_temp[c,h] = [self.stream_temp[c][0], self.stream_temp[c][1]]
                
                HU += self.q[h,c]
                zhu['HU', c] = 1 
                
            elif c == 'CU':
                U = 1/self.hh[h] + 1/self.hcu
                TAC += self.q[h,c] * self.cucost
                
                hot_temp[h,c] = [self.stream_temp[h][-2], self.stream_temp[h][-1]]
                cool_temp[c,h] = [self.tcuout,self.tcuin]
                
                zcu[h,'CU'] = 1
                
            else:
                U = 1/self.hh[h] + 1/self.hc[c]
                zh[h,c] = self.zh[h,c]
                zc[c,h] = self.zc[c,h] 

                hl = self.stream_temp[h][zh[h,c]]
                hr = hl - self.q[h,c] / self.flow[h,c]
                
                cr = self.stream_temp[c][zc[c,h] + 1]
                cl = cr + self.q[h,c]/self.flow[c,h]
                
                hot_temp[h,c]  =  [hl, hr]
                cool_temp[c,h] =  [cl, cr]
                
            left,right = hot_temp[h,c][0] - cool_temp[c,h][0], hot_temp[h,c][1] - cool_temp[c,h][1]
            
            delta_T = (left + right)/2 if abs(left - right) < 1e-5 else abs(left - right)/abs(1e-5 + math.log(left/right))
            area[h,c] = U * q[h,c] / delta_T
            
            Area += area[h,c]
            TAC += self.acoeff * (area[h,c]**self.aexp)   # 面积费用

        # 数据压缩打包
        q = {key : "%.2f"%val for key,val in q.items()}
        area = {key : "%.2f"%val for key,val in area.items()}
        fh = {key : "%.2f"%val for key,val in fh.items()}
        fc = {key : "%.2f"%val for key,val in fc.items()}
        hot_temp = {key: ("%.2f"%val[0], "%.2f"%val[1]) for key,val in hot_temp.items()}
        cool_temp = {key : ("%.2f"%val[0], "%.2f"%val[1]) for key,val in cool_temp.items()}
        

        return Structure_Data(zh, zc, zcu, zhu, '%.2f'%HU, '%.2f'%TAC, '%.2f'%Area, hot_temp, cool_temp, q, area, fh, fc)  