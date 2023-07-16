
from cmath import log
from collections import defaultdict
from itertools import chain
from typing import Any, Dict,List
from .. import Structure_Data, mytyping, Unpack_data



class model(Unpack_data): 
    
    def __init__(self, data):
        
        super(model, self).__init__(data)
        
        self.golden_cut = (5**0.5 +1)/2
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.run(*args, **kwds)
        
    def update_struct(self, zh: Dict, zc: Dict, zhu: Dict, zcu: Dict):
        
        """
        更新结构，和初始化方程
        """
        
        self.zh, self.zc, self.zhu, self.zcu = zh, zc, zhu, zcu

        self.q_idx = {key : i for i,key in enumerate(chain(self.zh.keys(),self.zhu.keys(),self.zcu.keys()))}
        self.q = {key : None for key in self.q_idx}
              
        self.heat_match = defaultdict(list)
        for a,b in self.q_idx.keys():
            self.heat_match[a].append(b)
            self.heat_match[b].append(a)
        
        self.gather_split = self.gather() # 两层列表嵌套在字典里[stream][k][r]
        self.stream_temp = dict()
        
        self.heat_load_solve()               # 初始化方程组
        
    def gather(self) -> dict:    
        
        arr : Dict[str, List[list]] = dict()
        
        for h in self.thin.keys():
            arr[h] = []
        for c in self.tcin.keys():
            arr[c] = []
            
        for h, c in self.zh.keys():
            
            if self.zh[h,c] > len(arr[h]):
                arr[h] += [[] for _ in range(self.zh[h,c] - len(arr[h]))]
            if self.zc[c,h] > len(arr[c]):
                arr[c] += [[] for _ in range(self.zc[c,h] - len(arr[c]))]
            
            arr[h][self.zh[h,c]-1].append(c)
            arr[c][self.zc[c,h]-1].append(h)
            
        return arr
    
    # 计算流股在各级的温度 
    def stream_temperature(self, q = None) -> mytyping.Stream_temperature:
        
        if q is None:
            q = self.q
        
        stream_temperature: Dict[str,List] = dict()
        
        for h in self.thin.keys():
            stream_temperature[h] = [self.thin[h], self.thin[h]]   # 入口与冷流股统一
            for g in self.gather_split[h]:
                stream_temperature[h].append(stream_temperature[h][-1] - sum(q[h,c] for c in g)/self.fh[h])   # 每一级出
                
            if (h,'CU') in q:
                stream_temperature[h].append(stream_temperature[h][-1] - q[h,'CU']/self.fh[h])       # 冷却器
            # self.temp_stage[h].append(self.thout[h])           
            
        for c in self.tcout.keys():
            stream_temperature[c] = [self.tcout[c]]                                                
            if ('HU',c) in q:
                stream_temperature[c].append(stream_temperature[c][-1] - q['HU',c]/self.fc[c])
            else:
                stream_temperature[c].append(self.tcout[c])
            
            for g in self.gather_split[c]:
                stream_temperature[c].append(stream_temperature[c][-1] - sum(q[h,c] for h in g)/self.fc[c])
        
        return stream_temperature
            
    def approach_temp(self):
        
        ...
             
    # 通过求解线性方程组得到个换热器流量
    def heat_load_solve(self):
        
        """初始化方程组"""
    
    def update_and_solve(self, hu):
        
        """求解方程组获得TAC和流股温度"""
        # 更新各级温度
        return self.cal_TAC()    
    
    def bounder(self):
        
        """获得公用工程边界"""    
    
    # 根据换热负荷求解TAC
    def cal_TAC(self) -> mytyping.TAC:
        
        self.stream_temp = self.stream_temperature()
        TAC = len(self.q) * self.unitc       # 固定费用
        # 数据重新计算
        for h,c in self.q:
            
            if h == 'HU':
                U = 1/self.hhu + 1/self.hc[c]
                TAC += self.q[h,c] * self.hucost         # 公用工程费用
                
                left  = self.thuin  - self.stream_temp[c][0]
                right = self.thuout - self.stream_temp[c][1]
                
            elif c == 'CU':
                U = 1/self.hh[h] + 1/self.hcu
                TAC += self.q[h,c] * self.cucost
                
                left  = self.stream_temp[h][-2] - self.tcuout
                right = self.stream_temp[h][-1] - self.tcuin
                
            else:
                U = 1/self.hh[h] + 1/self.hc[c]
                left  = self.stream_temp[h][self.zh[h,c]]     - self.stream_temp[c][self.zc[c,h]]
                right = self.stream_temp[h][self.zh[h,c] + 1] - self.stream_temp[c][self.zc[c,h] + 1]
            
            delta_T = (left + right)/2 if abs(left - right) < 1e-5 else abs(left - right)/abs(1e-5 + log(left/right))
            area = U * self.q[h,c] / delta_T

            TAC += self.acoeff * (area**self.aexp)   # 面积费用
        
        return TAC
                 
    # 黄金分割
    def Golden_cut(self, lb, ub):
        
        func = self.update_and_solve
        if (ub - lb) / (lb + 1e-3) <= 1e-3 or abs(lb - ub) <= 1e-3:
            TAC = func((lb + ub)/2)
        else:
            stopper_golden_E = 1
            x1, y1 = lb, func(lb)
            x2, y2 = ub, func(ub)
            x3 = x1 + (x2 - x1)/self.golden_cut
            y3 = func(x3)
            min_y123 = min(y1,y2,y3)
            
            # 单调性检验
            if y1 == min_y123:
                x11 = x1 + 1e-3
                y11 = func(x11)
                if y11 > y1:
                    HU = x1
                    TAC = func(x1)
                    stopper_golden_E = 0
                else:
                    x2, y2 = x3, y3
            elif y2 == min_y123:
                x22 = x2 - 1e-3
                y22 = func(x22)
                if y22 > y2:
                    HU = x2
                    TAC = func(x2)
                    stopper_golden_E = 0 
                else:
                    x1,y1 = x3,y3
  
            altcount_golden_E = 1
            while stopper_golden_E > 0:

                if altcount_golden_E == 1:
                    x3 = x1 + (x2 - x1)/self.golden_cut
                    y3 = func(x3)
                    x4 = x2 - (x2 - x1)/self.golden_cut
                    y4 = func(x4)
                    altcount_golden_E += 1
                    
                elif y4 <= y3:
                    x2, y2 = x3, y3
                    x3, y3 = x4, y4
                    x4 = x2 - (x2 - x1)/self.golden_cut
                    y4 = func(x4)
                else:
                    x1, y1 = x4, y4
                    x4, y4 = x3, y3
                    x3 = x1 + (x2 - x1)/self.golden_cut
                    y3 = func(x3)
                    
                if abs(x2 - x1)/(1e-3 + x1) < 1e-3:
                    stopper_golden_E = 0
                    HU = (x1 + x2) / 2
                    TAC = func(HU)
        
        return self.Data_pack()
        
    # 重新计算计算TAC，以及数据打包
    def Data_pack(self) -> Structure_Data:
        
        hot_temp,cool_temp = dict(),dict()
        area,q = dict(),dict()
        fh,fc = dict(),dict()
        TAC = len(self.q) * self.unitc       # 固定费用
        
        zh, zc, zhu, zcu = {}, {}, {}, {}
        HU, Area  = 0, 0
        for h in self.thin.keys():
            for g in self.gather_split[h]:
                s = sum(self.q[h,c] for c in g) / self.fh[h]
                for c in g:
                    fh[h,c] = self.q[h,c] / s if s != 0 else 0
                
        for c in self.tcin.keys():
            for g in self.gather_split[c]:
                s = sum(self.q[h,c] for h in g) / self.fc[c]
                for h in g:
                    fc[c,h] = self.q[h,c] / s if s != 0 else 0
            
        # 数据重新计算
        
        for h,c in self.q:
            q[h,c] = self.q[h,c]    
            
            if h == 'HU':
                U = 1/self.hhu + 1/self.hc[c]
                TAC += self.q[h,c] * self.hucost         # 公用工程费用
                
                hot_temp[h,c]  = [self.thuin,self.thuout]
                cool_temp[c,h] = [self.stream_temp[c][0],self.stream_temp[c][1]]
                
                HU += self.q[h,c]
                zhu['HU', c] = 1 
                
            elif c == 'CU':
                U = 1/self.hh[h] + 1/self.hcu
                TAC += self.q[h,c] * self.cucost
                
                hot_temp[h,c] = [self.stream_temp[h][-2],self.stream_temp[h][-1]]
                cool_temp[c,h] = [self.tcuout,self.tcuin]
                
                zcu[h,'CU'] = 1
                
            else:
                U = 1/self.hh[h] + 1/self.hc[c]
                zh[h,c] = self.zh[h,c]
                zc[c,h] = self.zc[c,h] 
                               
                hot_temp[h,c]  =  [self.stream_temp[h][zh[h,c]], self.stream_temp[h][zh[h,c] + 1]]
                cool_temp[c,h] =  [self.stream_temp[c][zc[c,h]], self.stream_temp[c][zc[c,h] + 1]]
                
            left,right = hot_temp[h,c][0] - cool_temp[c,h][0], hot_temp[h,c][1] - cool_temp[c,h][1]
            
            delta_T = (left + right)/2 if abs(left - right) < 1e-5 else abs(left - right)/abs(1e-5 + log(left/right))
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
    
    # 运行
    def run(self, zh: Dict, zc: Dict, zhu: Dict, zcu: Dict, *args):       
        
        self.update_struct(zh, zc, zhu, zcu)
        
        bounder = self.bounder()
        if not bounder:
            return None
        lb,ub = bounder
        if lb < ub:  # 防止数值错误
            lb += min(ub-lb,1e-5)
            ub -= min(ub-lb,1e-5)
        #print(lb,ub)
        return self.Golden_cut(lb, ub)

        # 运行
    
    def obtain_bound(self, zh: Dict, zc: Dict, zhu: Dict, zcu: Dict):       
        
        self.update_struct(zh, zc, zhu, zcu)
        
        bounder = self.bounder()
        if not bounder:
            return None

        return bounder