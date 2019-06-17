import sys
import time
import socket


# simulate mate--read data from matetest.obm, 7 lines (devices) at a time once per second
# output to socket
HOST=''
PORT = 5557

f = open ("matetest.obm")


def readFile():
    line = ""
    while line != "H":
        line = f.read(48)
        lineSplit=line.split(",")
        if lineSplit[0] == "H":
            break
    
    while (f is not None):
        for numLines in range (0,7):
            line = f.read(48)
            sys.stdout.write(line)
            sys.stdout.flush()
            byteStr=str.encode(line)
            s.sendall(byteStr)
        time.sleep(1)
    


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print ('Socket created')

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
    
print ('Socket bind complete')

#Start listening on socket
s.listen(10)
print ('Socket now listening')

#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print ('Connected with ' + addr[0] + ':' + str(addr[1])) 
    readFile()
    
s.close()





    
    
