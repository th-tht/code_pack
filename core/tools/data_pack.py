

class Structure_Data:
    
    '''保存可行的换热网络的可用数据'''
    __slots__ = ["zh_sp","zc_sp","zcu_sp","zhu_sp","HU","TAC","Area", "th_sp", "tc_sp", "q", "area", "fh_sp", "fc_sp","match","solve_time"]
    def __init__(self, zh_sp, zc_sp, zcu_sp, zhu_sp, HU, TAC, Area, th_sp, tc_sp, q, area, fh_sp, fc_sp, match = None, solve_time = None):
        self.zh_sp, self.zc_sp, self.zcu_sp, self.zhu_sp, self.HU, self.TAC, self.Area, self.th_sp, self.tc_sp, \
            self.q, self.area, self.fh_sp, self.fc_sp = zh_sp, zc_sp, zcu_sp, zhu_sp, HU, TAC, Area, th_sp, tc_sp, q, area, fh_sp, fc_sp
        self.match = match
        self.solve_time = solve_time


def tuple_pack(data: tuple):
    
    '''以字符的方式保存元组方便写入excel '''
    
    return ','.join(['(%s'%data[0]] + [str(i) for i in data[1:-1]] + ['%s)'%data[-1]]) if len(data) >= 2 else '(%s)'%data[0]


def is_digit(num: str) -> bool:
    
    if num.isdigit():
        return True
    num = num.split('.')
    return len(num) == 2 and all(st.isdigit() for st in num)
    
    
def tuple_depack(data: str):

    if type(data) != str:
        return data

    data = data.strip()
    if data[0] == "(" and  data[-1] == ")":

        return tuple([float(st) if is_digit(st) else st for st in data[1:-1].split(',')])
    
    return data



