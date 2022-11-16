import datetime, time
import hashlib
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


rootFolder = '/etc/smart/server/'
def writeLog(msg):
    global rootFolder
    logFile = rootFolder+'log.txt'
    with open(logFile,'at') as logger:
        # getting current date and time
        now = datetime.datetime.now() 
        logger.write(now.strftime('%y-%m-%d-%H:%M:%S')+' - '+msg+'\n')

def writeWeb(msg):
    global rootFolder
    with open(rootFolder+'web/index.html','at') as f:
        f.write('<p>'+msg+'</p>')
    writeLog(msg)

class MyServer(BaseHTTPRequestHandler): 
    def do_GET(self):
        global service
        global refresh
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        filePath = '/etc/smart/server/web/index.html'
        with open(filePath,'rt') as f:	
            for line in f:
                self.wfile.write(bytes(line, 'utf-8'))
        self.wfile.write(bytes('</body></html>', 'utf-8'))


if __name__ == '__main__': 
    
    with open(rootFolder+'web/index.html','wt') as f:
        f.write('<html><head><title>SMART Core Server Status</title><meta http-equiv=\"refresh\" content=\"5\"></head><body>\n')
    
    settings_info = []
    with open(rootFolder+'settings.conf','rt') as f:
        settings_temp = f.readlines()

        for line in settings_temp:
            if line[0] == '#' or line[0]=='\n' or line[0]==' ':
                continue		
            else:
                settings_info.append(line.rstrip())

    SEPARATOR = ':'
    BUFFER_SIZE = settings_info[0]
    webService= settings_info[1]
    del settings_info[0]
    del settings_info[0]
    
    contSettingsFolder = rootFolder+'containers/'
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
    print('Program started, deploying '+str(client_qty)+' containers: ')
    writeWeb('Settings read, deloying containers')
    
    deployedContainers = []
    for client in statusMon:
        webport = str(int(client[1])+1000)
        fileName = contSettingsFolder+'sm-'+client[1]+'.conf'
        with open(fileName,'wt') as f:
            f.write(client[0]+':'+client[1]+':'+client[2]+':'+client[3]+':'+BUFFER_SIZE+':'+webService)
        
        os.system('docker run -dtv '+contSettingsFolder+':/smart/settings -p '+client[1]+ ':' + client[1]+ ' -p '+webport + ':' + webport  +' --name sm-'+client[1]+ ' sanoopsadique/smart:latest python3 /smart/smCServer.py sm-'+client[1])
        print(' : Success')
        deployedContainers.append('sm-'+client[1])
        webport = str(int(client[1])+1000)
        writeWeb('Status monitoring server container for client at '+client[0]+ ' started. <a href=\"sm\" onmouseover=\"javascript:event.target.port='+webport+'\" target=_blank> Click here to view status</a>\n')
    
         
    writeWeb('Status Monitoring container(s) deloyed, starting honeypot container deployment\n')
                
    for client in honeyPots:
        webport = str(int(client[1])+1000)
        fileName = contSettingsFolder+'hp-'+client[1]+'.conf'
        with open(fileName,'wt') as f:
            #add values to settings file client_ip\nport\npasscode\ninterval\npipe\nwebport
            f.write(client[0]+':'+client[1]+':'+client[2]+':'+client[3]+':'+BUFFER_SIZE+':'+webService) 
        os.system('docker run -dtv '+contSettingsFolder+':/smart/settings -p '+client[1]+ ':' + client[1]+ ' -p '+webport + ':' + webport + ' --name hp-'+client[1]+ ' sanoopsadique/smart:latest python3 /smart/hpCServer.py hp-'+client[1]) 
        print(' : Success')
        deployedContainers.append('hp-'+client[1])
        webport = str(int(client[1])+1000)
        writeWeb('Honeypot server container for client at '+client[0]+ ' started. <a href=\"hp\" onmouseover=\"javascript:event.target.port='+webport+'\" target=_blank> Click here to view status</a>\n')
        
    print('starting web service.')
    writeWeb('Honeypot container(s) deloyment complete\n')
                
    time.sleep(2)
    print('Web service started. Visit \"http://localhost:'+webService+'\" to view web page or create request')
    writeWeb('Listening for RPC:')
    
    webServer = HTTPServer(('', int(webService)), MyServer)
    
    try:
        webServer.serve_forever()

       
    except KeyboardInterrupt:
        print('Exit request by user. Stopping containers')
        writeWeb('Exit request by user. Stopping containers')
        for item in deployedContainers:
            os.system('docker stop '+item)
            os.system('docker rm '+item)
        webServer.server_close()
        print('Server stopped') 
    
    except Exception as e:
        print('Script error: '+ str(e))
        for item in deployedContainers:
            os.system('docker stop '+item)
            os.system('docker rm '+item)
            exit(0)    
    