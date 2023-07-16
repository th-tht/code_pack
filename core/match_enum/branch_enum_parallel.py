from itertools import chain
from math import inf
import time
from collections import deque, defaultdict
from .import  mytyping, Structure_Data, Unpack_data, Numeric, IS_MPN, toplogical_sort
from . import  Bound, Transshipment
from . import match_trie_for_parallel as match_trie_p
from multiprocessing import Manager, Pool, Queue
import signal

class SEM(Unpack_data):
    
    def __init__(self, data, match_idx, idx_match, optimal_model):
        
        super().__init__(data)
        
        self.alpha = 0.9
        self.idx_i = list(self.thin.keys())
        self.idx_j = list(self.tcin.keys())
        self.trans = Transshipment(data)  
        self.length = len(self.idx_i) + len(self.idx_j) + 1
        self.match_idx, self.idx_match = match_idx, idx_match
        self.opt_model = optimal_model
        
    def pre_forbid(self, match_list: list):
        
        for match in match_list:
            self.trans.fix(match, 0)
        
    def solve_node(self, node: int, size: int, 
                   struct_pipe: Queue, node_pipe: Queue, 
                   pn_pipe: Queue, UB_TAC, lock):
        
        for idx in range(size):
            self.trans.fix(self.idx_match[idx], (node >> idx) & 1)
        
        mat = self.trans.is_feasible() 
        if mat is not None:
            loads, hu = mat
            pn = list(loads)
            value = sum(1 << self.match_idx[m] for m in pn)                   # 根据枚举出的匹配计算压缩的值
            pn_pipe.put(value)
            
            if IS_MPN(pn):
                pn_lowbound = self.low_bound(pn, hu)
                if pn_lowbound < UB_TAC.value - 1e-5:
                    
                    struct: Structure_Data = self.opt_model(pn)
                    if struct is not None:       
                        if float(struct.TAC) < UB_TAC.value:
                            
                            lock.acquire()
                            UB_TAC.value = float(struct.TAC)
                            lock.release()
                            
                            struct_pipe.put(struct)             # 传递最优结构回主进程
            if size < len(self.match_idx):
                node_pipe.put((node + (1 << size), size + 1))
                node_pipe.put((node, size + 1))
                    
        for match in self.idx_match[:size]:
            self.trans.unfix(match)
    
    def Enthepy(self, hu):
        
        enthepy = {"HU" : hu, "CU": hu}
        for h in self.thin.keys():
            enthepy[h] = self.fh[h] * (self.thin[h] - self.thout[h])
            enthepy["CU"] += enthepy[h]
        
        for c in self.tcin.keys():
            enthepy[c] = self.fc[c] * (self.tcout[c] - self.tcin[c])
            enthepy["CU"] -= enthepy[c]
  
        return enthepy
    
    def solve_max_hu(self, load: mytyping.Loads) -> mytyping.Loads:
        
        hu = mytyping.inf
        
        for (h,c), v in load.items():
            eql = eqr = -self.EMAT
            if h == "HU":
                eqr += self.thuout - (self.tcout[c] - v/self.fc[c])    
            elif c == "CU":
                eql += self.thout[h] + v / self.fh[h] - self.tcuout
            else:
                eql += self.thin[h] - v / self.fc[c] - self.tcin[c]
                eqr += self.thin[h] - v / self.fh[h] - self.tcin[c]
            
            if type(v) == Numeric and v.is_right():
                hu = min(hu, v.solve()[0])
            
            if type(eql) == Numeric and eql.is_right():
                hu = min(hu, eql.solve()[0])
            
            if type(eqr) == Numeric and eqr.is_right():
                hu = min(hu, eqr.solve()[0])
        
        return {k: (v if type(v) != Numeric else v.value(hu)) for k,v in load.items()}
             
    def low_bound(self, pn: mytyping.Proto_network, lhu) -> float:
        
        # Topological sort for heat transfer
        matches = defaultdict(list)
        for h,c in pn:
            matches[h].append(c)
            matches[c].append(h)
        
        hu = Numeric(var = 1)
        if "HU" not in matches:
            hu = 0
    
        load = toplogical_sort(matches, self.Enthepy(hu))
        # obtain largest hu
        load = self.solve_max_hu(load)
        area_cost = 0
        for (h,c), q in load.items():
            if h == "HU":
                U = 1/self.hhu + 1/self.hc[c]
                hr, hl = self.thuin, self.thuout
                cr, cl = self.tcout[c], self.tcout[c] - q / self.fc[c]
                
            elif c == "CU":
                U = 1/self.hcu + 1/self.hh[h]
                hr, hl = self.thout[h] + q / self.fh[h], self.thout[h]
                cr,cl = self.tcuout, self.tcuin
                
            else:
                U = 1/self.hh[h] + 1/self.hc[c]
                
                hr, hl = self.thin[h], self.thin[h] - q / self.fh[h]
                cr, cl = self.tcin[c] + q / self.fc[c], self.tcin[c]
            
            l, r = hl - cl, hr - cr     
            
            if l <= self.EMAT - 1e-5 or r <= self.EMAT - 1e-5:
                return mytyping.inf
            
            if abs(r - l) <= 1e-5:
                lmtd = (l + r)/2
            else:
                lmtd = abs(r - l) / abs(1e-5 + mytyping.log(r/l))
            
            area_cost += self.acoeff * (q * U / lmtd)**self.aexp            
    
        #print("area_cost: ", area_cost)
        #self.area_cost_max = max(area_cost, self.area_cost_max)
        #self.area_cost_min = min(area_cost, self.area_cost_min)
        
        op_cost = self.hucost * lhu + self.cucost * self.Enthepy(lhu)["CU"]
        return self.unitc * len(load) + area_cost + op_cost
 

class PMatch(Bound):
    
    def __init__(self, data, optimal_model) -> None:
         
        super().__init__(data)
           
        forbid = []
        for match in list(self.scores.keys()):
            if self.scores[match] == inf:
                forbid.append(match)  
                del self.scores[match]      # 匹配固定后清除匹配
        
        self.idx_match = sorted(self.scores.keys(), key = lambda x: self.scores[x])
        self.match_idx = {match: idx for idx,match in enumerate(self.idx_match)}
        
        self.match_exist = match_trie_p(len(self.match_idx))
        self.UB_TAC = mytyping.inf
        
        self.sem = SEM(data, self.match_idx, self.idx_match, optimal_model)
        self.sem.pre_forbid(forbid)
           
    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)

    @staticmethod
    def err_call_back(err):
        print("error encoming: ", err)
        exit()
    
    def valid(self, node, size):
        
        # 根据剩余的点数，查看还要多少节点能够满足每条流股至少有一个换热, 
        nodes = 0
        num = 0
        for idx, (h,c) in enumerate(self.idx_match[:size]):
            if (node >> idx) & 1:
                nodes |= (1 << self.stream_idx[h]) | (1 << self.stream_idx[c]) 
                num += 1
        
        need = 0
        for st in chain(self.idx_i, self.idx_j):
            if nodes & (1 << self.stream_idx[st]) == 0:
                need |= 1 << self.stream_idx[st]
        
        op, cache = 0, 0
        for h,c in self.idx_match[size:]:
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
    
        return need == cache and op <= self.Nmin_max - num
        
    def run(self,  Target_TAC, path, process_num):
        
        def kill(*avg):
            pool.terminate()
        #signal.signal(signal.SIGUSR1, kill)
        
        start = time.time()
        
        b_struct: Structure_Data = None
        node_list = deque()
        with Manager() as manager:
            
            pool = Pool(processes = process_num)
            lock = manager.Lock()
            self.UB_TAC = manager.Value("f", float("inf"))
            struct_pipe = manager.Queue(128)
            node_pipe = manager.Queue(128)
            pn_pipe = manager.Queue(128)

            pool.apply_async(self.sem.solve_node, 
                             (0, 0, struct_pipe, node_pipe, pn_pipe, self.UB_TAC, lock), 
                             error_callback= self.err_call_back)
           
            num = 0
            while node_list or len(pool._cache) > 0:
                
                while not pn_pipe.empty():
                    self.match_exist.add(pn_pipe.get())

                while not struct_pipe.empty():
                    struct: Structure_Data = struct_pipe.get()
                    if b_struct is None or float(struct.TAC) < float(b_struct.TAC):
                        
                        with open(path / "process.txt", "a+") as f:
                            f.write(f"the new TAC is {struct.TAC}, time is {time.time() - start: .2f}\n\n")
                        
                        b_struct = struct
                
                while not node_pipe.empty():
                    node_list.append(node_pipe.get())
                
                if self.UB_TAC.value < Target_TAC + 2:
                    break

                if node_list:
                    new_node, size = node_list.popleft()
                    
                    if not self.valid(new_node, size):
                        continue
                        
                    if self.match_exist.exist(new_node, size) and size < len(self.idx_match):
                        node_list.append((new_node + (1 << size), size + 1))
                        node_list.append((new_node, size + 1))
                        continue
                    
                    pool.apply_async(self.sem.solve_node, 
                                    (new_node, size, struct_pipe, node_pipe, pn_pipe, self.UB_TAC, lock), 
                                    error_callback= self.err_call_back)
            
            
            UBTAC = self.UB_TAC.value
            pool.terminate()
            pool.close()
            pool.join()

        return b_struct, UBTAC, f"{time.time() - start: .2f}"


    





