from database import DatabaseDocuments
from crawler import WebСrawler
from variables import HTTP_PORT


import asyncio

class App:
    
    def __init__(self):
        self.database = DatabaseDocuments()
        self.crawler = WebСrawler()
        
    def crawlerRun(self):
        if self.crawler.current_state == "wait":
            self.crawler.start(self.database)
        
if __name__ == "__main__":
    app = App()
    app.crawlerRun()

"""        
from http.server import BaseHTTPRequestHandler, HTTPServer


class HttpHandler(BaseHTTPRequestHandler):

    def __init__(self, **kwargs):
        super().__init__()
        self.app = App()

    def do_GET(self):
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        json_dumped: str = json.dumps({"urls":"lol"}, indent = 4)
        
        self.wfile.write(json_dumped.encode())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    
    server_address = ('', HTTP_PORT)
    httpd = server_class(server_address, handler_class)
    
    try:
        httpd.serve_forever()    
    except KeyboardInterrupt:
        httpd.server_close()

run()
"""