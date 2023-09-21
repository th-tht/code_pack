from .option_base import *

class Run(Run_Base):
    
    '''算分支树节点的下界, 然后计算, 使用面积超目标估算面积费用, 使用最小公用工程用量估算公用工程'''
    
    def __init__(self, path, case, solve):
        
        super(Run, self).__init__(path, case, BMatch, solve)

    def run(self, *avg, pns_number_limit = mytyping.inf):
        
        self.Attribute: Dict[int, PNS_Data] = {}
        Ub_TAC = mytyping.inf
        start_time, Enum_structure_number = time.time(), 0
        pn_idxs = []
        pns_yield_time = opt_time = 0
        results_structures = []
        
        PNN = EPNN = 0
        terminal_time = 12 * 3600
        for idx, (pn, hu) in enumerate(self._proto_network_yield(pns_number_limit, cutting = True), start = 1):
            PNN += 1
            #self.Attribute[idx].LTAC = self.low_bound(self.PNS[idx - 1], self.Attribute[idx])
            LTAC = self.low_bound(pn, PNS_Data(LHU = hu))
            
            #print(pn, LTAC)
            #print("PNLB: ", LTAC)
            #pn_idxs.append(idx)
            pns_yield_time += time.time() - start_time
            start_time = time.time()
            
            if LTAC >= Ub_TAC - 1e-3:
                continue
            
            EPNN += 1
            tac, struc, num = self._structure_optimal(pn)
            #print("UB:", tac)
            #print(tac)
            #if PNN >= 8:
            #    exit()
                
            opt_time += time.time() - start_time
            start_time = time.time()
            
            Enum_structure_number += num
            #self.Attribute[idx].TAC = tac
            #results_structures.append(struc)
            
            if tac <= Ub_TAC:
                pn_idxs = [idx]
                results_structures = [struc]
                self.Enum_PNS.update_ub(tac)
                Ub_TAC = tac
            
            if Ub_TAC < self.Target_TAC + 2.5:
                break
        
        self.Attribute[pn_idxs[0]] = PNS_Data(TAC = results_structures[0].TAC)
        self.data_save(results_structures, pn_idxs)
        
        return pns_yield_time, opt_time, PNN, EPNN, Enum_structure_number, self.Enum_PNS.get_data()[0], Ub_TAC