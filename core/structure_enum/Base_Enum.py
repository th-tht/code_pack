from itertools import chain, combinations
from collections import deque, defaultdict
from . import mytyping, Numeric, toplogical_sort, pinch_energy

class Enum_Base:
    
    def __init__(self, *avg, stage_num = mytyping.inf) -> None:
        
        self.thin, self.thout, self.fh, self.tcin, self.tcout, self.fc, self.EMAT, self.HRAT_MAX = avg
        self.stage_num = stage_num
        
        self.stream_topology: mytyping.Dict[str, set] = dict()  # 拓扑排序长度
        
        self.humax, _ = pinch_energy(self.thin, self.thout, self.fh, self.tcin, self.tcout, self.fc, self.HRAT_MAX)
    
    def Enthepy(self, hu):
        
        enthepy = {"HU" : hu, "CU": hu}
        for h in self.thin.keys():
            enthepy[h] = self.fh[h] * (self.thin[h] - self.thout[h])
            enthepy["CU"] += enthepy[h]
        
        for c in self.tcin.keys():
            enthepy[c] = self.fc[c] * (self.tcout[c] - self.tcin[c])
            enthepy["CU"] -= enthepy[c]
        
        return enthepy
    
    def update_hu_bound(self, expr: Numeric):
        
        value, st = expr.solve()
        if st == "r":
            self.hu_bound[1] = min(value, self.hu_bound[1])
        else:
            self.hu_bound[0] = max(value, self.hu_bound[0])
    
    def initial_hu_bound(self, expr_list: mytyping.List[Numeric] = None):
        
        self.hu_bound = [0, mytyping.inf]
        if expr_list is None:
            return
        
        for expr in expr_list:
            self.update_hu_bound(expr)
      
    def input_match(self, matches: mytyping.Proto_network):
        
        # 加个功能判断是否能够求出换热量来
                    
        self.n_matches = {k: [] for k in chain(self.thin.keys(), self.tcin.keys())}
        
        self.zhu, self.zcu = dict(), dict()

        matches_list = defaultdict(list)
        
        for h,c in matches:
            if h == 'HU':
                self.zhu['HU',c] = 1
            elif c == 'CU':
                self.zcu[h, 'CU'] = 1
            else:
                self.n_matches[h].append(c)
                self.n_matches[c].append(h)
            
            matches_list[h].append(c)
            matches_list[c].append(h)
        
        hu = Numeric(var = 1)
        if "HU" not in matches_list:
            hu = 0
            
        self.q = toplogical_sort(matches_list, self.Enthepy(hu))
        
        self.hu_expr = []
        self.initial_hu_bound([v for v in self.q.values() if type(v) == Numeric])
        #print(self.q)
        
        u = min(self.hu_bound[1], self.humax)
        self.q = toplogical_sort(matches_list, self.Enthepy(u))
        
        #return all(type(v) != Numeric for v in self.q.values())
    
    def divide_match(self, num: int) -> list:

        '''将流股所具有的匹配数目确定分给不同的级数量'''
        tmp = []  
        def dfs(num: int):
            
            if len(tmp) > self.stage_num:     # 限制一条流股的级数生成
                return
            
            if num == 0:
                yield tmp
                return 
            for i in range(1,num+1):
                tmp.append(i)
                yield from dfs(num-i)
                tmp.pop()
        
        yield from dfs(num)
    
    # 计算topo长度从而计算级数
    def _add_node(self, st, stream_in_stage):
        
        for i in range(len(stream_in_stage)-1):
            for ms in stream_in_stage[i]:
                for nms in stream_in_stage[i+1]:
                    self.stream_topology[self.swap(st, ms)].add(self.swap(st, nms))
    
    def _delete_node(self, st, stream_in_stage):
        
        for i in range(len(stream_in_stage)-1):
            for ms in stream_in_stage[i]:
                for nms in stream_in_stage[i+1]:
                    self.stream_topology[self.swap(st, ms)].discard(self.swap(st, nms))
    
    def topology_length(self) -> bool:
        
        def bfs(m):
            
            if m in visit:
                return length_arr[m]
            
            visit.add(m)
            if not self.stream_topology[m]:
                return 1
        
            return max(bfs(nm) + 1 for nm in self.stream_topology[m])
                   
        length_arr = {m: 1 for m in self.stream_topology}
        visit = set()
        
        for m in length_arr:
            if m in visit:
                continue
            length_arr[m] = max(bfs(m), length_arr[m])
        
        return max(length_arr.values()) <= self.stage_num
    
    def stream_divide(self, nums: list, stream, match_stream:list) -> mytyping.List[mytyping.List[str]]:
    
        '''
        根据不同级拥有的匹配数目，将所有匹配分到不同级。
        返回的是根据不同级的数目分过去的匹配
        '''
        arr = match_stream
        res = []
        
        def dfs(arr, idx):
            
            if not arr:
                #self._add_node(stream, res)
                #if self.topology_length():
                yield res
                #self._delete_node(stream, res)
                return 
            
            for arr_cc in combinations(arr, nums[idx]):
                res.append(arr_cc)
                
                arr_cc = set(arr_cc)
                yield from dfs([k for k in arr if k not in arr_cc], idx + 1)
                res.pop()

        yield from dfs(arr, 0)
              
    def stream_structure_generate(self, stream: str, match_stream: list) -> dict:
    
        '''
        生成流股结构
        '''        
             
    def sort_streams(self) -> mytyping.Stream_index:
            
        # 流股结构的生成顺序，选取词条流股所有匹配中最小的？
        # 选择枚举的流股顺序, 可以从小到大, 设计一个备用数组, 
        streames_sort = sorted(self.n_matches.keys(), key = lambda x: \
            (sum(1 for y in self.n_matches[x] if type(self.q[self.swap(x,y)]) == Numeric), len(self.n_matches[x])))

        return streames_sort
    
    def select_stream(self, st_idx: int) -> mytyping.stream:
            
        return self.streams_selects[st_idx]
    
    @staticmethod
    def swap(st, sst):
        if st[0] == 'H':
            return st,sst
        else:
            return sst,st
    
    def tex_update(self, match, left, right) -> bool:
            
        if match[0][0] == 'H':
            h,c = match
            self.teh[h,c] = (left, right)
        else:
            c,h = match
            self.tec[c,h] = (left, right)
    
        if self.teh[h,c] is not None and self.tec[c,h] is not None:
            
            if any(type(v) == Numeric for v in self.teh[h,c]) or any(type(v) == Numeric for v in self.tec[c,h]):
                
                l = self.teh[h,c][0] - self.tec[c,h][0] + 1e-5 - self.EMAT
                r = self.teh[h,c][1] - self.tec[c,h][1] + 1e-5 - self.EMAT
                if type(l) == Numeric:
                    self.hu_expr.append(l)
                    self.update_hu_bound(l)
                else:
                    if l < 0: return False
                if type(r) == Numeric:
                    self.hu_expr.append(r)
                    self.update_hu_bound(r)
                else:
                    if r < 0: return False
                return self.hu_bound[0] - 1e-5 <= self.hu_bound[1]
            
            return (self.teh[h,c][0] - self.tec[c,h][0] + 1e-5 >= self.EMAT) and \
                (self.teh[h,c][1] - self.tec[c,h][1] + 1e-5 >= self.EMAT)

        return True
       
    def temperature_judge(self, struct: dict) -> bool:
        
        '''
        温度判断
        '''        
  
    def Run(self, proto_network: mytyping.Proto_network):
        
        self.stream_topology = {m : set() for m in proto_network}    

        #status = 1 if self.input_match(proto_network) else 0
        self.input_match(proto_network)
        self.streams_selects = self.sort_streams()
        self.teh = {(h,c): None for h,c in self.q.keys()}             # 每个换热器在冷流股侧的左右两段温度
        self.tec = {(c,h): None for h,c in self.q.keys()}
        
        length = len(self.thin) + len(self.tcin)
        zh,zc = {},{}
        
        def config(stream_idx):
            
            if stream_idx == length:
                #print(self.teh)
                #print(self.tec)
                yield zh.copy(), zc.copy(), self.zhu, self.zcu
                return
            
            st = self.select_stream(stream_idx)
            for struct in self.stream_structure_generate(st, self.n_matches[st]):
                
                if st[0] == 'H':
                    zh.update(struct)
                else:
                    zc.update(struct)
                temp_hu_expr_list = self.hu_expr.copy()
                # 计算对应的换热器的传热温差，判断是否继续进行枚举
                #print(struct)
                if not self.temperature_judge(struct):   
                    self.hu_expr = temp_hu_expr_list
                    self.initial_hu_bound()  
                    continue
                yield from config(stream_idx + 1)
                self.hu_expr = temp_hu_expr_list
                self.initial_hu_bound()
                
            # 计算得到的流股进出口温度需要丢弃,防止后续计算有bug 
            for sst in self.n_matches:
                if st[0] == 'H':
                    self.teh[st,sst] = None
                else:
                    self.tec[st,sst] = None       
                        
        yield from config(0)
        
