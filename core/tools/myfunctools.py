
from collections import deque
from typing import Dict, List
from . import Numeric, mytyping

def toplogical_sort(matches: Dict[str,List], enthepy: dict) -> mytyping.Loads:
    
    """根据换热匹配求取换热器传热负荷, 用的方法是拓扑排序"""
    exist =  {st : set(sst) for st, sst in matches.items()}
    
    hu = enthepy["HU"]
    copy_enthepy = enthepy.copy()
    q = dict()
    
    start = deque([key for key in exist.keys() if len(exist[key]) == 1])
    while start:              # 求解换热器热负荷
        
        st = start.popleft()
                
        if not exist[st]:        # 判断是否存在匹配，因为可能在前面就丢掉了
            continue
        
        for sst in exist[st]:    # 获得第一个与st匹配的流股或公用工程
            break
        
        h,c = (st,sst) if st[0] == 'H' else (sst,st)
        
        q[h,c] = enthepy[st]
        exist[st].discard(sst)
        enthepy[st] = 0
        
        enthepy[sst] -= q[h,c]
        exist[sst].discard(st)
    
        if len(exist[sst]) == 1:
            start.append(sst)
    
    # 因为热公用工程可能会优先使用造成可以直接确定的换热器负荷变为未知
    for st in matches.keys():
        if st == "HU" or st == "CU":
            continue
        elif st.startswith("H"):
            eq = copy_enthepy[st] - sum(q[st,c] for c in matches[st])
        else:
            eq = copy_enthepy[st] - sum(q[h,st] for h in matches[st])
        
        if type(eq) == Numeric:
            hu, _ = eq.solve()
            break

    if type(hu) != Numeric:
        for k, v in q.items():
            if type(v) == Numeric:
                q[k] = v.value(hu)
                
    return q


def pinch_energy(thin: Dict, thout, fh, tcin: Dict, tcout, fc, TEPE: int) -> mytyping.Tuple[float, float]:
    
    idx_i = thin.keys()
    idx_j = tcin.keys()  
    # pinch candidate
    # lower bound
    tpinch = [thin[i] for i in idx_i] + [tcin[j] + TEPE for j in idx_j] \
          + [thout[i] for i in idx_i] + [tcout[j] + TEPE for j in idx_j]
        
    qsoa = qsia = zph = 0
    for x in range(len(tpinch)):
        qsoa = qsia = 0
        for i in idx_i:
            qsoa += fh[i] * (max(0, thin[i] - tpinch[x]) - max(0, thout[i] - tpinch[x]))
        for j in idx_j:
            qsia += fc[j] * (max(0, tcout[j] + TEPE - tpinch[x]) - max(0, tcin[j] + TEPE -tpinch[x]))
        zph = max(qsia - qsoa, zph)
    
    qh = zph
    q_surplus = sum(fh[i] * (thin[i] - thout[i]) for i in idx_i) - sum(fc[j] * (tcout[j] - tcin[j]) for j in idx_j)
    
    qc = qh + q_surplus
    
    return qh, qc

    
def IS_MPN(pn: mytyping.Proto_network) -> bool:
    
    def find(key):
        father = key
        while unit[father] != -1:
            father = unit[father]
        if key != father: unit[key] = father
        return father

    def add(key1, key2):
        key1 = find(key1)
        key2 = find(key2)
        if key1 != key2:
            unit[key2] = key1
    
    unit = {"HU": -1, "CU": -1}
    for h,c in pn:
        unit.update({h: -1, c: -1})

    for k1, k2 in pn:
        add(k1, k2)
    
    return len(pn) == len(unit) - sum(1 for v in unit.values() if v == -1)   

