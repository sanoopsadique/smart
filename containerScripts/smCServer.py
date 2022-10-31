#! /usr/bin/env python3

import socket
import datetime
import time
from tabulate import tabulate
import sys




def writeLog(msg,logFile):
    logger = open(logFile,"at")
    # getting current date and time
    now = datetime.datetime.now() 
    logger.write(now.strftime("%y-%m-%d-%H:%M:%S")+" - "+msg+"\n")
    logger.close()


if __name__ == "__main__": 
#def statusMon_server(client,BUFFER_SIZE,logFile):
    #Create socket to the ip and listen of particular number of seconds
    #Once connected wait for services msg [(service_name,status),(service_name,status)] 
    #
    #if any service status changed, send notification and listen again
    # Client_status:
    # 0 - never attempted connected, 1 - previous unsuccessful connection, 2 - connected, 5 - reset connection due to no heartbeat
    client = []
    with open(sys.argv[1],'rt') as f:
        settings = f.readline()
    client = settings.split(':')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',int(client[1])))
    client_status = 0
    err_count = 0
    while True:
        while True:
            try:
                print("Starting listening for Status monitoring on port "+client[1])
                s.settimeout(30)
                s.listen(5)
                conn, addr = s.accept()
                
                if addr[0] != client[0]:
                    writeLog("Incoming connection from unexpected Honeypot client at "+client[0],logFile)
                    conn.close()
                    continue
                
                recvd = conn.recv(BUFFER_SIZE).decode()
                passcode,service_list= recvd.split(':')
                service_list = eval(service_list)
                client[2] = hashlib.md5(client[2].encode()).hexdigest()
                
                if passcode != client[2]:
                    #passcodes do not match
                    writeLog("SM CLient at "+client[0]+" has wrong passcode",logFile)
                    print("SM CLient at "+client[0]+" has wrong passcode")
                    # sending status: 0 - connected, 1 - disconnected due to passcode mismatch
                    status = "wrong-pass"
                    conn.sendall(status.encode())
                    time.sleep(2) 
                    conn.close()
                    continue
                else:
                    client_status = 2
                    writeLog("SM Client at "+client[0]+" connected. Sending success code",logFile)
                    print("SM Client at "+client[0]+" connected. Current status: ")
                    print (tabulate(service_list, headers=["Service", "Status"]))
                    inactive ='The following services are not running on '+client[0]+' at startup:\n'
                    for service in service_list:
                        if service[1] != 'active':
                            inactive = inactive+service[0]+'\n'
                    #notifySM("Services inactive at startup",inactive) 
                    status = "success:"+client[3]
                    conn.sendall(status.encode())
                    time.sleep(2) 
                    break
                err_count = 0
            
            except KeyboardInterrupt:
                print("Exit request by user. Shutting down server")
                s.close()
                exit()
                        
            except socket.timeout:
                if client_status == 2: # Client was previously connected now got diconnected and not reconnecting
                    #notifySM("Client device disconnected","Client device at "+client[0]+ " changed state to disconnected")
                    print("Client device at "+client[0]+ " changed state to disconnected")
                    client_status = 1
                elif client_status == 0: # Client didnt connected on time
                    #notifySM("No connection from Client device","Client device at "+client[0]+ " has not initiated a connection")
                    print("Client device at "+client[0]+ " has not initiated a connection")
                    client_status = 1
                
            except ConnectionError as e:
                writeLog("Error: "+str(e)+" on "+client[0]+". Re-initiating listening.",logFile)
                err_count = err_count + 1
                
                if err_count > 3:
                    exit(0)
            
            except Exception as e:
                print("Script error: "+e)
                s.close()
                exit(0)    
        
        while True:
            client_status = 2
            try:
                conn.settimeout(int(client[3]))
                status_list = conn.recv(BUFFER_SIZE).decode()
                orig_status = status_list
                status,status_list = status_list.split(':')
                if status == '0':
                    conn.close()
                    if status_list == '0':
                        print("Client at "+client[0]+" terminated by user")
                        writeLog("Honeypot at "+client[0]+" terminated by user",logFile)
                        #notifyHPUsers('0',client[0],0)
                        client_status = 0
                        break
                    else:
                        writeLog("Honeypot at "+client[0]+" terminated due to script error: "+ status_list,logFile)
                        #notifyHPUsers('0',client[0],remarks)
                        break
                status_list = eval(status_list)    
                if status_list == service_list:
                    print("No change in service status")
                    service_list = status_list
                    continue
                    
                else:
                    if len(service_list) != len(status_list): 
                        print("Unexpected status update message")
                        continue
                    i=0
                    while i < len(service_list):
                        if service_list[i][1] != status_list[i][1]:
                            print("Status of "+status_list[i][0]+" changed from "+ service_list[i][1] +" to "+status_list[i][1])
                        i= i+1
                    service_list = status_list
                    print("New Status:")
                    print (tabulate(service_list, headers=["Service", "Status"]))
                    
                err_count = 0
            
            except KeyboardInterrupt:
                print("Exit request by user. Shutting down server")
                s.close()
                exit()
            
            
            except socket.timeout:
                if client_status == 2:
                    #notifySM("Client device disconnected","Client device at "+client[0]+ " changed state to disconnected")
                    print("Client device at "+client[0]+ " changed state to disconnected")
                    client_status = client_status+1
                elif client_status < 5:
                    client_status = client_status+1

            
            except ConnectionError as e:
                writeLog("Error: "+str(e)+" on "+client[0]+". Re-initiating listening.",logFile)
                print("Error: "+str(e)+" on "+client[0]+". Re-initiating listening.")
                err_count = err_count + 1
                
                if err_count > 3:
                    exit(0)    
                
            except Exception as e:
                print("Script error: "+e)
                s.close()
                exit(0)
            