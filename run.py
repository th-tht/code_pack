
from run.run_part1 import *
    

def iso():
    
    save_path = path / "data" / "PART1"
    case = list(range(3,4))
    run(save_path, [*case], Part1, solve_model)
    
def niso():
    save_path = path / "data" / "NPART1"
    case = list(range(3,4))
    run(save_path, [*case], Part1, Nsolve_model)
      

 
if __name__ == "__main__":
    
    
    # run iso part
    iso()
    
    # run non-iso party
    niso()
    
    
    