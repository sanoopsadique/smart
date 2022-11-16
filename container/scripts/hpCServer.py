#! /usr/bin/env python3
#test
import socket
import datetime
import time
import sys
import subprocess

def writeLog(msg):
    logFile = '/smart/log.txt'
    with open(logFile,'at') as logger:
        # getting current date and time
        now = datetime.datetime.now() 
        logger.write(now.strftime('%y-%m-%d-%H:%M:%S')+' - '+msg+'\n')
    
def writeWeb(msg):
    with open('/smart/web/index.html','at') as f:
        f.write('<p>'+msg+'</p>\n')
    writeLog(msg)
	
if __name__ == '__main__': 
#def honeypot_server(client,BUFFER_SIZE):
    #Create socket to the ip and listen
    #Once connected wait for distress signal
    #if distress signal is received update log and notify
    #if disconnected update the log file, send notification and listen on port
    
    err_count = 0
    SEPARATOR = ':'
    client = []
    settingsFile = '/smart/settings/'+sys.argv[1]+'.conf'
    
    with open('/smart/web/index.html','wt') as f:
        f.write('<html><head><title>'+sys.argv[1]+' Status</title><meta http-equiv=\"refresh\" content=\"5\"></head><body>\n')
        
    writeWeb('Honeypot server container '+sys.argv[1]+' starting')
    
    with open(settingsFile,'rt') as f:
        settings = f.readline()

    clientIP, listenPort, passKey, interval, BUFFER_SIZE, rpcPort = settings.split(SEPARATOR)
    # client_ip:port to listen:encrypted passcode:interval:BUFFER_SIZE: RPC port
    listenPort = int(listenPort)
    webService = str(listenPort+1000)
    BUFFER_SIZE = int(BUFFER_SIZE)
    rpcPort = int(rpcPort)
    p = subprocess.Popen(['python3','/smart/web.py',webService])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',int(listenPort)))
    while True:
        while True:
            try:
                writeWeb('Waiting for honeypot client '+clientIP)
                s.listen(5)
                conn, addr = s.accept()
                if addr[0] != clientIP:
                    writeWeb('Incoming connection from unexpected Honeypot client at '+clientIP)
                    conn.close()
                    continue
                recvd = conn.recv(BUFFER_SIZE).decode()
                status, passcode = recvd.split(SEPARATOR)
                if passcode != passKey:
                    #passcodes do not match
                    writeWeb('Honeypot at '+clientIP+' has wrong passcode')
                    status = 'wrong-pass'
                    conn.sendall(status.encode())
                    time.sleep(1) 
                    conn.close()
                    continue
                else:
                    writeWeb('Honeypot at '+clientIP+' connected. Sending success code')
                    status = 'success'
                    conn.sendall(status.encode())
                    time.sleep(1) 
                    break
                    
                err_count = 0
            
            except KeyboardInterrupt:
                writeWeb('Exit request by user. Shutting down server')
                s.close()
                p.kill()
                exit()
            
            except ConnectionError as e:
                writeWeb('Error: '+str(e)+' on '+clientIP+'. Re-initiating listening.')
                err_count = err_count + 1
                
                if err_count > 3:
                    exit(0)
                    p.kill()
            
            except Exception as e:
                writeWeb('Script error: '+ str(e))
                s.close()
                p.kill()
                exit(0)        
        while True:
            try:
                recvd = conn.recv(BUFFER_SIZE).decode()
                status,remarks = recvd.split(SEPARATOR)
                if status == '1':
                    writeWeb(remarks + ' connected to '+clientIP+'. Sending notification.')
                    #notifyHPUsers('1',clientIP,remarks)
                elif status == '0':
                    conn.close()
                    if remarks == '0':
                        writeWeb('Honeypot at '+clientIP+' terminated by user')
                        #notifyHPUsers('0',clientIP,0)
                        break
                    else:
                        writeWeb('Honeypot at '+clientIP+' terminated due to script error: '+ remarks)
                        #notifyHPUsers('0',clientIP,remarks)
                        break
                err_count = 0
            except KeyboardInterrupt:
                writeWeb('Exit request by user. Shutting down server')
                s.close()
                exit()
                
            except ConnectionError as e:
                writeWeb('Error: '+str(e)+' on '+clientIP+'. Re-initiating attack listening.')
                err_count = err_count + 1
                #notifyHPUsers(2,clientIP,0)
                
                if err_count > 3:
                    break     
            except Exception as e:
                writeWeb('Script error: '+ str(e))
                s.close()
                exit(0)    
