
from pathlib import Path
import os
import pandas as pd
from . import tuple_depack
from . import structure_data_save


def save_data(case, index, structures, path, file_number):

    results_file = path / "results" 
    if not os.path.exists(results_file):
        os.makedirs(results_file)
    
    # 保存TAC文件
    d_tac = {"TAC" : []}
    
    for st in structures:
        d_tac["TAC"].append("-1" if st is None else st.TAC)
    
    df = pd.DataFrame(d_tac, index = index)
    
    df.index.name = "Index"
    df.to_csv(results_file / ("results%s.csv"%file_number), mode = "w")                
    
    # 保存结构数据文件
    data_file = path / ("structures_data%s"%file_number)    
    
    structure_data_save(case = case).write_results(structures, data_file)


def save_data_by_each(case, idx, structure, path):
    
    results_file = path / "results" 
    
    if not os.path.exists(results_file):
        os.makedirs(results_file)
    
    results_file /= ("results%s.csv"%((idx - 1)//500 + 1))
    
    # 保存TAC文件
    d_tac = {"TAC" : [structure.TAC]}
    
    df = pd.DataFrame(d_tac, index = [idx], columns=["TAC"])
    df.index.name = "Index"
    
    if not os.path.exists(results_file):
        df.to_csv(results_file, mode = "a+")                
    else:
        df.to_csv(results_file, mode = "a+", header=None)
    
    # 保存结构数据文件
    data_file = path / ("structures_data%s"%((idx - 1)//500 + 1))    
    
    structure_data_save(case = case).write_results([structure], data_file, mode = 'a+')





