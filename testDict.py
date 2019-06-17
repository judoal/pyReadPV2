

def invErrMode(bitPos):
    bitNum= {
        1 : "Low VAC Out",
        2 : "Stacking Err",
        3 : "Over Temp",
        4 : "Low Battery",
        5 : "Phase Loss",
        6 : "High Battery",
        7 : "Shorted Output",
        8 : "Backfeed"
    }
    return bitNum[bitPos]
    

#print (invErrMode(3))    
def getErrString(code):
    a=""        
    b=bin(code)[2:].zfill(8)
    a=str(b[::-1]) 
    print (a)
    errStr = ""
    bit0=0
    bit8=8
    for pos in range (bit0,bit8):
        ipos = int(pos)
        print (str(pos) + " " + str(a[ipos]))
        if str([ipos])  == str(1):
            errStr += invErrMode(ipos+1) + ", "
            print (errStr)
         
getErrString(132)        
        



