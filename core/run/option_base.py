
import time, os, traceback
import pandas as pd
from typing import Dict, List
from collections import defaultdict

from . import example, mytyping, Unpack_data, toplogical_sort, Numeric
from . import BMatch, Match_write
from . import Structure_Generation, structure_data_save


class PNS_Data:
    
    __slot__ = ["LHU", "UHU", "LTAC", "TAC"]
    
    def __init__(self, LHU = -1, UHU = -1, LTAC = -1, TAC = -1):
        self.LHU = LHU
        self.UHU = UHU
        self.LTAC = LTAC
        self.TAC = TAC


class Run_Base(Unpack_data):
    
    """Implementation method run"""
    
    def __init__(self, path, case, Match, solve_model):
        
        data = example().data(case)
        super(Run_Base, self).__init__(data)
        
        self.idx_i, self.idx_j = self.thin.keys(), self.tcin.keys()
        self.opt_model = solve_model(data)
        self.Enum_PNS = Match(data)
        self.match_write = Match_write(self.idx_i, self.idx_j, path / "proto_networks")
        
        self.Enum_Structures = Structure_Generation(self.thin, self.thout, self.fh, self.tcin, self.tcout, self.fc, self.EMAT, self.HRAT_MAX)#, self.Stage_Num)
        
        #self.opt_model = solve_model(data)
        self.PNS = []       # proto-networks, occupy
        self.path = path
        
        self.schedule = 0
        
        self.area_cost_min, self.area_cost_max = float('inf'), 0
        
    def _proto_network_yield(self, pns_number_limit, cutting = False):
        
        try:
            # generate proto-networks
            #start_time = time.time()
            for idx, (pn, hu) in enumerate(self.Enum_PNS.run(cutting = cutting, path = self.path), start = 1):
                
                #self.match_write.add(pn)
                #self.PNS.append(pn)

                #if idx % mytyping.FILE_Row == 0:
                #    self.match_write.write()
                
                #self.Attribute[idx] = PNS_Data(LHU = hu)
                #print(pn)
                yield pn, hu
                
                if  idx >= pns_number_limit:
                    break

            #if idx % mytyping.FILE_Row!= 0:
            #    self.match_write.write()
            
        except:
            print(traceback.format_exc())
            print(f"the proto-netowrk: {pn}")
            exit()
        
        #proto_network_number = idx
        #return proto_network_number, pns_yield_time

    def _structure_optimal(self, pn: mytyping.Proto_network):
        
        structure_number = 0
        tac, struc = mytyping.inf, None
        
        self.schedule += 1
        #if self.schedule % 100 == 0:
            #print(f"run out {self.schedule} / {len(self.PNS)}")
        
        try:
            for structure in self.Enum_Structures.Run(pn):
    
                result = self.opt_model.run(*structure)
                if result is not None:              
                    structure_number += 1
                    if float(result.TAC) < tac:
                        tac = float(result.TAC)
                        struc = result
        except:
            print(traceback.format_exc())
            zh, zc, zhu, zcu, *_ = structure
            print(f"zh = {zh}")
            print(f"zc = {zc}")
            print(f"zhu = {zhu}")
            print(f"zcu = {zcu}")
            exit()
        
        return tac, struc, structure_number

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
             
    def low_bound(self, pn: mytyping.Proto_network, data: PNS_Data) -> float:
        
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
        data.UHU = 0
        for (h,c), q in load.items():
            if h == "HU":
                U = 1/self.hhu + 1/self.hc[c]
                hr, hl = self.thuin, self.thuout
                cr, cl = self.tcout[c], self.tcout[c] - q / self.fc[c]
                
                data.UHU += q
                
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
        
        op_cost = self.hucost * data.LHU + self.cucost * self.Enthepy(data.LHU)["CU"]
        return self.unitc * len(load) + area_cost + op_cost
    
    def _proto_network_read(self, pathes):
        
        from . import read_matches
        
        for idx, pn in enumerate(read_matches(pathes), 1):
            
            self.PNS.append(pn)
            
            self.Attribute[idx] = PNS_Data(LHU = -1)
            
            yield pn
 
    def run(self, pns_number_limit = 3000):
        
        self.Attribute: Dict[int, PNS_Data] = {}

        ...
        
        #return pns_generate_time, opt_time, Enum_structure_number
    
    def _structure_save(self, structures, pn_idxs, path = None):
        
        if path is None:
            path = self.path
        
        if not os.path.exists(path):
            os.mkdir(path)
            
        write_obj = structure_data_save(self.idx_i, self.idx_j)
        for i in range(len(structures) // mytyping.FILE_Row + 1):
            
            l, r = i * mytyping.FILE_Row, min((i+1) * mytyping.FILE_Row, len(structures))  
            write_obj.write_results(structures[l: r], path / (f"structures{i+1}"), index = pn_idxs[l:r])
    
    def _results_save(self, pn_idxs):

        columns = ["LHU", "UHU", "LTAC", "TAC"]
        
        result_path = self.path / "results"
        if not os.path.exists(result_path):
            os.mkdir(result_path)
        
        for i in range(len(pn_idxs) // mytyping.FILE_Row + 1):
            
            l, r = i * mytyping.FILE_Row, min((i+1) * mytyping.FILE_Row, len(pn_idxs))   
            
            data = {"LHU": [], "UHU": [],"LTAC": [], "TAC": []}
            
            t_idx = pn_idxs[l : r]
            data["LHU"] = [f"{self.Attribute[idx].LHU: .2f}" for idx in t_idx]
            data["UHU"] = [f"{self.Attribute[idx].UHU:.2f}" for idx in t_idx]
            data["LTAC"] = [f"{self.Attribute[idx].LTAC: .2f}" for idx in t_idx]
            data["TAC"] = [(self.Attribute[idx].TAC if self.Attribute[idx].TAC is not None else -1) for idx in t_idx]

            df = pd.DataFrame(data, index = t_idx, columns = columns)
            df.index.name = "PN_IDX"
            
            df.to_csv(result_path / (f"results{i+1}.csv"))
        
    def data_save(self, structures, pn_idxs):
                
        self._structure_save(structures, pn_idxs, self.path / "structures")
        
        self._results_save(pn_idxs)
        
    def test_structure(self, zh, zc, zhu, zcu):
    
        result = self.opt_model.run(zh, zc, zhu, zcu)
        
        return result
    
    def test_pn(self, pn):
        
        tac = mytyping.inf
        for struc in self.Enum_Structures.Run(pn):
            t = self.opt_model(*struc)
            if t is not None:
                tac = min(float(t.TAC), tac)
            
        print(tac)
