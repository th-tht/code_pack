
from .Base_Enum import Enum_Base
from . import mytyping

class Enum_Structures(Enum_Base):
    
    def __init__(self, thin: dict, thout: dict, fh: dict, tcin: dict, tcout: dict, fc: dict, EMAT: int, stage_num = mytyping.inf) -> None:
        
        super(Enum_Structures, self).__init__(thin, thout, fh, tcin, tcout, fc, EMAT, stage_num)
    
    def temperature_judge(self, struct: dict):
            
        if not struct:
            return True
        
        stage_number = max(struct.values())
        splits = [[] for _ in range(stage_number)]
        for match, val in struct.items():
            st = match[0]
            splits[val - 1].append(match)

        tk = [None] * (stage_number + 1)
        if st[0] == 'H':
            tk[0] = self.thin[st]
            flow = self.fh[st]
        else:
            flow = self.fc[st]
            tk[0] = self.tcout[st]
            if ('HU',st) in self.q:
                tk[0] -= self.q['HU',st] / flow
        
        for k_1, k_g in enumerate(splits):
            q_stage = sum(self.q[self.swap(*match)] for match in k_g)
            
            tk[k_1 + 1] = tk[k_1] - q_stage / flow
            for match in k_g:
                if not self.tex_update(match, tk[k_1], tk[k_1 + 1]):
                    return False
          
        return True
    
    def stream_structure_generate(self, stream: mytyping.stream, match_stream: mytyping.Stream_index) -> dict:
    
        '''
        生成等温混合分级超结构
        '''        
        generate_structure = dict()
        
        if not match_stream:
            yield generate_structure
            return
        
        match_length = len(match_stream)
        
        for divide_number in self.divide_match(match_length):
            for divide_stream_enum in self.stream_divide(divide_number, stream, match_stream):
                
                # 分级超结构，分配好流股就相当于固定了结构
                for stage, matches in enumerate(divide_stream_enum, 1):
                    for sst in matches:
                        generate_structure[stream, sst] = stage
                    
                yield generate_structure

