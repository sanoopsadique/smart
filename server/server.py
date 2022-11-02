import datetime, time
import hashlib
import os
import subprocess
import socket


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
    
  
    print("SMART Server starting")
    
    settings_info = []
    with open("settings.txt","rt") as f:
        settings_temp = f.readlines()

        for line in settings_temp:
            if line[0] == '#' or line[0]=='\n' or line[0]==' ':
                continue		
            else:
                settings_info.append(line.rstrip())

    SEPARATOR = ":"
    BUFFER_SIZE = int(settings_info[0])
    logFile=settings_info[1]
    rpcListen = int(settings_info[2])
    del settings_info[0]
    del settings_info[0]
    del settings_info[0]
    #writeLog("Program started successfully, getting list of clients",logFile)
    writeWeb("<html><head><title>SMART Status</title><meta http-equiv=\"refresh\" content=\"5\"></head><body>\n")
    contSettingsFolder = "containers/"
    client_qty=len(settings_info)
    honeyPots = []
    statusMon= [] 
    for client in settings_info:
        mode,ip,port,passcode,interval = client.split(SEPARATOR)
        passcode = hashlib.md5(passcode.encode()).hexdigest()
        if mode == 'H':
            honeyPots.append([ip,port,passcode])
        elif mode == 'M':
            statusMon.append([ip,port,passcode,interval])
    
    print("Settings read, deloying containers")
    
    
    for client in statusMon:
                
        fileName = contSettingsFolder+"/sm-"+client[1]
        with open(fileName,'wt') as f:
            f.write(client[0]+":"+client[1]+":"+client[2]+":"+client[3]+":"+BUFFER_SIZE+":"+rpcListen)
        
        os.system('docker run -d -v '+contSettingsFolder+ ':/smart/settings -p '+client[1]+ ':' + client[1]+ '--hostname sm-'+client[1]+ 'sanoopsadique/smart python3 /smart/smCserver.py sm-'+client[1]) 
        webport = str(int(client[1])+1000)
        writeWeb("<p>Status monitoring server container for client at "+client[0]+ "started. <a href=\"\\\\localhost:"+webport+ "\\ target=_blank> Click here to view status</a></p>\n")
    
         
    print("Status Monitoring container(s) deloyed, starting honeypot container deployment")
    writeWeb("<p>Status Monitoring container(s) deloyed, starting honeypot container deployment</p>/n")
                
    for client in honeyPots:
        fileName = contSettingsFolder+"/hp-"+client[1]
        with open(fileName,'wt') as f:
            #add values to settings file client_ip\nport\npasscode\ninterval\npipe\nwebport
            f.write(client[0]+":"+client[1]+":"+client[2]+":"+":"+BUFFER_SIZE+":"+rpcListen)
        
        os.system('docker run -d -v '+contSettingsFolder+':/smart/settings -p '+client[1]+ ':' + client[1]+ 'sanoopsadique/smart:latest python3 /smart/smCserver.py hp-'+client[1]) 
        
        webport = str(int(client[1])+1000)
        print("Honeypot server container for client at "+client[0]+ "started. View status on \\\\localhost:"+webport+ "\\ \n")
        writeWeb("<p>Honeypot server container for client at "+client[0]+ "started. <a href=\"\\\\localhost:"+webport+ "\\ target=_blank> Click here to view status</a></p>\n")
        
    print("Honeypot container(s) deloyed.")
    writeWeb("<p>Honeypot container(s) deloyment complete</p>/n")
                
    print("Starting web service")
    p = subprocess.Popen(["python3 ","web/mainweb.py"])
    time.sleep(2)
    print("Web service started. Visit \\\\localhost\\:"+str(rpcListen)+"\\ to view web page")
    print("Listening for notification requests:")
    err_count = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',rpcListen))
    try:
        while True:
            try:
                s.listen(client_qty)
                conn, addr = s.accept()
                recvd = conn.recv(BUFFER_SIZE).decode()
                cMode,message = recvd.split(":")
                print("Message from client " + addr + " to " + cMode + " recipents: "+message)
                writeWeb("<p>Message from client " + addr + " to " + cMode + " recipents: "+message+"</p>/n")
                conn.close()
                err_count = 0
            except ConnectionError as e:
                print("Connection Error: "+str(e))
                err_count = err_count + 1
                #notifyHPUsers(2,client[0],0)
                
                if err_count > 3:
                    break     
    except KeyboardInterrupt:
        print("Exit request by user. Stopping containers")
        writeWeb("<p>Exit request by user. Stopping containers</p>/n")
        os.system("docker rm -f $(docker ps -a -q)")
        p.kill()
        print("Server stopped") 
    
    except Exception as e:
        print("Script error: "+ str(e))
        os.system("docker rm -f $(docker ps -a -q)")
        p.kill()
        s.close()
        exit(0)    
    