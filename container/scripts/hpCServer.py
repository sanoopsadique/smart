#! /usr/bin/env python3

import socket
import datetime
import time
import sys

def writeLog(msg,logFile):
    logger = open(logFile,"at")
    # getting current date and time
    now = datetime.datetime.now() 
    logger.write(now.strftime("%y-%m-%d-%H:%M:%S")+" - "+msg+"\n")
    logger.close()

def writeWeb(msg):
    with open("web/index.html","rt") as f:
        content = f.readlines()
    with open("web/index.html","wt") as f:
        f.write(msg+content)
	
if __name__ == "__main__": 
#def honeypot_server(client,BUFFER_SIZE,logFile):
    #Create socket to the ip and listen
    #Once connected wait for distress signal
    #if distress signal is received update log and notify
    #if disconnected update the log file, send notification and listen on port
    
    err_count = 0
    SEPARATOR = ":"
    client = []
    settingsFile = "settings/"+sys.argv[1]
    logFile = "log.txt"
    with open(settingsFile,'rt') as f:
        settings = f.readline()
    clientIP, listenPort, passKey, interval, BUFFER_SIZE, rpcPort = settings.split('SEPARATOR')
    # client_ip:port to listen:encrypted passcode:interval:BUFFER_SIZE: RPC port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',int(listenPort)))
    while True:
        while True:
            try:
                print("Waiting for honeypot client "+clientIP)
                s.listen(5)
                conn, addr = s.accept()
                if addr[0] != clientIP:
                    writeLog("Incoming connection from unexpected Honeypot client at "+clientIP,logFile)
                    conn.close()
                    continue
                recvd = conn.recv(BUFFER_SIZE).decode()
                status, passcode = recvd.split('SEPARATOR')
                if passcode != passKey:
                    #passcodes do not match
                    writeLog("Honeypot at "+clientIP+" has wrong passcode",logFile)
                    status = "wrong-pass"
                    conn.sendall(status.encode())
                    time.sleep(1) 
                    conn.close()
                    continue
                else:
                    writeLog("Honeypot at "+clientIP+" connected. Sending success code",logFile)
                    print("Honeypot at "+clientIP+" connected. Sending success")
                    status = "success"
                    conn.sendall(status.encode())
                    time.sleep(1) 
                    break
                    
                err_count = 0
            
            except KeyboardInterrupt:
                print("Exit request by user. Shutting down server")
                s.close()
                exit()
            
            except ConnectionError as e:
                writeLog("Error: "+str(e)+" on "+clientIP+". Re-initiating listening.",logFile)
                err_count = err_count + 1
                
                if err_count > 3:
                    exit(0)
            
            except Exception as e:
                print("Script error: "+ str(e))
                s.close()
                exit(0)        
        while True:
            try:
                recvd = conn.recv(BUFFER_SIZE).decode()
                status,remarks = recvd.split(SEPARATOR)
                if status == '1':
                    print(remarks + " connected to "+clientIP+". Sending notification.")
                    writeLog(remarks + " connected to "+clientIP+". Sending notification.",logFile)
                    #notifyHPUsers('1',clientIP,remarks)
                elif status == '0':
                    conn.close()
                    if remarks == '0':
                        print("Honeypot at "+clientIP+" terminated by user")
                        writeLog("Honeypot at "+clientIP+" terminated by user",logFile)
                        #notifyHPUsers('0',clientIP,0)
                        break
                    else:
                        writeLog("Honeypot at "+clientIP+" terminated due to script error: "+ remarks,logFile)
                        #notifyHPUsers('0',clientIP,remarks)
                        break
                err_count = 0
            except KeyboardInterrupt:
                print("Exit request by user. Shutting down server")
                s.close()
                exit()
                
            except ConnectionError as e:
                writeLog("Error: "+str(e)+" on "+clientIP+". Re-initiating attack listening.",logFile)
                err_count = err_count + 1
                #notifyHPUsers(2,clientIP,0)
                
                if err_count > 3:
                    break     
            except Exception as e:
                print("Script error: "+ str(e))
                s.close()
                exit(0)    
