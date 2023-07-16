from itertools import chain
from math import inf
from typing import Tuple
import time
from .import IS_MPN, mytyping
from . import Transshipment, match_trie, Bound


class Match(Bound):
    
    def __init__(self, data) -> None:
        
        super(Match, self).__init__(data)
        
        self.trans = Transshipment(data)
        
        self.alpha = 0.9

        self.match_idx,i = {},0         
        self.idx_match = []
        for match in list(self.scores.keys()):
            if self.scores[match] == inf:
                self.trans.fix(match, 0)
                del self.scores[match]      # 匹配固定后清除匹配
            else:
                self.match_idx[match] = i        # 需要枚举匹配的序号，用于压缩匹配
                self.idx_match.append(match)
                i += 1        
        
        self.match_exist = match_trie(len(self.match_idx))
        self.match_results = []  # List[int] 用整数表示 
        self.scheme = [0]
        self.UB_TAC = mytyping.inf
        
        self.layer_num = 0
           
    def __call__(self, *args, **kwds):
        return self.run(*args, **kwds)
    
    @staticmethod
    def show(msg):
        return
        print(msg)
    
    def solve_node(self, node, match, next_layer_nodes: list, cutting, fix_value):
        
        self.trans.fix(match, fix_value)   # 固定该节点匹配为1
        mat = self.trans.is_feasible()
        
        self.run_model_number += 1
        
        if mat is not None:
            pn, hu = mat
            
            if not cutting or not self.is_larger(pn, hu):  # 判断下界是否大于上界
                
                value = sum(1 << self.match_idx[m] for m in pn)                   # 根据枚举出的匹配计算压缩的值
                self.score_adjust(value)
                self.match_exist.add(value)
                
                self.pns += 1
                
                yield pn, hu

                if fix_value:
                    next_layer_nodes.append(node + (1 << self.match_idx[match]))                            # 可继续搜索的节点
                else:
                    next_layer_nodes.append(node)  
        else:
            self.show("Infeasible")
        self.trans.unfix(match) 
    
    # 采用广度优先搜索进行枚举
    def branch_bound_bfs(self, cutting) -> Tuple[mytyping.Proto_network, mytyping.HU]:
    
        self.utilities_score = {(h,c): v for (h,c),v in self.scores.items() if h == 'HU' or c == 'CU'}
          
        self.match_results = []  # List[int] 用整数表示 
        self.scheme = [0]
        
        enumed_matched = []
        
        self.area_cost = self.Area_supertarget(self.HRAT_MAX)
        mat = self.trans.is_feasible()               # 计算Node0
        
        start = time.time()
        if mat is not None:
            loads, hu = mat
            pn = list(loads)
            value = sum(1 << self.match_idx[m] for m in pn)                   # 根据枚举出的匹配计算压缩的值
            self.score_adjust(value)
            self.match_exist.add(value)   
            yield pn, hu
        else:
            return
        total_layer = len(self.scores)
        
        with open(self.path / "process.out", "a+") as f:
            f.write(f"{0}/{total_layer}, ---; {1}; {time.time()-start: .3f}; {1}; {1}\n")
        
        total_number = 1
        tt = time.time() - start
        
        layer = 0; node_num = 0
        while self.scheme and self.scores:
            
            start = time.time()
            self.pns, self.run_model_number = 0, 0
            layer += 1
            #print("scores: ",self.scores)
            
            next_layer_nodes = []
            #match = matches[layer - 1]
            match = self.select_match()     # 选出最不可行的节点进行枚举        
            #print(match)
            self.match_exist.order.append(self.match_idx[match])    # 顺序 + 1
            
            for node in self.scheme:   # 依次遍历二叉树每个节点
                node_val = 1 << self.stream_idx['HU'] + 1 << self.stream_idx['CU']; val = 0 
                for num in enumed_matched:                        # 固定该组合的所有匹配                 
                    if node & (1 << num):
                        self.trans.fix(self.idx_match[num],1)
                        val += 1
                        node_val |= (1 << self.stream_idx[self.idx_match[num][0]]) | (1 << self.stream_idx[self.idx_match[num][1]])  
                    else:
                        self.trans.fix(self.idx_match[num],0)

                node_num += 1
                self.show(f"Node{node_num}, status:")
                # 先运行exist判断, 可以把暂存的proto-network给更新
                if self.match_exist.exist(node + (1 << self.match_idx[match])):             # 这条组匹配存在的情况
                    next_layer_nodes.append(node + (1 << self.match_idx[match]))
                    self.show("Is part of PNS")
                else:
                    if self.valid(node_val | (1 << self.stream_idx[match[0]]) | (1 << self.stream_idx[match[1]]), self.Nmin_max - val - 1):
                        yield from self.solve_node(node, match, next_layer_nodes, cutting, 1)
                    else:
                        self.show("Infeasible")
                
                node_num += 1
                self.show(f"Node{node_num}, status:")
                # 判断为0的情况有没有存在匹配，可能也已经搜寻过了
                if self.match_exist.no_exist(node):                  # 返回为True则是没有相应的匹配需要继续搜索
                    if self.valid(node_val, self.Nmin_max - val):    
                        yield from self.solve_node(node, match, next_layer_nodes, cutting, 0)
                    else:
                        self.show("Infeasible")
                else:   
                    next_layer_nodes.append(node)
                    self.show("Is part of PNS")
                
                for num in enumed_matched:                                                  # 解除固定该组合的所有匹配                 
                    if node & (1 << num):
                        self.trans.unfix(self.idx_match[num])           

            laryer_node = len(self.scheme) * 2
            
            end = time.time()  
            
            with open(self.path / "process.out", "a+") as f:
                f.write(f"{layer}/{total_layer}; ({match[0]}, {match[1]}); {laryer_node}; {end-start: .3f}; {self.run_model_number}; {self.pns}, {self.UB_TAC}\n")

            enumed_matched.append(self.match_idx[match])
            self.scheme = next_layer_nodes                  # 需要枚举的节点  
            
            tt += end-start
            total_number += self.run_model_number

        self.run_model_number = total_number
        #print(total_number, tt)
            
    def run(self, alpha = None, cutting = False, path = None):
        
        self.path = path
        if alpha is not None:
            self.alpha = alpha
        #num = 0
        for pn, hu in self.branch_bound_bfs(cutting = cutting):
            #print(f"Proto-nework: {pn}, humin = {hu:.2f}")
            #num += 1
            #print(pn, "PN NUM: ", num)
            if IS_MPN(pn):
                yield pn, hu
                
    def branch_bound_dfs(self, *args, **kwargs):
        
        from .match_exist import tree_dfs
        match_exist = tree_dfs(self.idx_match)
        nodes = {}
        
        run_model_num = 0
        
        node_num = 0
        
        def select_match():
            order = sorted(list(self.scores), key=lambda x: -self.scores[x])
            for match in order:
                if match not in enumed_matched:
                    return match
            return None
        
        def solve():
            
            nonlocal run_model_num
            run_model_num += 1
            mat = self.trans.is_feasible()
            
            if mat is not None:
                pn, hu = mat
                if not self.is_larger(pn, hu):  # 判断下界是否大于上界
                    
                    value = sum(1 << self.match_idx[m] for m in pn)                   # 根据枚举出的匹配计算压缩的值
                    self.score_adjust(value)
                    match_exist.add(pn)
                    return pn, hu
            #else:
            #    print("Infeasible")
            return False
        
        def dfs():
            
            nonlocal node_num 
            node_num += 1
            #if len(nodes) < 5:
            #    print(f"node{node_num}, {nodes}: ")
            
            if not match_exist.exist(nodes):
                
                mat = solve()
                if not mat:
                    return 
                yield mat
            #else:
            #    print("Part of PNS")
            
            if sum(nodes.values()) >= self.Nmin_max:
                return
            
            match = select_match()
            if match is not None:
                enumed_matched.add(match)
                self.trans.fix(match, 1)
                nodes[match] = 1
                yield from dfs()
                self.trans.unfix(match)
                del nodes[match]
                
                self.trans.fix(match, 0)
                nodes[match] = 0
                yield from dfs()
                self.trans.unfix(match)
                del nodes[match]
                enumed_matched.discard(match)

        
        self.stream_idx = {s : i for i,s in enumerate(chain(self.idx_i, self.idx_j, ['HU','CU']))}
        
        self.utilities_score = {(h,c): v for (h,c),v in self.scores.items() if h == 'HU' or c == 'CU'}
        
        enumed_matched = set()
        mat = self.trans.is_feasible()               # 计算Node0
        if mat is not None:
            loads, hu = mat
            pn = list(loads)
            self.area_cost = self.Area_supertarget(self.HRAT_MAX)
            #print(self.area_cost)

            value = sum(1 << self.match_idx[m] for m in pn)                   # 根据枚举出的匹配计算压缩的值
            self.score_adjust(value)
            match_exist.add(pn)   
            yield pn, hu
        else:
            return
        
        start = time.time()
        match = select_match()
        enumed_matched.add(match)
        self.trans.fix(match, 1)
        nodes[match] = 1
        yield from dfs()
        self.trans.unfix(match)
        del nodes[match]
        
        self.trans.fix(match, 0)
        nodes[match] = 0
        yield from dfs()
        self.trans.unfix(match)
        del nodes[match]
        enumed_matched.discard(match)
        
        end = time.time()
        
        print(run_model_num, start - end)
        
    def get_data(self):
        
        return self.run_model_number, self.UB_TAC