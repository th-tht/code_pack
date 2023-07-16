# utf-8
from multiprocessing import Manager, Pool
from pathlib import Path
import sys, os

path = Path(os.path.abspath(__file__)).parent
sys.path.append(str(path))

from core import mytyping, PPart1, Nsolve_model
 
    
def save_p(path, TAC, time):
    
    with open(path / "time_file.txt", "w+") as f:
        
        f.write(f"Total time : {time} s\n")
        f.write(f"TAC: {TAC: .2f} s\n")



# 并行分布进程，对多个匹配文件进行计算
def run(path: Path, cases: list, Run, pns_limit = mytyping.inf):
    
    #sys.argv.append("example9")
    if not os.path.exists(path):
        os.mkdir(path)
    
    for i in cases:
        
        if i < 10:
            process_num = 4
        else:
            process_num = 16
        
        case = "example%s"%i

        path = path / case
        
        if not os.path.exists(path):
            os.mkdir(path)
        obj = Run(path, case, Nsolve_model)
        
        res = obj.run(process_num)

        save_p(path, *res)

        print(case, "out\n")
    
        path = path.parent
 
if __name__ == "__main__":
    
    path = path / "data" / "NPPART1"
        
    run(path, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], PPart1)
    #exit()