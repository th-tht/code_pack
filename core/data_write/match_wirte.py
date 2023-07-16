import os
import pandas as pd
from itertools import chain, product
from pathlib import Path
from . import tuple_pack

class Match_write:
    
    def __init__(self, idx_i, idx_j, path = None):
        
        self.pns = {(h,c): [] for h,c in chain(product(idx_i,idx_j),product(['HU'], idx_j), product(idx_i,['CU']))}
        self.column = [tuple_pack(k) for k in self.pns.keys()]        
        
        self.path = path
        self.pn_idx = 0
        self.file_idx = 1
        
    def __len__(self):
        
        return len(self.pns)
    
    def add(self, pn):
        
        self.pn_idx += 1
        
        for k in self.pns:
            self.pns[k].append("0")
        for k in pn:
            self.pns[k][-1] = "1"
    
    def write(self, path = None, file_idx = None) -> Path:
        
        if path is None:
            path = self.path
        else:
            self.path = path
        
        if file_idx is None:
            file_idx = self.file_idx
        else:
            self.file_idx = file_idx
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        data = dict()
        for k,v in self.pns.items():
            data[tuple_pack(k)] = v  
         
        df = pd.DataFrame(data, index = [i for i in range(self.pn_idx - len(self.pns["H1","C1"]) + 1, self.pn_idx + 1)], columns=self.column)
        
        df.index.name = "Index"
        write_path = path / ("proto_network%s.csv"%file_idx)
        
        df.to_csv(write_path, mode="w+")
        
        self.file_idx += 1
        for k in self.pns:
            self.pns[k] = []
            
        return write_path
        
    def append(self, path, pn, idx):
        
        data = {k: ["0"] for k in self.pns.keys()}
        for k in pn:
            data[k] = ["1"]
        
        df = pd.DataFrame(data, index=[idx], columns=self.column)
        df.to_csv(path, 'a+', header=False)
        
        
        
        



