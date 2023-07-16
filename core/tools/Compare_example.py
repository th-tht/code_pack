
class example:

    def __init__(self):
        pass
    
    def data(self,ex):   
        if type(ex) == int:
            ex = f"example{ex}"
        try:
            return eval("self.%s()"%ex)
        except:
            print("Haven't this example")
    
    def example1(self):
        
        # Hot
        thin  = {"H1": 650, "H2": 590}
        thout = {"H1": 370, "H2": 370}
        hh    = {"H1": 1.0, "H2": 1.0}
        fh    = {"H1":  10, "H2":  20} 

        # Cold
        tcin  = {"C1": 410, "C2": 350}
        tcout = {"C1": 650, "C2": 500}
        hc    = {"C1": 1.0, "C2": 1.0}
        fc    = {"C1":  15, "C2":  13}

        # Costs and coefficients
        hucost = 80; hucoeff = 150; thuin = 680; thuout = 680; hhu = 5.0
        cucost = 15; cucoeff = 150; tcuin = 300; tcuout = 320; hcu = 1.0

        unitc = 5500; acoeff = 150
        aexp  = 1;    EMAT = 10
        HRAT = 108
        
        Nmin_max, Stage_Num = 5, 2
        
        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT, Nmin_max, Stage_Num

    def example2(self):

        # Hot
        thin  = {"H1": 270, "H2": 220}
        thout = {"H1": 160, "H2": 60}
        hh    = {"H1": 0.5, "H2": 0.5}
        fh    = {"H1": 18 , "H2": 22} 

        # Cold
        tcin  = {"C1": 50,  "C2": 160}
        tcout = {"C1": 210, "C2": 210}
        hc    = {"C1": 0.5, "C2": 0.5}
        fc    = {"C1": 20,  "C2": 50}

        # Costs and coefficients
        hucost = 200; hucoeff = 500; thuin = 250; thuout = 250; hhu = 1.0
        cucost = 20; cucoeff = 500; tcuin = 15; tcuout = 20; hcu = 1.0

        unitc = 4000; acoeff = 500
        aexp  = 0.83;    EMAT = 10
        HRAT = 250

        Nmin_max, Stage_Num = 5, 2

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num
    
    def example3(self):

        # Hot
        thin  = {"H1": 150, "H2": 90}
        thout = {"H1": 60,  "H2": 60}
        hh    = {"H1": 0.1, "H2": 0.1}
        fh    = {"H1": 20,  "H2": 80} 

        # Cold
        tcin  = {"C1": 20,  "C2": 25}
        tcout = {"C1": 125, "C2": 100}
        hc    = {"C1": 0.1, "C2": 0.1}
        fc    = {"C1": 25,  "C2": 30}

        # Costs and coefficients
        hucost = 0; hucoeff = 670; thuin = 180; thuout = 180; hhu = 0.1
        cucost = 0; cucoeff = 670; tcuin = 10; tcuout = 15; hcu = 0.1

        unitc = 8600; acoeff = 670
        aexp  = 0.83;    EMAT = 8
        HRAT = (20,20)

        Nmin_max, Stage_Num = 5, 2

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example4(self):
        # Parameters
        # Hot
        thin  = {"H1": 432.15, "H2": 540.15, "H3":  616.15}
        thout = {"H1": 350.15, "H2": 353.15, "H3":  363.15}
        hh    = {"H1":   0.10, "H2":   0.04, "H3":  0.50}
        fh    = {"H1":  2.285, "H2":  0.204, "H3":  0.538} 

        # Cold
        tcin  = {"C1": 299.15, "C2": 391.15}
        tcout = {"C1": 400.15, "C2": 538.15}
        hc    = {"C1":  0.01,  "C2": 0.50}
        fc    = {"C1": 0.933,  "C2": 1.961}

        # Costs and coefficients
        hucost = 110; hucoeff = 80; thuin = 573.15; thuout = 573.15; hhu = 0.05
        cucost =  10; cucoeff = 80; tcuin =  293.15; tcuout = 333.15; hcu = 0.20

        unitc = 7400; acoeff = 80
        aexp  = 1;    EMAT = 10
        HRAT = 100

        Nmin_max, Stage_Num = 6, 2

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example5(self):

        # Parameters
        # Hot
        thin  = {"H1":   159, "H2":  267, "H3":   343}
        thout = {"H1":    77, "H2":   88, "H3":    90}
        hh    = {"H1":  0.40, "H2":  0.3, "H3":  0.25}
        fh    = {"H1": 228.5, "H2": 20.4, "H3":  53.8} 

        # Cold
        tcin  = {"C1":    26, "C2":   118}
        tcout = {"C1":   127, "C2":   265}
        hc    = {"C1":  0.15, "C2":  0.50}
        fc    = {"C1":  93.3, "C2": 196.1}

        # Costs and coefficients
        hucost = 100; hucoeff = 55; thuin = 500; thuout = 499; hhu = 0.53
        cucost =  10; cucoeff = 55; tcuin =  20; tcuout =  40; hcu = 0.53

        unitc = 25000; acoeff = 55
        aexp  = 1;    EMAT = 10
        HRAT = 350

        Nmin_max, Stage_Num = 6, 2

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example6(self):

        # Parameters
        # Hot
        thin  = {"H1": 500, "H2": 480, "H3": 460, 'H4': 380, 'H5': 380}
        thout = {"H1": 320, "H2": 380, "H3": 360, 'H4': 360, 'H5': 320}
        hh    = {"H1": 2,   "H2": 2,   "H3": 2,   'H4': 2,   'H5': 2}
        fh    = {"H1": 6,   "H2": 4,   "H3": 6,   'H4': 20,  'H5': 12}

        # Cold
        tcin  = {"C1": 290}
        tcout = {"C1": 660}
        hc    = {"C1": 2}
        fc    = {"C1": 18}

        # Costs and coefficients
        hucost = 140; hucoeff = 1200; thuin = 700; thuout = 700; hhu = 2.0
        cucost =  10; cucoeff = 1200; tcuin = 300; tcuout = 320; hcu = 1.0

        unitc = 5500; acoeff = 1200
        aexp  = 0.6;    EMAT = 10
        HRAT = 250

        Nmin_max, Stage_Num = 7, 2

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example7(self):

        # Parameters
        # Hot
        thin  = {"H1": 626,   "H2": 620,   "H3": 528 }
        thout = {"H1": 586,   "H2": 519,   "H3": 353 }
        hh    = {"H1": 1.25,  "H2": 0.05,  "H3": 3.2 }
        fh    = {"H1": 9.802, "H2": 2.931, "H3": 6.161}

        # Cold
        tcin  = {"C1": 497,   "C2": 389,   "C3": 326,  "C4": 313}
        tcout = {"C1": 613,   "C2": 576,   "C3": 386,  "C4": 566}
        hc    = {"C1": 0.65,  "C2": 0.25,  "C3": 0.33, "C4": 3.2}
        fc    = {"C1": 7.179, "C2": 0.641, "C3": 7.672, "C4": 1.69}

        # Costs and coefficients
        hucost = 130; hucoeff = 670; thuin = 650; thuout = 650; hhu = 3.5
        cucost =  20; cucoeff = 670; tcuin = 293; tcuout = 308; hcu = 3.5

        unitc = 8600; acoeff = 670
        aexp  = 0.83;    EMAT = 10
        HRAT = 250

        Nmin_max, Stage_Num = 8, 3

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example8(self):

        # Parameters
        # Hot
        thin  = {"H1": 433.15,  "H2": 522.05,   "H3": 499.85,  "H4": 544.25, "H5": 472.05}
        thout = {"H1": 366.45,  "H2": 410.95,   "H3": 338.75,  "H4": 422.05, "H5": 338.75}
        hh    = {"H1": 1.7,     "H2": 1.7,      "H3": 1.7,     "H4": 1.7,    "H5": 1.7}
        fh    = {"H1": 8.8,     "H2": 10.6,     "H3": 14.8,    "H4": 12.6,   "H5": 17.7}

        # Cold
        tcin  = {"C1": 333.15, "C2": 388.75, "C3": 310.95, "C4": 355.35, "C5": 366.45}
        tcout = {"C1": 433.15, "C2": 494.85, "C3": 494.25, "C4": 449.85, "C5": 477.55}
        hc    = {"C1": 1.7,    "C2": 1.7,    "C3": 1.7,    "C4": 1.7,    "C5": 1.7}
        fc    = {"C1": 7.6,    "C2": 6.1,    "C3": 8.4,    "C4": 17.3,   "C5": 13.9}

        # Costs and coefficients
        hucost = 200; hucoeff = 146; thuin = 513.15; thuout = 513.15; hhu = 3.4
        cucost =  10; cucoeff = 146; tcuin = 298.15; tcuout = 313.15; hcu = 1.7

        unitc = 4000; acoeff = 146
        aexp  = 0.6;    EMAT = 10
        HRAT = 30

        Nmin_max, Stage_Num = 9, 3

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example9(self):

        # Parameters
        # Hot
        thin  = {'H1': 500,  'H2': 460, 'H3': 440, 'H4': 350, 'H5': 350}
        thout = {'H1': 340,  'H2': 400, 'H3': 400, 'H4': 310, 'H5': 320}
        hh    = {'H1': 1.6,  'H2': 1.6, 'H3': 1.6, 'H4': 1.6, 'H5': 1.6}
        fh    = {'H1': 15.0, 'H2': 3.0, 'H3': 8.0, 'H4': 9.0, 'H5': 5.0}

        #cool
        tcin  = {'C1': 300, 'C2': 340,  'C3': 340, 'C4': 380, 'C5': 460}
        tcout = {'C1': 340, 'C2': 360,  'C3': 400, 'C4': 460, 'C5': 560}
        hc    = {'C1': 1.6, 'C2': 1.6,  'C3': 1.6, 'C4': 1.6, 'C5': 1.6}
        fc    = {'C1': 8.0, 'C2': 15.0, 'C3': 8.0, 'C4': 4.0, 'C5': 6.0}

        # Costs and coefficients
        hucost = 125; hucoeff = 300; thuin = 580; thuout = 580; hhu = 1.6
        cucost = 10;  cucoeff = 300; tcuin = 300; tcuout = 320; hcu = 1.6

        unitc = 900; acoeff = 300
        aexp = 1;    EMAT = 1
        HRAT = 30

        Nmin_max, Stage_Num = 10, 4

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example10(self):

        # Parameters
        # Hot
        thin  = {"H1": 160,   "H2": 249,   "H3": 271,   "H4": 227,   "H5": 199}
        thout = {"H1": 93,    "H2": 138,   "H3": 149,   "H4": 66,    "H5": 66}
        hh    = {"H1": 1.704, "H2": 1.704, "H3": 1.704, "H4": 1.704, "H5": 1.704}
        fh    = {"H1": 8.79,  "H2": 10.55, "H3": 12.56, "H4": 14.77, "H5": 17.73}

        # Cold
        tcin  = {"C1": 82,    "C2": 93,    "C3": 38,    "C4": 60,    "C5": 116}
        tcout = {"C1": 177,   "C2": 205,   "C3": 221,   "C4": 160,   "C5": 222}
        hc    = {"C1": 1.704, "C2": 1.704, "C3": 1.704, "C4": 1.704, "C5": 1.704}
        fc    = {"C1": 17.28, "C2": 13.9,  "C3": 8.44,  "C4": 7.62,  "C5": 6.08}

        # Costs and coefficients
        hucost = 37.64; hucoeff = 145.63; thuin = 236; thuout = 236; hhu = 3.404
        cucost = 18.12; cucoeff = 145.63; tcuin = 38;  tcuout = 82;  hcu = 1.704

        unitc = 0; acoeff = 145.63
        aexp  = 0.6;    EMAT = 10
        HRAT = 30

        Nmin_max, Stage_Num = 10, 3

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example11(self):

        # Parameters
        # Hot
        thin  = {"H1": 140.2, "H2": 248.8, "H3": 170.1, "H4": 277.0, "H5": 250.6, "H6": 210.0,  "H7": 303.6,  "H8": 360.0, "H9": 178.6, "H10": 359.6, "H11": 290.0}
        thout = {"H1": 39.5,  "H2": 110.0, "H3": 60.0,  "H4": 121.9, "H5": 90.0,  "H6": 163.0,  "H7": 270.2,  "H8": 290.0, "H9": 108.9, "H10": 280.0, "H11": 115.0}
        hh    = {"H1": 0.26,  "H2": 0.72,  "H3": 0.45,  "H4": 0.57,  "H5": 0.26,  "H6": 0.33,   "H7": 0.41,   "H8": 0.47,  "H9": 0.6,   "H10": 0.47,  "H11": 0.47}
        fh    = {"H1": 106.5, "H2": 31.81, "H3": 33.93, "H4": 24.58, "H5": 132.2, "H6": 115.76, "H7": 234.98, "H8": 39.81, "H9": 47.85, "H10": 24.53, "H11": 39.81} 

        # Cold
        tcin  = {"C1": 30.0,   "C2": 130.0}
        tcout = {"C1": 130.0,  "C2": 350.0}
        hc    = {"C1": 0.26,   "C2": 0.72}
        fc    = {"C1": 202.48, "C2": 289.92}

        # Costs and coefficients
        hucost = 100; hucoeff = 55; thuin = 500; thuout = 499; hhu = 0.53
        cucost =  10; cucoeff = 55; tcuin =  20; tcuout =  40; hcu = 0.53

        unitc = 25000; acoeff = 55
        aexp  = 1;    EMAT = 10
        HRAT = 50

        Nmin_max, Stage_Num = 14, 3

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example12(self):
        
        # https://doi.org/10.1002/aic.15524
        # Parameters
        # Hot
        thin  = {"H1": 840,    "H2": 76,    "H3": 50,    'H4': 180,    'H5': 180,   'H6': 90}
        thout = {"H1": 40,     "H2": 45,    "H3": 40,    'H4':  77,    'H5': 179,   'H6': 45}
        hh    = {"H1": 1.5,    "H2": 1.5,   "H3": 1.5,   'H4':  1.5,   'H5': 0.8,   'H6': 1.5}
        fh    = {"H1": 4.9894, "H2": 4.684, "H3": 0.772, 'H4': 0.6097, 'H5': 292.7, 'H6': 3.066}

        # Cold
        tcin  = {"C1": 24,    "C2": 25,     "C3": 35,    "C4": 90,     "C5": 180}
        tcout = {"C1": 25,    "C2": 70,     "C3": 122,   "C4": 180,    "C5": 181}
        hc    = {"C1": 0.8,   "C2": 1.5,    "C3": 1.5,   "C4": 1.5,    "C5": 0.8}
        fc    = {"C1": 329.8, "C2": 0.5383, "C3": 3.727, "C4": 0.6097, "C5": 2581.1}

        # Costs and coefficients
        hucost = 110; hucoeff = 485; thuin = 230; thuout = 230; hhu = 1.5
        cucost =  15; cucoeff = 485; tcuin = 20;  tcuout = 40;  hcu = 0.8

        unitc = 9094; acoeff = 485
        aexp  = 0.81;    EMAT = 10
        HRAT = 30

        Nmin_max, Stage_Num = 11, 2

        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num

    def example13(self):

        # Parameters
        # Hot
        thin  = {"H1": 385.0,  "H2": 516.0,   "H3": 132.0,   "H4": 91.0,    "H5": 217.0,   "H6": 649.0}
        thout = {"H1": 159.0,  "H2": 43.0,    "H3": 82.0,    "H4": 60.0,    "H5": 43.0,    "H6": 43.0 }
        hh    = {"H1": 1.238,  "H2": 0.546,   "H3": 0.771,   "H4": 0.859,   "H5": 1.0,     "H6": 1.0}   
        fh    = {"H1": 131.51, "H2": 1198.96, "H3": 378.52,  "H4": 589.545, "H5": 186.216, "H6": 116.0}

        # Cold
        tcin  = {"C1": 30.0,  "C2": 99.0,   "C3": 437.0,  "C4": 78.0,   "C5": 217.0,  "C6": 256.0,  "C7": 49.0,   "C8": 59.0,    "C9": 163.0,  "C10": 219.0}
        tcout = {"C1": 385.0, "C2": 471.0,  "C3": 521.0,  "C4": 418.6,  "C5": 234.0,  "C6": 266.0,  "C7": 149.0,  "C8": 163.4,   "C9": 649.0,  "C10": 221.3}
        hc    = {"C1": 1.85,  "C2": 1.129,  "C3": 0.815,  "C4": 1.0,    "C5": 0.443,  "C6": 2.085,  "C7": 1.0,    "C8": 1.063,   "C9": 1.81,   "C10": 1.377}
        fc    = {"C1": 119.1, "C2": 191.05, "C3": 377.91, "C4": 160.43, "C5": 1297.7, "C6": 2753.0, "C7": 197.39, "C8": 123.156, "C9": 95.98,  "C10": 1997.5}

        # Costs and coefficients
        hucost =  35;  hucoeff = 4147.5; thuin = 1800; thuout = 800;  hhu = 1.2
        cucost =  2.1; cucoeff = 4147.5; tcuin =   38; tcuout =  82;  hcu = 1.0

        unitc = 26600;   acoeff = 4147.5
        aexp  = 0.6;    EMAT = 5
        HRAT = 50

        Nmin_max, Stage_Num = 17, 2
        
        TTAC = 7030035.0
        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max,Stage_Num, TTAC
     
    def example14(self):

        #  https://pubs.acs.org/doi/abs/10.1021/acs.iecr.5b01592
        # Parameters
        # Hot
        thin  = {"H1": 180, "H2": 280, "H3": 180, "H4": 140, "H5": 220, "H6": 180, "H7": 200, "H8": 120}
        thout = {"H1": 75,  "H2": 120, "H3": 75,  "H4": 40,  "H5": 120, "H6": 55,  "H7": 60,  "H8": 40}
        hh    = {"H1": 2,   "H2": 1,   "H3": 2,   "H4": 1,   "H5": 1,   "H6": 2,   "H7": 0.4, "H8": 0.5}   
        fh    = {"H1": 30,  "H2": 60,  "H3": 30,  "H4": 30,  "H5": 50,  "H6": 35,  "H7": 30,  "H8": 100}

        # Cold
        tcin  = {"C1": 40,  "C2": 100, "C3": 40,  "C4": 50,  "C5": 50,  "C6": 90,  "C7": 160}
        tcout = {"C1": 230, "C2": 220, "C3": 190, "C4": 190, "C5": 250, "C6": 190, "C7": 250}
        hc    = {"C1": 1,   "C2": 1,   "C3": 2,   "C4": 2,   "C5": 2,   "C6": 1,   "C7": 3}
        fc    = {"C1": 20,  "C2": 60,  "C3": 35,  "C4": 30,  "C5": 60,  "C6": 50,  "C7": 60}

        # Costs and coefficients
        hucost =  80; hucoeff = 500; thuin = 325; thuout = 325;  hhu = 1
        cucost =  10; cucoeff = 500; tcuin =  25; tcuout =  40;  hcu = 2

        unitc = 8000;   acoeff = 500
        aexp  = 0.75;    EMAT = 2.5
        HRAT = (10, 30)

        Nmin_max, Stage_Num = 15, 3
        
        TTAC = 1500000.1
        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max,Stage_Num,TTAC

    def example15(self):
        
        # Hot
        thin  = {"H1": 576,  "H2": 599,   "H3": 530,   "H4": 449,   "H5": 368,  "H6": 121,   "H7": 202,   "H8": 185,  "H9": 140,   "H10": 69,     "H11": 120,  "H12": 67,   "H13": 1034.5}
        thout = {"H1": 437,  "H2": 399,   "H3": 382,   "H4": 237,   "H5": 177,  "H6": 114,   "H7": 185,   "H8": 113,  "H9": 120,   "H10": 66,     "H11": 68,   "H12": 35,   "H13": 576}
        hh    = {"H1": 0.06, "H2": 0.6,   "H3": 0.06,  "H4": 0.06,  "H5": 0.06, "H6": 1.0,   "H7": 1.0,   "H8": 1.0,  "H9": 1.0,   "H10": 1.0,    "H11": 1.0,  "H12": 1.0,  "H13": 0.06}  
        fh    = {"H1": 23.1, "H2": 15.22, "H3": 15.15, "H4": 14.76, "H5": 10.7, "H6": 149.6, "H7": 258.2, "H8": 8.38, "H9": 59.89, "H10": 165.79, "H11": 8.74, "H12": 7.62, "H13": 21.3}

        # Cold
        tcin  = {"C1": 123,   "C2": 20,   "C3": 156,  "C4": 20,    "C5": 182,   "C6": 318,     "C7": 322}
        tcout = {"C1": 343,   "C2": 156,  "C3": 157,  "C4": 182,   "C5": 318,   "C6": 320,     "C7": 923.78}
        hc    = {"C1": 0.06,  "C2": 1.2,  "C3": 2.0,  "C4": 1.2,   "C5": 1.2,   "C6": 2.0,     "C7": 0.06}
        fc    = {"C1": 10.61, "C2": 6.65, "C3": 3291, "C4": 26.63, "C5": 31.19, "C6": 4011.83, "C7": 17.6}

        # Costs and coefficients
        hucost = 250;  hucoeff = 500; thuin = 927; thuout = 927;  hhu = 5.0
        cucost =  25;  cucoeff = 500; tcuin = 9.0; tcuout = 17;   hcu = 1.0
        
        unitc = 4000;   acoeff = 500
        aexp  = 0.83;    EMAT = 8
        HRAT = (10, 30)

        Nmin_max, Stage_Num = 20, 7
        
        TTAC = 1427966.0
        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max, Stage_Num, TTAC

    def example16(self):
        
        # Hot
        thin  = {"H1": 180, "H2": 280,  "H3": 180,  "H4": 140,  "H5": 220,  "H6": 180,  "H7": 170,  "H8": 180,  "H9": 280,  "H10": 180,
                "H11": 120, "H12": 220, "H13": 180, "H14": 140, "H15": 140, "H16": 220, "H17": 220, "H18": 150, "H19": 140, "H20": 220, 
                "H21": 180, "H22": 150}
         
        thout = {"H1": 75,  "H2": 120,  "H3": 75,   "H4": 45,   "H5": 120,  "H6": 55,   "H7": 45,   "H8": 50,   "H9": 90,   "H10": 60, 
                "H11": 45,  "H12": 120, "H13": 55,  "H14": 45,  "H15": 60,  "H16": 50,  "H17": 60,  "H18": 70,  "H19": 80,  "H20": 50,
                "H21": 60,  "H22": 45}
        
        hh    = {"H1": 2.0, "H2": 2.5,  "H3": 2.0,  "H4": 2.0,  "H5": 1.5,  "H6": 2.0,  "H7": 2.0,  "H8": 2.0,  "H9": 2.0,  "H10": 2.0,
                "H11": 2.0, "H12": 2.0, "H13": 2.0, "H14":2.0,  "H15": 2.0, "H16": 2.5, "H17": 2.5, "H18": 2.0,  "H19": 2.0, "H20": 2.0,
                "H21": 2.0, "H22": 2.5}   
        
        fh    = {"H1": 30,  "H2": 15,   "H3": 30,   "H4": 30,   "H5": 25,   "H6": 10,   "H7": 30,   "H8": 30,   "H9": 15,    "H10": 30,
                "H11": 30,  "H12": 25,  "H13": 10,  "H14": 20,  "H15": 70,  "H16": 15,  "H17": 10,  "H18": 20,  "H19": 70,   "H20": 35,
                "H21": 10,  "H22": 20}

        # Cold
        tcin  = {"C1": 40, "C2": 120,  "C3": 40,   "C4": 50,    "C5": 50,   "C6": 40,    "C7": 40,  "C8": 120,  "C9": 40,  "C10": 60,
                "C11": 50,  "C12": 40,  "C13": 120, "C14": 40,   "C15": 50,  "C16": 50,   "C17": 30}
        
        tcout = {"C1": 230, "C2": 260,  "C3": 190,  "C4": 190,   "C5": 250,  "C6": 150,   "C7": 150, "C8": 210,  "C9": 130, "C10": 120,
                "C11": 150, "C12": 130, "C13": 160, "C14": 90,   "C15": 90,  "C16": 150,  "C17": 150}
        
        hc    = {"C1": 1.5, "C2": 1.0,  "C3": 1.5,  "C4": 2.0,   "C5": 2.0,  "C6": 2.0,   "C7": 2.0, "C8": 2.5,  "C9": 2.5, "C10": 2.5,
                "C11": 3.0, "C12": 1.0, "C13": 1.0, "C14": 1.75, "C15": 1.5, "C16": 2.0,  "C17": 2.0}
        
        fc    = {"C1": 20,  "C2": 35,   "C3": 35,   "C4": 30,    "C5": 60,   "C6": 20,    "C7": 20,  "C8": 35,   "C9": 35,  "C10": 30,
                "C11": 10, "C12": 20,   "C13": 35,  "C14": 35,   "C15": 30,  "C16": 30,   "C17": 50}

        # Costs and coefficients
        hucost = 70;  hucoeff = 800; thuin = 325; thuout = 325;  hhu = 1.0
        cucost = 10;  cucoeff = 800; tcuin =  25; tcuout = 40;   hcu = 2.0
        
        unitc = 8000;   acoeff = 800
        aexp  = 0.8;    EMAT = 1
        HRAT = (10, 30)

        Nmin_max, Stage_Num = 38, 4

        TTAC = 1958836.0
        return thin,thout,hh,fh,tcin,tcout,hc,fc,hucost,hucoeff,thuin,thuout,hhu,cucost,cucoeff,tcuin,tcuout,hcu,unitc,acoeff,aexp,EMAT,HRAT,Nmin_max,Stage_Num,TTAC  

