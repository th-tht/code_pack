
import time, os, traceback
import pandas as pd
from typing import Dict, List
from collections import defaultdict

from . import example, mytyping, Unpack_data
from . import PMatch, Match_write
from . import  Structure_Generation, structure_data_save

class Run(Unpack_data):
    
    def __init__(self, path, case, solve_model):

        data = example().data(case)
        
        super().__init__(data)
        
        self.path = path
        self.opt_model = solve_model(data)
        self.Enum_Structures = Structure_Generation(self.thin, self.thout, self.fh, self.tcin, self.tcout, self.fc, self.EMAT)#, self.Stage_Num)
        
        self.model = PMatch(data, self.optimal_model)
    

    def optimal_model(self, pn):
        
        tac = mytyping.inf
        struct = None
        try:
            for structure in self.Enum_Structures.Run(pn):
    
                result = self.opt_model.run(*structure)
                if result is not None:              
                    if float(result.TAC) < tac:
                        tac = float(result.TAC)
                        struct = result
        except:
            print(traceback.format_exc())
            zh, zc, zhu, zcu, *_ = structure
            print(f"zh = {zh}")
            print(f"zc = {zc}")
            print(f"zhu = {zhu}")
            print(f"zcu = {zcu}")
            exit()
        
        return struct
    
    def run(self, process_num):
        
        struct, TAC, time = self.model(self.Target_TAC, self.path, process_num)
        
        print("Run out")
        
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        write_obj = structure_data_save(self.idx_i, self.idx_j)

        
        write_obj.write_results([struct], self.path / (f"structures"), index = [1])
        
        return TAC, time
    
      