from ..model import model
from .. import Numeric, toplogical_sort


class Heat_exchanger_network(model): 
    
    def __init__(self, data):
            
        super(Heat_exchanger_network, self).__init__(data)
     
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
        