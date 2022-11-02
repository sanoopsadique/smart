import sys
import socket
import time
import datetime
import os
import hashlib

#Read info from settings file

'''
open settings file
iterate line by line to get ip address and port number
store info in variables
close file
'''
def writeLog(msg,logFile):
    logger = open(logFile,"at")
    # getting current date and time
    now = datetime.datetime.now() 
    logger.write(now.strftime("%y-%m-%d-%H:%M:%S")+" - "+msg+"\n")
    logger.close()

settings_file = open('settings.txt','rt')

settings_temp = settings_file.readlines()
settings_info = []

for line in settings_temp:
	if line[0] == '#' or line[0]=='\n' or line[0]==' ':
		continue		
	else:
		settings_info.append(line.rstrip())

server_ip,server_port,buff_size,services,logFile,passcode = settings_info
md5C = hashlib.md5(passcode.encode()).hexdigest()
passcode = md5C
services_list = []
services_list = services.split(':')
print("Script started, settings read")
buff_size=int(buff_size)
server_port = int(server_port)
    
# connect to server

while True:
    #connect to the server
    serverConnect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print("Gathering service information")
        status_list=[]
        for service in services_list:
            status = os.popen("systemctl is-active "+service).read().rstrip()
            if status =="unknown":
                status = "Not Installed"
            status_list.append([service,status])    
        msg = passcode+':'+str(status_list)
        print("Connecting to server at "+server_ip)
        serverConnect.connect((server_ip,server_port))
        try:
            serverConnect.sendall(msg.encode())
            print("Passcode & Service status sent.. waiting for response")
            recvd = serverConnect.recv(buff_size)
            recvd=recvd.decode()
            resp,interval = recvd.split(':')
            if resp == 'wrong-pass':
                writeLog("Server denied connection due to passcode mismatch. Program exiting.",logFile)
                time.sleep(2)
                exit(0)
            elif resp == 'success':
                print("Server connection established. Starting monitoring and sending status update every "+ interval + " seconds.")
                writeLog("Server connection established. Starting honeypot process.",logFile)
                
                while True:
                    time.sleep(int(interval)-2)
                    status_list=[]
                    for service in services_list:
                        status = os.popen("systemctl is-active "+service).read().rstrip()
                        if status =="unknown":
                            status = "Not Installed"
                        status_list.append([service,status])    
                    msg = '1:'+str(status_list)
                    serverConnect.sendall(msg.encode())
                    print("Status update sent to server")
            else:
                print("Unknown status received, retrying connection")
                serverConnect.close()
        except KeyboardInterrupt:
            print("Exit request by user. Sending message to server and shutting down")
            serverConnect.sendall('0:0'.encode())
            writeLog("Exit request by user. Sending message to server and shutting down",logFile)
            serverConnect.close()
            exit()
        except ConnectionError as e:
            print("Server connection closed. Retrying in ")
            serverConnect.close()
            i = 10 
            while i>=0:
                print(i, end=" ")
                sys.stdout.flush()
                i = i - 1
                time.sleep(1)
            print()    
                    
        except Exception as e:
            writeLog("Error: "+str(e),logFile)
            serverConnect.close()
        
    except KeyboardInterrupt:
        print("Exit request by user. Shutting down")
        serverConnect.close()
        exit()
    
    except ConnectionError as e:
        print("Error connecting to server. Retrying in ")
        serverConnect.close()
        i = 10 
        while i>=0:
            print(i, end=" ")
            sys.stdout.flush()
            time.sleep(1)
            i = i - 1
                    
        
    except Exception as e:
        serverConnect.sendall('0:1'.encode())
        serverConnect.close()
        writeLog("Script error: "+str(e),logFile)
        print("Script error: "+str(e))
        
        