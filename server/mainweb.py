
from http.server import BaseHTTPRequestHandler, HTTPServer
import time, os, datetime
import socket, sys


hostName = ""
serverPort = int(sys.argv[1])

class MyServer(BaseHTTPRequestHandler): 
    def do_GET(self):
        global service
        global refresh
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        filePath = "/etc/smart/server/web/index.html"
        with open(filePath) as f:	
            for line in f:
                self.wfile.write(bytes(line, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    
    webServer = HTTPServer((hostName, serverPort), MyServer)
    
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    