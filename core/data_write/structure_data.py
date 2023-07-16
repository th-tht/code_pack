
import pandas as pd
from pathlib import Path
from itertools import chain, product
import os
from typing import List
from . import tuple_pack, example


class Write_Class:
    
    def __init__(self, idx_i = None, idx_j = None, case = None):
        
        if idx_i is not None and idx_j is not None:
            self.idx_i = idx_i
            self.idx_j = idx_j
        elif case is not None:
            thin, _, _, _, tcin, *_ = example().data(case)    
            self.idx_i = list(thin.keys())
            self.idx_j = list(tcin.keys())
        else:
            raise Exception("Need input streams number")

        self.all_matches = list(chain(product(self.idx_i,self.idx_j), product(self.idx_i,['CU']), product(['HU'],self.idx_j)))
        
        self.column_1 = [tuple_pack(k) for k in self.all_matches]
        self.column_2 = [tuple_pack((c,h)) for h,c in self.all_matches]
        self.column_h = [tuple_pack(k) for k in product(self.idx_i,self.idx_j)]
        self.column_c = [tuple_pack(k) for k in product(self.idx_j,self.idx_i)]
        self.column_u = [tuple_pack(k) for k in chain(product(self.idx_i,['CU']), product(['HU'],self.idx_j))]
        
        self.write_mode = "w+"
        
    def write(self, data_frame: List[dict], file_name: list, columns: list):
        
        for i, data in enumerate(data_frame):
            
            data = {tuple_pack(k): v for k,v in data.items()}
            
            if self.index is None:
                self.index = [i for i in range(1, len(data[columns[i][0]])+1)] 
            
            df = pd.DataFrame(data, index = self.index, columns=columns[i])
            
            df.index.name = "Index"
            
            if self.write_mode == "w+":        
                df.to_csv(self.data_file_path / file_name[i], mode="w+")
            else:
                df.to_csv(self.data_file_path / file_name[i], mode="a+", header = False)
    
    # need change
    def _structure(self):
    
        '''写入热流股、冷流股、公用工程结构'''
        
        zh = {key : [] for key in product(self.idx_i,self.idx_j)}
        zc = {key : [] for key in product(self.idx_j,self.idx_i)}
        zu = {key : [] for key in chain(product(['HU'],self.idx_j), product(self.idx_i,['CU']))}
        
        ...        
        
        self.write([zh,zc,zu], ['hot_structure.csv', 'cool_structure.csv', 'utilities_structure.csv'], 
                   [self.column_h, self.column_c, self.column_u])
        
    def _temperature(self):
        '''写入温度数据'''
        
        th = {key : [] for key in self.all_matches}
        tc = {(c,h) : [] for h,c in self.all_matches}
        
        for struc in self.structures:
            for h,c in th.keys():
                if struc is None:
                    th[h,c].append("-1")
                    tc[c,h].append("-1")
                else:
                    th[h,c].append(tuple_pack(struc.th_sp[h,c]) if (h,c) in struc.th_sp else "0")
                    tc[c,h].append(tuple_pack(struc.tc_sp[c,h]) if (c,h) in struc.tc_sp else "0")

        self.write([th,tc], ['hot_temperature.csv', 'cool_temperature.csv'], [self.column_1, self.column_2])
               
    def _load(self):
        
        '''写入热负荷数据'''
        q = {key : [] for key in self.all_matches}
        
        for struc in self.structures:
            for key in q.keys():
                if struc is None:
                    q[key].append("-1")
                else:
                    q[key].append('%s'%struc.q[key] if key in struc.q else "0")
        
        self.write([q], ['load.csv'], [self.column_1])

    def _area(self):
        
        '''写入面积数据'''
        area = {key : [] for key in self.all_matches}
        
        for struc in self.structures:              
            for key in area.keys():
                if struc is None:
                    area[key].append("-1")
                else:
                    area[key].append('%s'%struc.area[key] if key in struc.area else "0")
        
        self.write([area], ['area.csv'], [self.column_1])

    def _flow(self):
        
        '''写入支流'''
        
        fh = {key : [] for key in product(self.idx_i,self.idx_j)}
        fc = {key : [] for key in product(self.idx_j,self.idx_i)}
        
        for struc in self.structures:
            
            for h,c in product(self.idx_i,self.idx_j):
                if struc is None:
                    fh[h,c].append("-1")
                    fc[c,h].append("-1")
                else:
                    fh[h,c].append("%s"%struc.fh_sp[h,c] if (h,c) in struc.fh_sp else "0")
                    fc[c,h].append("%s"%struc.fc_sp[c,h] if (c,h) in struc.fc_sp else "0")
            
        self.write([fh, fc], ['hot_flow.csv', 'cool_flow.csv'], [self.column_h, self.column_c])
       
    def _other(self):
        
        '''写入TAC,HU等'''
        other = {key : [] for key in ['TAC', 'HU','Area']}
        for struc in self.structures:
            other['TAC'].append("%s"%struc.TAC if struc is not None else "-1")
            other['HU'].append("%s"%struc.HU if struc is not None else "-1")
            other['Area'].append("%s"%struc.Area if struc is not None else "-1")
        
        if self.index is None:
            self.index = [i for i in range(1, len(self.structures) + 1)]
        
        df_other = pd.DataFrame(other, index = self.index, columns =  ['TAC', 'HU','Area'])
        df_other.index.name = "Index"

        df_other.to_csv(self.data_file_path / 'other.csv', mode = self.write_mode)

        
        
    def write_results(self, structures, data_file_path : Path, mode = 'w+', index = None):
        
        self.index = index
        self.data_file_path = data_file_path
        self.structures = structures
        self.write_mode = mode    
        
        if not os.path.exists(data_file_path):
            os.makedirs(data_file_path)
            
        self._other()
        self._structure()
        self._temperature()
        self._load()
        self._area()
        self._flow()
     

class SWS(Write_Class):
    
    def __init__(self, idx_i=None, idx_j=None, case=None):
        super().__init__(idx_i, idx_j, case)
    
    def _structure(self):
    
        '''写入热流股、冷流股、公用工程结构'''
        
        zh = {key : [] for key in product(self.idx_i,self.idx_j)}
        zc = {key : [] for key in product(self.idx_j,self.idx_i)}
        zu = {key : [] for key in chain(product(['HU'],self.idx_j), product(self.idx_i,['CU']))}
        
        for struc in self.structures:
            for h,c in zh.keys():
                if struc is None:
                    zh[h,c].append("-1")
                    zc[c,h].append("-1")
                else:
                    zh[h,c].append(str(struc.zh_sp[h,c]) if (h,c) in struc.zh_sp else "0")
                    zc[c,h].append(str(struc.zc_sp[c,h]) if (c,h) in struc.zc_sp else "0")

            for key in zu.keys():
                if struc is None:
                    zu[key].append("-1")
                else:
                    if (key in struc.zhu_sp) or (key in struc.zcu_sp):
                        zu[key].append('1')
                    else:
                        zu[key].append('0') 
        
        self.write([zh,zc,zu], ['hot_structure.csv', 'cool_structure.csv', 'utilities_structure.csv'], 
            [self.column_h, self.column_c, self.column_u])
         
class SSWS(Write_Class):
    
    def __init__(self, idx_i=None, idx_j=None, case=None):
        super().__init__(idx_i, idx_j, case)
    
    def _structure(self):
    
        '''写入热流股、冷流股、公用工程结构'''
        
        zh = {key : [] for key in product(self.idx_i,self.idx_j)}
        zc = {key : [] for key in product(self.idx_j,self.idx_i)}
        zu = {key : [] for key in chain(product(['HU'],self.idx_j), product(self.idx_i,['CU']))}
        
        for struc in self.structures:
            for h,c in zh.keys():
                if struc is None:
                    zh[h,c].append("-1")
                    zc[c,h].append("-1")
                else:
                    zh[h,c].append(tuple_pack(struc.zh_sp[h,c]) if (h,c) in struc.zh_sp else "0")
                    zc[c,h].append(tuple_pack(struc.zc_sp[c,h]) if (c,h) in struc.zc_sp else "0")

            for key in zu.keys():
                if struc is None:
                    zu[key].append("-1")
                else:
                    if (key in struc.zhu_sp) or (key in struc.zcu_sp):
                        zu[key].append('1')
                    else:
                        zu[key].append('0') 
        
        self.write([zh,zc,zu], ['hot_structure.csv', 'cool_structure.csv', 'utilities_structure.csv'], 
            [self.column_h, self.column_c, self.column_u])
    
    
    
    
    
    
    
