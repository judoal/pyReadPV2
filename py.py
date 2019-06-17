import socket
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.1.112', 8899)
sock.connect(server_address)
f=open ("readpv.out","w+", buffering=512)
lineLen=[]
date="%m%d%Y"
tod="%H%M%S"
data=[]
tmp=[]
invDataDict={}
listOfInvdata=[]

chgContDict={}
listOfChgContData=[]

def sum_digits(str1):
#    return sum(int(x) for x in str1 if x.isdigit())
    a=int(0)
    for x in str1:
        if x.isdigit():
            x=int(x)+int(a)
            a=x
    return x
                
def decode_inverter_data(inverterList):
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

        errCode = invDataDict[inverterList[0]]["Error Mode"]   
        
        
        print (invDataDict[inverterList[0]])

        return invDataDict

        
def decode_chgcontroller(chgContList):
    for item in chgContList:
        chgContDict[chgContList[0]] = {
            "ID" : chgContList[0], 
            "charger Current" : chgContList[2],
            "PV Current" : chgContList[3],
            "PV Voltage" : chgContList[4],
            "Power (KWH)" : chgContList[5],
            "Aux Mode" : chgContList[7],
            "Error" : chgContList[8],
            "Charger Mode" : chgContList[9],
            "Battery Volt" : chgContList[10]
            }
            
        listOfChgContData.append(chgContDict)
        print (chgContDict[chgContList[0]])
        return chgContDict
                
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
                
try:
    while 1:
        data = sock.recv(512)
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
        print (timestamp)
#        print (datalist)
        for n in range(1,numItems):
            tmp=datalist[n]
#            print (tmp[0])
            devlist=tmp[0].split(",")
            
            #count number of measurements in each device in CSV delimited string
            #chksum is the last item
            numStrItem=tmp[0].count(",")
    
            #chksum is bum of numeric values  of each digit in string
            #alpha is numerically encoded by ascii value - '0'
            
            chksum=devlist[numStrItem]
            csdigit=sum_digits(chksum)
            digits_sum=sum_digits(tmp[0])
            chksum_calc=int(digits_sum) - int(csdigit)
            
            #inverters have numeric code in 0th position
            #numeric code used to calc chksum
            if devlist[0].isdigit():
                listOfInvdata=[]
                if (int(chksum_calc) == int(chksum)):
                    decode_inverter_data(devlist)
                                       
            #charge controllers have upper case alpha in 0th position
            #get relative position as index to calc chksum       
            if devlist[0].isalpha():    # devuceID not numeric
                code = ord(devlist[0]) - ord("0") 
                if (int(code + chksum_calc) == int (chksum)):
                    decode_chgcontroller(devlist)
                
finally:
    print ('closing socket')
    sock.close()