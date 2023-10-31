from variables import *

import http.server
import socketserver
import urllib.parse

import json
import requests
 

class subclientApp:
    def __init__(self): 
        self.__servers = {}
        self.__loadServers()
    
    def __loadServers(self):
        for server in SERVERS.keys():
            self.__servers[server] = SERVERS[server]
            
    def search(self, request):
        responses = []
        for server in self.__servers.keys():
            try:
                server_address = str(self.__servers[server]["host"]) + ":" + str(self.__servers[server]["port"])
                request_url = "http://" + server_address + "/search?request_content=" + "\"" + request + "\"" 
                    
                response = requests.get(url = request_url).json()
                # add response from every server to common responses
                for document in response:
                    # set server url for every found document
                    document["server"] = server_address
                    responses.append(document)
                
            except Exception as ex: 
                print(ex)
        
        return json.dumps(sorted(responses, key=lambda document: document['similarity'], reverse=True), indent=4)
        # return json.dumps(responses, indent=4)
    

class SearchHandler(http.server.SimpleHTTPRequestHandler):
    
    def __init__(self, *args, app=None, **kwargs):
        self.__app = app
        super().__init__(*args, directory=WORKING_DIRECTORY, **kwargs)
    
    def do_GET(self):
        # search api endpoint
        if self.path.startswith("/search?request_content="):
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            if "request_content" in query_params:
                request_content = query_params["request_content"][0]
                result = self.perform_search(request_content)
                # everything is bad
                if result == "" or result == None:
                    self.send_error(503, "Service Unavailable")
                # everything ok
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(result.encode("utf-8"))
            else:
                self.send_error(400, "Bad Request")
                
        elif self.path.startswith(f"/{SITE_FILES_DIRECTORY_URL}/"):
            super().do_GET()
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        super().do_POST()
        
    def perform_search(self, request_content):
        return self.__app.search(request_content)


# Create an HTTP server for handling search requests
mainApp = subclientApp()
search_server = socketserver.TCPServer(SERVER_ADDRESS, lambda *args, **kwargs: SearchHandler(*args, app=mainApp, **kwargs))

if __name__ == "__main__":
    try:
        search_server.serve_forever()
    finally:
        search_server.shutdown()
