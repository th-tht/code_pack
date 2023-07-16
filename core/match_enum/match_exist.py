# 保存的匹配的顺序和枚举的顺序不对应, 应该按照分支节点的顺序逐渐分支下去递增分层
class match_trie:
    
    def __init__(self, length: int) -> None:
        self.length = length
        self.map = [None] * length
        self.order = []
        self.end = False               # 是不是order 到头后的尾部节点
        self.match_sets = []
        self.exist_match = 0
    
    def update(self, node, idx):            
        '''
        更新此节点,order加深,往下拓展一层
        '''     
        l,r = [],[]
        le,re = 0,0
        for num in node.match_sets:
            if num & (1 << idx):
                re |= num
                r.append(num)
            else:
                le |= num
                l.append(num)

        node.match_sets = l
        node.exist_match = le         
        if not l: self.end = False          # 找到下个节点后看看是不是目前所有匹配都可以分过去了
        
        node.map[idx] = match_trie(self.length)    # 初始化下个节点参数
        node.map[idx].match_sets = r
        node.map[idx].exist_match = re
        if r: node.map[idx].end = True

    # 添加匹配组
    def add(self, match: int):     # 用整数来表示每个匹配组, 与在保存的匹配组对应的下标
        '''
        添加匹配, 根据现有的order进行递进,如到底则保存匹配,需要是否需要根据order加深
        '''
        node = self
        for idx in self.order:
            if match & (1 << idx):
                if node.map[idx] is None:     
                    if node.end:              # 判断这条路有没有走过
                        self.update(node, idx)     
                    else:   
                        node.map[idx] = match_trie(self.length)
                node = node.map[idx]
        
        if len(self.order) < self.length:       # 没有枚举结束所有的节点，需要暂时保存匹配
            node.match_sets.append(match)
            node.exist_match |= match
            node.end = True
                            
    # 判断该匹配是否以及存在
    def exist(self, match: int) -> bool:
        '''根据之前的匹配判断该匹配前序是否存在，以及存在前序末尾则递进'''
        node = self
        for idx in self.order:
            if match & (1 << idx):
                if node.map[idx] is None:
                    if node.exist_match & (1 << idx):
                        self.update(node, idx)
                    else:
                        return False
                node = node.map[idx]
        return True
    
    def no_exist(self, match: int) -> bool:       # 先枚举匹配为1的情况，只需要判断是否还有别的枚举出来就行了？因为前面的已经枚举过的固定死了？
        '''
        枚举存在的情况之后,判断将此匹配设置为0是否可行
        '''
        # 代码没有问题，但是有一个前提，就是exist函数必须在no_exist前运行一次，否则会导致多余节点，也会导致后期速度变慢
        node = self
        for idx in self.order:
            if match & (1 << idx):
                if node.map[idx] is None:           # 因为不存在，所以没有分支了
                    self.update(node, idx)
                node = node.map[idx]
        if node.exist_match == 0:
            return True
        return False
    

#################################
# 为采用深度搜索建立的一个结构简单的树
        
class tree_dfs:
    
    def __init__(self, order):
        
        self.order_idx = {ma: idx for idx, ma in enumerate(order)}
        self.order = order
        self.map = []
    
    def add(self, pn: list):
        
        pn = [self.order_idx[ma] for ma in sorted(pn, key = lambda x: self.order_idx[x])]
        self.map.append(sum(1 << idx for idx in pn))
        
    def exist(self, node: dict):
       
        for pn in self.map:
            for m,v in node.items():
                if (v == 0 and pn >> self.order_idx[m] & 1 == 1) or (v == 1 and pn >> self.order_idx[m] & 1 == 0):
                    break
            else:
                return True
            
        return False


##########################################
# 用于并行计算的树
class match_trie_for_parallel:
    
    def __init__(self, length: int) -> None:
        self.length = length
        self.map = [None] * length
        self.end = False               # 是不是order 到头后的尾部节点

    def add(self, pn: int):
        
        node = self
        for i in range(self.length):
            if pn >> i & 1:
                if node.map[i] is None:
                    node.map[i] = match_trie_for_parallel(self.length)
                node = node.map[i]
        node.end = True
    
    def exist(self, check_node, size):
        
        node = self
        for i in range(size):
            if check_node >> i & 1:
                if node.map[i] is None:
                    return False
                node = node.map[i]
            
        if node.end or any(n is not None for n in node.map[size:]):
            return True

        return False
        
        
if __name__ == '__main__': 
    
    obj = match_trie_for_parallel(3)
    
    obj.add(0b111)
    obj.add(0b101)
    
    print(obj.exist(0b011, 2)) # True
    print(obj.exist(0b011, 3)) # False
    print(obj.exist(0b001, 2)) # True
    print(obj.exist(0b001, 3)) # False
    print(obj.exist(0b001, 1)) # True
    print(obj.exist(0b000, 1)) # False
    
    exit()
    
    obj = tree_dfs([("H1","C1"), ("H1", "C2"), ("H2","C2")])
    
    obj.add([("H1","C1"),("H2","C2")])
    
    print(obj.exist({("H1","C1"): 1, ("H2","C2"): 0}))
    
    exit()
    
    
    obj = match_trie(6)
    obj.order = [3,2,1,0]
    obj.add(0b010101)
    obj.add(0b110100)
    print(obj.exist(0b0101))
    print(obj.no_exist(0b0100))
    obj.order.append(4)

    #obj.add(0b11100100)
    print(obj.exist(0b10101))
    print(obj.no_exist(0b00101))





