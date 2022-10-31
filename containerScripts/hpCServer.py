#! /usr/bin/env python3

import socket
import datetime
import time

def writeLog(msg,logFile):
    logger = open(logFile,"at")
    # getting current date and time
    now = datetime.datetime.now() 
    logger.write(now.strftime("%y-%m-%d-%H:%M:%S")+" - "+msg+"\n")
    logger.close()
	
if __name__ == "__main__": 
#def honeypot_server(client,BUFFER_SIZE,logFile):
    #Create socket to the ip and listen
    #Once connected wait for distress signal
    #if distress signal is received update log and notify
    #if disconnected update the log file, send notification and listen on port
    #client[0] = IP
    #client[1] = Port
    #client[2] = Passcode
    err_count = 0
    client = []
    with open(sys.argv[1],'rt') as f:
        settings = f.readline()
    client = settings.split(':')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',int(client[1])))
    while True:
        while True:
            try:
                print("Waiting for honeypot client "+client[0])
                s.listen(5)
                conn, addr = s.accept()
                if addr[0] != client[0]:
                    writeLog("Incoming connection from unexpected Honeypot client at "+client[0],logFile)
                    conn.close()
                    continue
                recvd = conn.recv(BUFFER_SIZE).decode()
                status, passcode = recvd.split(':')
                if passcode != client[2]:
                    #passcodes do not match
                    writeLog("Honeypot at "+client[0]+" has wrong passcode",logFile)
                    status = "wrong-pass"
                    conn.sendall(status.encode())
                    time.sleep(2) 
                    conn.close()
                    continue
                else:
                    writeLog("Honeypot at "+client[0]+" connected. Sending success code",logFile)
                    print("Honeypot at "+client[0]+" connected. Sending success")
                    status = "success"
                    conn.sendall(status.encode())
                    time.sleep(2) 
                    break
                    
                err_count = 0
            
            except KeyboardInterrupt:
                print("Exit request by user. Shutting down server")
                s.close()
                exit()
            
            except ConnectionError as e:
                writeLog("Error: "+str(e)+" on "+client[0]+". Re-initiating listening.",logFile)
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
                    print(remarks + " connected to "+client[0]+". Sending notification.")
                    writeLog(remarks + " connected to "+client[0]+". Sending notification.",logFile)
                    #notifyHPUsers('1',client[0],remarks)
                elif status == '0':
                    conn.close()
                    if remarks == '0':
                        print("Honeypot at "+client[0]+" terminated by user")
                        writeLog("Honeypot at "+client[0]+" terminated by user",logFile)
                        #notifyHPUsers('0',client[0],0)
                        break
                    else:
                        writeLog("Honeypot at "+client[0]+" terminated due to script error: "+ remarks,logFile)
                        #notifyHPUsers('0',client[0],remarks)
                        break
                err_count = 0
            except KeyboardInterrupt:
                print("Exit request by user. Shutting down server")
                s.close()
                exit()
                
            except ConnectionError as e:
                writeLog("Error: "+str(e)+" on "+client[0]+". Re-initiating attack listening.",logFile)
                err_count = err_count + 1
                #notifyHPUsers(2,client[0],0)
                
                if err_count > 3:
                    break     
            except Exception as e:
                print("Script error: "+ str(e))
                s.close()
                exit(0)    
