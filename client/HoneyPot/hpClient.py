
import sys
import socket
import time
import datetime
import hashlib
'''
from psutil import process_iter
from signal import SIGTERM 
'''


#Read info from settings file

'''
open settings file
iterate line by line to get ip address and port number
store info in variables
close file
'''
def writeLog(msg,logFile):
    logger = open(logFile,'at')
    # getting current date and time
    now = datetime.datetime.now() 
    logger.write(now.strftime('%y-%m-%d-%H:%M:%S')+' - '+msg+'\n')
    logger.close()

settings_file = open('settings.txt','rt')

settings_temp = settings_file.readlines()
settings_info = []

for line in settings_temp:
	if line[0] == '#' or line[0]=='\n' or line[0]==' ':
		continue		
	else:
		settings_info.append(line.rstrip())

server_ip,server_port,buff_size,listening_port,logFile,passcode = settings_info
md5C = hashlib.md5(passcode.encode()).hexdigest()
passcode = '0:'+md5C
writeLog('Script started, settings read',logFile)
buff_size=int(buff_size)
server_port = int(server_port)
listening_port = int(listening_port)
'''
# checking listening port is in use, if yes killing the process
for proc in process_iter():
    for conns in proc.connections(kind='inet'):
        if conns.laddr.port == listening_port:
            proc.send_signal(SIGTERM) # or SIGKILL
'''
try:
    hpConnect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hpConnect.bind(('',listening_port))
except:
    print('Listening port '+str(listening_port)+' is currently in use. Exiting program')
    exit(0)
    
# connect to server

while True:
    #connect to the server
    try:
        serverConnect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Connecting to server at '+server_ip)
        time.sleep(3)
        serverConnect.connect((server_ip,server_port))
        try:
            serverConnect.sendall(passcode.encode())
            print('Passcode sent.. waiting for response')
            recvd = serverConnect.recv(buff_size)
            recvd=recvd.decode()
            if recvd == 'wrong-pass':
                writeLog('Server denied connection due to passcode mismatch. Program exiting.',logFile)
                time.sleep(2)
                exit(0)
            elif recvd == 'success':
                print('Server connection established. Starting honeypot process.')
                writeLog('Server connection established. Starting honeypot process.',logFile)
                
                while True:
                    try:
                        print('Starting listening on '+str(listening_port))
                        hpConnect.listen(buff_size)
                        attk, addr = hpConnect.accept()
                        writeLog('Connection request from '+addr[0]+'. Sending message to server',logFile)
                        print('Connection request from '+addr[0]+'. Sending message to server')
                        msg = '1:'+addr[0]
                        serverConnect.sendall(msg.encode())
                        print('Attack informed to Server. Starting listening again')
                        attk.sendall('Hello attacker'.encode())
                        time.sleep(1)
                        attk.close()
                        
                    except ConnectionError as e:
                        print('Server connection closed. Retrying in ')
                        i = 10 
                        while i>0:
                            print(i, end=' ')
                            sys.stdout.flush()
                            time.sleep(1)
                            i = i - 1
                        print('')
                        break
                    except Exception as e:
                        writeLog('Honeyport Error: '+str(e),logFile)
                        print('Honeyport Error: '+str(e))
            else:
                print('Unknown status received, retrying connection')
                serverConnect.close()
                exit(0)
        except KeyboardInterrupt:
            print('Exit request by user. Sending message to server and shutting down')
            serverConnect.sendall('0:0'.encode())
            hpConnect.shutdown(0)
            writeLog('Exit request by user. Sending message to server and shutting down',logFile)
            serverConnect.close()
            exit()
        except Exception as e:
            writeLog('Error: '+str(e),logFile)
            serverConnect.close()
        
    except KeyboardInterrupt:
        print('Exit request by user. Shutting down')
        serverConnect.close()
        exit()
    
    except ConnectionError as e:
        print('Error connecting to server. Retrying in ')
        serverConnect.close()
        i = 10 
        while i>0:
            print(i, end=' ')
            sys.stdout.flush()
            time.sleep(1)
            i = i - 1
        print('')
    except Exception as e:
        print('Script error: '+str(e))
        writeLog('Script error: '+str(e),logFile)
        serverConnect.close()
        exit()

'''
    listen on port number taken from settings file
    if (connection is established):
        get IP address of connecting host
        send IP to log file
        inform monitoring server
        elif (connection is not established):
            return to start of loop and listen again
        
'''
