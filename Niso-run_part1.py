# utf-8
from multiprocessing import Manager, Pool
from pathlib import Path
import sys, os

path = Path(os.path.abspath(__file__)).parent
sys.path.append(str(path))

from core import  mytyping, Part1, Nsolve_model


def save(path, pns_yield_time, opt_time, PNN, EPNN, Enum_structure_number, run_model_number):
    
    with open(path / "time_file.txt", "w+") as f:
        
        f.write(f"Time for proto-network generation : {pns_yield_time: .2f} s\n")
        f.write(f"Time for Network building and Evaluation: {opt_time: .2f} s\n")
        f.write(f"The TOTAL TIME: {pns_yield_time + opt_time : .2f} s\n")
        f.write(f"The proto-network number: {PNN}\n")
        f.write(f"The evaluate proto-network number: {PNN}\n")
        f.write(f"TOTAL Enum structure number: {Enum_structure_number}\n")
        f.write(f"Run transshipment model number: {run_model_number}\n")
    

# 并行分布进程，对多个匹配文件进行计算
def run(path: Path, cases: list, Run):
    
    #sys.argv.append("example9")
    if not os.path.exists(path):
        os.mkdir(path)
    
    for i in cases:

        case = "example%s"%i

        path = path / case
        
        if not os.path.exists(path):
            os.mkdir(path)
        
        obj = Run(path, case, Nsolve_model)
        
        res = obj.run()

        save(path, *res)

        print(case, "out\n")
    
        path = path.parent


 
if __name__ == "__main__":
    
    path = path / "data" / "NPART1"
        
    run(path, [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15], Part1)
    #exit()