import datetime, time
import hashlib
import os
import subprocess
import socket

rootFolder = '/etc/smart/server/'
def writeLog(msg):
    global rootFolder
    logFile = rootFolder+"log.txt"
    with open(logFile,"at") as logger:
        # getting current date and time
        now = datetime.datetime.now() 
        logger.write(now.strftime("%y-%m-%d-%H:%M:%S")+" - "+msg+"\n")

def writeWeb(msg):
    global rootFolder
    with open(rootFolder+"web/index.html","at") as f:
        f.write(msg)
    writeLog(msg)


if __name__ == "__main__": 
    
    with open(rootFolder+"web/index.html","wt") as f:
        f.write("<html><head><title>SMART Core Server Status</title><meta http-equiv=\"refresh\" content=\"5\"></head><body>\n")
    
    settings_info = []
    with open(rootFolder+"settings.conf","rt") as f:
        settings_temp = f.readlines()

        for line in settings_temp:
            if line[0] == '#' or line[0]=='\n' or line[0]==' ':
                continue		
            else:
                settings_info.append(line.rstrip())

    SEPARATOR = ":"
    BUFFER_SIZE = settings_info[0]
    webService= settings_info[1]
    rpcListen = settings_info[2]
    del settings_info[0]
    del settings_info[0]
    del settings_info[0]
    #writeLog("Program started successfully, getting list of clients")
    
    contSettingsFolder = rootFolder+"containers/"
    client_qty=len(settings_info)
    honeyPots = []
    statusMon= [] 
    for client in settings_info:
        mode,ip,port,passcode,interval = client.split(SEPARATOR)
        passcode = hashlib.md5(passcode.encode()).hexdigest()
        if mode == 'H':
            honeyPots.append([ip,port,passcode,interval])
        elif mode == 'M':
            statusMon.append([ip,port,passcode,interval])
    
    print("Settings read, deloying containers")
    
    deployedContainers = []
    for client in statusMon:
                
        fileName = contSettingsFolder+"sm-"+client[1]+".conf"
        with open(fileName,'wt') as f:
            f.write(client[0]+":"+client[1]+":"+client[2]+":"+client[3]+":"+BUFFER_SIZE+":"+rpcListen)
        
        os.system('docker run -dtv '+contSettingsFolder+':/smart/settings -p '+client[1]+ ':' + client[1]+ ' -p '+webport + ':' + webport  +' --name sm-'+client[1]+ ' sanoopsadique/smart:latest python3 /smart/smCserver.py sm-'+client[1])
        deployedContainers.append('sm-'+client[1])
        webport = str(int(client[1])+1000)
        writeWeb("<p>Status monitoring server container for client at "+client[0]+ "started. <a href=\"\\\\localhost:"+webport+"\\ target=_blank> Click here to view status</a></p>\n")
    
         
    print("Status Monitoring container(s) deloyed, starting honeypot container deployment")
    writeWeb("<p>Status Monitoring container(s) deloyed, starting honeypot container deployment</p>/n")
                
    for client in honeyPots:
        webport = str(int(client[1])+1000)
        fileName = contSettingsFolder+"hp-"+client[1]+".conf"
        with open(fileName,'wt') as f:
            #add values to settings file client_ip\nport\npasscode\ninterval\npipe\nwebport
            f.write(client[0]+":"+client[1]+":"+client[2]+":"+client[3]+":"+BUFFER_SIZE+":"+rpcListen) 
        os.system('docker run -dtv '+contSettingsFolder+':/smart/settings -p '+client[1]+ ':' + client[1]+ ' -p '+webport + ':' + webport + ' --name hp-'+client[1]+ ' sanoopsadique/smart:latest python3 /smart/hpCserver.py hp-'+client[1]) 
        deployedContainers.append('hp-'+client[1])
        webport = str(int(client[1])+1000)
        print("Honeypot server container for client at "+client[0]+ "started. View status on \\\\localhost:"+webport+ "\\ \n")
        writeWeb("<p>Honeypot server container for client at "+client[0]+ "started. <a href=\"\\\\localhost:"+webport+ "\\ target=_blank> Click here to view status</a></p>\n")
        
    print("Honeypot container(s) deloyed.")
    writeWeb("<p>Honeypot container(s) deloyment complete</p>/n")
                
    print("Starting web service")
    p = subprocess.Popen(["python3",rootFolder+"web.py",webService])
    time.sleep(2)
    print("Web service started. Visit \\\\localhost\\:"+webService+"\\ to view web page")
    print("Listening for notification requests:")
    writeWeb("Listening for notification requests:")
    err_count = 0
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',int(rpcListen)))
    try:
        while True:
            try:
                s.listen(client_qty)
                conn, addr = s.accept()
                recvd = conn.recv(int(BUFFER_SIZE)).decode()
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
        for item in deployedContainers:
            os.system("docker stop "+item)
            os.system("docker rm "+item)
        p.kill()
        print("Server stopped") 
    
    except Exception as e:
        print("Script error: "+ str(e))
        for item in deployedContainers:
            os.system("docker stop "+item)
            os.system("docker rm "+item)
        p.kill()
        s.close()
        exit(0)    
    