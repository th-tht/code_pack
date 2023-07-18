from collections import deque
from typing import List, Dict
import math

from core.model_optim import Structure_Data
from .Flow_optimize_Golden_cut import Flow_optimize
from ..model import model
from .. import Numeric


class Heat_exchanger_network(model): 
    
    """
    type:
    
    gathered:   List[List(HEX)]
    stream_temp:  stream : temperature list
    flow:  (h,c): value, (c,h): value
    flow_opt:  gather_idx: Flow_optimaze 
    
    """
    
    
    def __init__(self, data):
            
        super(Heat_exchanger_network, self).__init__(data)
        
    def update_struct(self, zh: Dict, zc: Dict, zhu: Dict, zcu: Dict):
        
        super().update_struct(zh, zc, zhu, zcu)
        
        self.gathered = self._gathered()
        
        
        gather_length = len(self.gathered)
        self.stream_temp = dict() # stream stemperature
        self.flow = dict()         # 优化得到的流量
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
    
    # 将对应的换热匹配聚集为同一级, 注意没有和其他流股换热的  
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
    
    #对流量需要进行优化的进行优化
    def cal_TAC(self):
        
        self.stream_temp = self.stream_temperature()
        
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
                
                self.flow_opt[gathered_idx] = Flow_optimize(zh, zc, temperature, q, 
                                                            self.hh, self.hc, self.fh, self.fc, self.aexp, self.acoeff, self.EMAT)
                
                # 初始化
                t, flow = self.flow_opt[gathered_idx].run()  # 传入初始化流量
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
                
                if abs(t_left - t_right) < 1e-3:
                    lmtd = (t_left + t_right) / 2
                else:
                    lmtd = (t_left - t_right) / math.log(t_left / t_right)
            
                hcoeff = 1/self.hh[h] + 1/self.hc[c]
                TAC += ((self.q[h,c] * hcoeff / lmtd) ** self.aexp) * self.acoeff
                
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
                
                t,flow = self.flow_opt[gathered_idx].run(q, temperature) # 更新的参数
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