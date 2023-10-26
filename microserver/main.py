from database import DatabaseDocuments
from crawler import WebСrawler
from variables import HTTP_PORT

# import json
# import asyncio

class App:
    
    def __init__(self):
        self.database = DatabaseDocuments()
        
        # crawler
        self.crawler = WebСrawler()
        self.crawler_in_work = False
                
    def run(self):
        print(self.database.getDocumentAll())
        self.__crawlerRun()

    def __del__(self):
        print("programm finished")
        
    def __crawlerRun(self):
        if self.crawler_in_work:
           return
        
        self.database.getDocumentAll()
        self.crawler.setDocumentsFromDB(self.database.get_document_all_last)
        self.crawler.start()

if __name__ == "__main__":
    app = App()
    app.run()

        
"""
import http.server
import socketserver

class HttpHandler(BaseHTTPRequestHandler):

    def __init__(self):
        self.app = App()

    def do_GET(self):
        
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        json_dumped: str = json.dumps({"urls":urls}, indent = 4)
        
        self.wfile.write(json_dumped.encode())


def run():
    server_class=HTTPServer
    handler_class=HttpHandler
    server_address = ('', HTTP_PORT)
    
    httpd = server_class(server_address, handler_class)
    
    try:
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        httpd.server_close()
        
run()
"""