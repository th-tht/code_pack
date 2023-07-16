import os
import pandas as pd
from pathlib import Path

from . import tuple_depack

def read_match(file_path: Path):
    
    '''从文件夹中读取匹配文件'''    
    # 检查匹配文件是否可读
    assert os.access(file_path, os.R_OK)

    # 逐行读取proto-metwork
    df = pd.read_csv(file_path, index_col = "Index")
    for idx in df.index:
        pns = []
        for col in df.columns:
            if col == "Time":
                break
            if str(df.loc[idx,col]) != "0":
                pns.append(tuple_depack(col))
        yield pns

def read_matches(file_pathes: list):
    
    for file_path in file_pathes:
        
        yield from read_match(file_path)

  
def obtained_results(path):

    def is_out(proto_network_idx):
        
        return proto_network_idx in proto_number
    
    if not os.path.exists(path):
        os.makedirs(path)

    proto_number = set()
    for file in os.listdir(path):
        df = pd.read_csv(path / file, index_col="Index")
        for idx in df.index:
            proto_number.add(int(idx))
            
    return is_out, len(os.listdir(path)) + 1
    


    