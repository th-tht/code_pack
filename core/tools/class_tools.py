
class Numeric:
    
    def __init__(self, num = 0, var = 0):
            
        self.num = num
        self.var = var
    
    def __repr__(self) -> str:
        
        if self.var > 0:    
            return f"{self.num: .2f} + {self.var}x"
        return f"{self.num:.2f} - {-self.var}x"

    def __add__(self, other):
        
        if type(other) == Numeric:
            
            if self.var + other.var == 0:       # 转为正常数值
                return self.num + other.num
            
            return Numeric(self.num + other.num, self.var + other.var)
        
        return Numeric(self.num + other, self.var)

    def __radd__(self, other):
        
        return self + other

    def __iadd__(self, other):
        
        return self + other
    
    def __neg__(self):
        
        return Numeric(-self.num, -self.var)
    
    def __sub__(self, other):
        
        return self + (-other)
        
    def __rsub__(self, other):
        
        return (-self) + other
    
    def __isub__(self, other):
        
        return self - other
    
    def __mul__(self, other):
        
        return Numeric(self.num * other, self.var * other)
    
    def __rmul__(self, other):
        
        return self * other
    
    def __imul__(self, other):
        
        return self * other
    
    def __truediv__(self, other):
        
        return self * (1/other)
    
    def __itruediv__(self, other):
        return self * (1/other)

    def is_right(self):
        return self.var < 0
    
    def solve(self):
        
        if self.var == 0:
            raise
        elif self.var < 0:
            st = "r"
        else:
            st = "l"
        return - self.num / self.var, st
    
    def value(self, x):
        return round(self.num  + self.var * x, 3)


class Unpack_data:
    
    def __init__(self, *avg):
        
        self.thin: dict; self.tcin: dict; self.thout: dict; self.tcout: dict
        self.fh: dict; self.fc: dict; self.hh: dict; self.hc: dict
        
        if len(avg) == 1:
        
            self.thin, self.thout, self.hh, self.fh, self.tcin, self.tcout, self.hc, self.fc, \
            self.hucost, self.hucoeff, self.thuin, self.thuout, self.hhu, self.cucost, self.cucoeff,self.tcuin, self.tcuout,self.hcu,\
            self.unitc,self.acoeff,self.aexp,self.EMAT,self.HRAT, *other= avg[0]
        
        else:
            self.thin, self.thout, self.hh, self.fh, self.tcin, self.tcout, self.hc, self.fc = avg[0]
            self.hucost, self.hucoeff, self.thuin, self.thuout,self.hhu,self.cucost, self.cucoeff, self.tcuin, self.tcuout,self.hcu,\
            self.unitc,self.acoeff,self.aexp,self.EMAT,self.HRAT, *other = avg[1]

        self.idx_i = list(self.thin)
        self.idx_j = list(self.tcin)
        
        self.all_matches = [(h,c) for h in self.thin for c in self.tcin] \
            + [("HU", c) for c in self.tcin] + [(h,"CU") for h in self.thin]

        if type(self.HRAT) == tuple:
            self.HRAT_MIN, self.HRAT_MAX = self.HRAT
        else:
            self.HRAT_MIN = self.EMAT
            self.HRAT_MAX = self.HRAT
        
        self.Target_TAC = 0
        if len(other) == 2:
            self.Nmin_max, self.Stage_Num = other
        else:
            self.Nmin_max, self.Stage_Num, self.Target_TAC = other
        
        self.Max_Energy = -1
        
        """Gamma = max(
            max(abs(self.thin[h] - self.tcin[c]) for h in self.thin for c in self.tcin),
            max(abs(self.thout[h] - self.tcin[c]) for h in self.thin for c in self.tcin),
            max(abs(self.tcin[c] - self.tcout[c]) for c in self.tcin),
            max(abs(self.thin[h] - self.tcout[c]) for h in self.thin for c in self.tcin)
        )

        self.HU_MAX_T = self.EMAT + Gamma / 1.01"""

if __name__ == "__main__":
    
    num = Numeric(1,2)
    print(num)
    print(num + Numeric(1,6))
    print(num * 5)
    num /= 2
    print(num)
    print(num.value())

      
    
