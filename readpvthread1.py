import socket
import time
import stripchart as sc
import logging
import threading



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

def invWarnMode(bitPos):
    bitNum={
        1 : "AC Input Freq High",
        2 : "AC Input Freq Low",
        3 : "Input VAC High",
        4 : "Input VAC Low",
        5 : "Buy Amps > Input size",
        6 : "Temp Sensor Failed",
        7 : "Comm Error",
        8 : "Fan Failure"        
    }
    return bitNum[bitPos]

def invMiscMode(bitPos):
    bitNum={
        1 : "230V unit",
        2 : "Reserved",
        3 : "Reserved",
        4 : "Reserved",
        5 : "Reserved",
        6 : "Reserved",
        7 : "Reserved",
        8 :  "Aux Output On"
    }
    return bitNum[bitPos]


def getErrString(code, type):
    errStr=""
    b=bin(code)[2:].zfill(8)
    a=""        
    #invert binary string to correspond to specs
    a=str(b[::-1]) 
    errStr = ""
    bit0=0
    bit8=8
    for pos in range (bit0,bit8):
        ipos = int(pos)
        if str(a[ipos])  == str(1):
            if type==1:
                errStr += invErrMode(ipos+1) + ", "
            if type == 2:
               errStr += invWarnMode(ipos+1) + ", "
            if type == 3:
                errStr += invMiscMode(ipos+1) + ", "
    return errStr
 
def sum_digits(str1):
#    return sum(int(x) for x in str1 if x.isdigit())
    a=0
    for x in str1:
        if str(x).isdigit():
            a += int(x) 
    return a
                
def decode_inverter_data(inverterList,invDataDict, listOfInvData):
        for item in inverterList:
            invDataDict[inverterList[0]] = {  
                "ID" : inverterList[0],
                "Inverter Current" : inverterList[1],
                "Chgrger Current" : inverterList[2],
                "Buy Current" : inverterList[3],
                "ACIn Volt" : inverterList[4],
                "ACOut Volt" : inverterList[5],
                "Sell Current" : inverterList[6],
                "Op Mode" :   inverterList[7],
                "Error Mode" : inverterList [8],
                "AC Mode"  : inverterList [9],
                "Battery Volt" : float(inverterList[10])/10.0,
                "Misc" : inverterList[11],
                "Warn Mode" : inverterList[12]
            }   
        
        if invDataDict[inverterList[0]]["Misc"] == str(1):
            invDataDict["ACIn Volt"] *= 2
            invDataDict["ACOut Volt"] *= 2
            
        code=invDataDict[inverterList[0]]["Op Mode"]
        invDataDict[inverterList[0]]["Op Mode"]=inverterOpMode(code)
        
        code = invDataDict[inverterList[0]]["AC Mode"]
        invDataDict[inverterList[0]]["AC Mode"]=inverterACMode(code)
        
        errCode = invDataDict[inverterList[0]]["Error Mode"]
        if errCode == "000":
            err="OK"
        else:
            err = getErrString(int(errCode),1) 
        invDataDict[inverterList[0]]["Error Mode"]=err
        
        warnCode = invDataDict[inverterList[0]]["Warn Mode"]
        if warnCode == "000":
            err="OK"
        else:
            err = getErrString(int(warnCode),2)
        invDataDict[inverterList[0]]["Warn Mode"]=err
        
        miscCode = invDataDict[inverterList[0]]["Misc"]
        if miscCode == "000":
            err="OK"
        else:
            err = getErrString(int(warnCode),3)
        invDataDict[inverterList[0]]["Misc"]=err
        #        print (invDataDict[inverterList[0]])                
        listOfInvData.append(invDataDict[inverterList[0]])        
        return invDataDict[inverterList[0]]

        
def decode_chgcontroller(chgContList, chgContDict, listOfChgContData):
    for item in chgContList:
        chgContDict[chgContList[0]] = {
            "ID" : chgContList[0], 
            "charger Current" : chgContList[2],
            "PV Current" : chgContList[3],
            "PV Voltage" : chgContList[4],
            "Power (KWH)" : float(chgContList[5])/float(10.0),
            "Aux Mode" : chgContList[7],
            "Error" : chgContList[8],
            "Charger Mode" : chgContList[9],
            "Battery Volt" : float(chgContList[10])/10.0
        }
        listOfChgContData.append(chgContDict[chgContList[0]])
        
        auxModeCode = chgContDict[chgContList[0]]["Aux Mode"]
        err = chgContAuxMode(auxModeCode)
        chgContDict[chgContList[0]]["Aux Mode"]=err
        
        chgContDict[chgContList[0]]["Error"] = "NA"
        
        chgModeCode = chgContDict[chgContList[0]]["Charger Mode"]
        err= chgContChargeMode(chgModeCode)
        chgContDict[chgContList[0]]["Charger Mode"] = err

        return chgContDict[chgContList[0]]
                
def inverterOpMode(opModeCode):
    opCode= {
        "00" : "Inv Off",
        "01" : "Search",
        "02" : "Inv On",
        "03" : "Charge",
        "04" : "Silent",
        "05" : "Float",
        "06" : "EQ",
        "07" : "Charger Off",
        "08" : "Support",
        "09" : "Sell Enabled",
        "10" : "Pass Thru",
        "90" : "FX Error",
        "91" : "AGS Error",
        "92" : "Comm Error"
    }
    return opCode.get(opModeCode)

def inverterACMode(ACModeCode):
    opCode = {
        "00" : "No AC",
        "01" : "AC Drop",
        "02" :  "AC Use"
        }
    return opCode.get(ACModeCode)

def chgContAuxMode(auxModeCode):
    opCode = {
        "00" : "Disabled",
        "01" : "Diversion",
        "02" : "Remote",
        "03" : "Manual",
        "04" : "Vent Fan",
        "05" : "PV Trigger"
    }
    return opCode.get(auxModeCode)

def chgContChargeMode(chgModeCode):
    opCode = {
        "00" : "Silent",
        "01" : "Float",
        "02" : "Bulk",
        "03" : "Absorb",
        "03" : "EQ"
    }    
    return opCode.get(chgModeCode)
#*********************************************************   
    
class Reader:
        
    def runReader(dummy):  
        iSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #server_address = ('127.0.0.1', 5557)
        server_address = ('192.168.1.112', 8899)
        iSock.connect(server_address)
    #    f=open ("readpv.out","w+", buffering=512)
        
        lineLen=[]
        date="%m%d%Y"
        tod="%H%M%S"
        data=[]
        tmp=[]
        invDataDict={}
        listOfInvData=[]
        
        chgContDict={}
        listOfChgContData=[]
        inverterList = []
        
        
        totSellCurr=int(0)
        totBuyCurr=int(0)
        totInvCurr=int(0)
        
        ACOutVolt = int(0)
        ACInVolt = int(0)
        invBattVolt = int(0)
        chgContBattVolt = int(0)
        numInverters = float(0.0)
        numChgCont = float(0.0)
        PVKWH = float(0)
        pvWatts = int(0)
        ctr=0 
        i=-1
        y=[0]*20
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 8001))
        s.listen()
        conn, addr = s.accept()
        try:
            while 1:
                data = iSock.recv(512)
                data = data.decode('ISO-8859-1')
        #        print (data)
                lines=data.splitlines()
        #        print(lines)
                numItems=len(lines)
        #        print (numItems)
        #        for items in lines:  
                datalist=([[x] for x in lines])
                timedate=time.strftime(date)
                timetod=time.strftime(tod)
                timestamp=timedate + timetod
                ACOutVolt = 0
                ACInVolt = 0
                InvBattVolt = 0
                for n in range(1,numItems):           
                    tmp=datalist[n]
                    devlist=str(tmp[0]).split(",")
                    
                    #count number of measurements in each device in CSV delimited string
                    #chksum is the last item
                    numStrItem=str(tmp[0]).count(",")
            
                    #chksum is bum of numeric values  of each digit in string
                    #alpha is numerically encoded by ascii value - '0'               
                    chksum=devlist[numStrItem]
                    csdigit=sum_digits(chksum)
                    digits_sum=sum_digits(tmp[0])  
                    chksum_calc=digits_sum - int(csdigit)
                    #inverters have numeric code in 0th position
                    #numeric code used to calc chksum
                    
                    if devlist[0].isdigit():
                        numInverters += int(1)
        #                listOfInvData=[]
                        if (int(chksum_calc) == int(chksum)):
                            inv_data=decode_inverter_data(devlist,invDataDict,listOfInvData)
        #                    print(inv_data)     
                            totSellCurr += int(inv_data["Sell Current"])
                            totBuyCurr += int(inv_data['Buy Current'])
                            totInvCurr += int(inv_data['Inverter Current'])
                            ACOutVolt += int(inv_data['ACOut Volt'])
                            ACInVolt += int(inv_data['ACIn Volt'])
                            invBattVolt += float(inv_data['Battery Volt'])
                            
                                 
                    #charge controllers have upper case alpha in 0th position
                    #get relative position as index to calc chksum       
                    if devlist[0].isalpha():    # deviceID not numeric
                        numChgCont += int(1)
                        code = ord(devlist[0]) - ord("0") 
                        if (int(code + chksum_calc) == int (chksum)):
                            chgCont_data = decode_chgcontroller(devlist,chgContDict, listOfChgContData)
         #                   print (chgCont_data)
                            chgContBattVolt += float(chgCont_data['Battery Volt'])
                            PVKWH += float(chgCont_data['Power (KWH)'])
                            pvWatts += (int(chgCont_data['PV Voltage']) * int(chgCont_data['PV Current']))
                                        
        #        print ("Timestamp (mmddyyyyhhmmss): %s" % timestamp)        
        #        print("Sell Current: %3d" % totSellCurr)
        #        print("Buy Current: %3d" % totBuyCurr)
        #        print("Inverter Current: %3d" % totInvCurr)
        #        totPower = totSellCurr * int(123)
        #        print("sell WATTS: %4d" % totPower)
        #       load = totInvCurr-totSellCurr+totBuyCurr
        #        print ("Load Current: %4d" % load)
                if numInverters > 0:
                    ACOutVolt /= numInverters
                    ACInVolt /= numInverters
                    invBattVolt /= numInverters
                    chgContBattVolt /= numChgCont
        #        print ("ACOut Volt (avg): %3d" % int(ACOutVolt))
        #        print ("ACIn Volt (avg): %3d" % int(ACInVolt))
        #        print ("Invert Battery Volt (avg): %.1f" % float(invBattVolt))
        #        print ("Charge Controller Battery Volt (avg): %.1f" % float(chgContBattVolt))
        #        print ("PV Power (KWH): %.1f" % float(PVKWH))
        #        print ("PV Watts : %4d" % int(pvWatts))
    
#                print(pvWatts)
                clientRecv=conn.recv(1024)
                conn.sendall(str(pvWatts).encode('utf-8'))
        #        dictionary access
        #        print (listOfInvData)
        #        print (listOfInvData[n]['Op Mode'])   n=0-2  (numInverters)
        #        print (listOfChgContData)
                
                listOfInvData=[]
                listOfChgContData = []
                totSellCurr=int(0)   
                totBuyCurr=int(0)          
                totInvCurr=int(0)
                ACOutVolt=int(0)
                ACInVolt=int(0)
                numInverters = int(0)
                numChgCont = 0
                invBattVolt = float(0.0)
                chgContBattVolt = float(0.0)
                PVKWH=float(0)
                pvWatts=int(0)
                
        #        print (int(decode_inverter_data(devlist)['1']['Sell Current']) + int(decode_inverter_data(devlist)['2']['Sell Current']))
        #        print(decode_chgcontroller(devlist))
                    
        finally:
            print ('closing socket')
            iSock.close()
        
       
    #if __name__ == '__main__':    
    def main():
        format = "%(asctime)s: %(message)s"
        logging.basicConfig(format=format, level=logging.INFO,
                            datefmt="%H:%M:%S")
    
        logging.info("Main    : before creating thread")
        x = threading.Thread(target=Reader.runReader, args=(1,))
        logging.info("Main    : before running thread")
        x.start()
        logging.info("Main    : wait for the thread to finish")
        x.join()
        logging.info("Main    : all done")



#Reader.main()
