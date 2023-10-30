# from database import DatabaseDocuments
from crawler import WebСrawler
from searcher import Searcher

from variables import SERVER_ADDRESS, CRAWLER_TIMESPAN_SEC, WORKING_DIRECTORY, DOCUMENTS_DIRECTORY_URL  

import http.server
import socketserver
import urllib.parse
import asyncio


class App:
    
    def __init__(self):
        # self.database = DatabaseDocuments()
        self.crawler = WebСrawler()
        self.searcher = Searcher()
                
    def crawlerRun(self):
        if self.crawler.current_state == "wait":
            self.crawler.start()
            # self.crawler.start(self.database)

    def searcherRun(self, request_content):
        result = ""
        if self.crawler.current_state == "wait":
            result = self.searcher.search(request_content)
            # result = self.searcher.search(request_content, self.database)
        return result

# Define the custom handler for the search request
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
        
        # documents api endpoint
        elif self.path.startswith(f'/{DOCUMENTS_DIRECTORY_URL}/'):
            super().do_GET()    
        else:
            self.send_error(404, "Not found")

    # search logic:
    def perform_search(self, request_content):
        return self.__app.searcherRun(request_content)
        
# Define a crawler coroutine that runs every 10 minutes
async def runCrawler(app: App):
    while True:
        # Replace this with your crawler logic
        print("Crawler is running...")
        app.crawlerRun()
        print("Crawler done...")
        await asyncio.sleep(CRAWLER_TIMESPAN_SEC)  # Wait for timespan 
    

# def main():
mainApp = App()
# Create an HTTP server for handling search requests
# search_server = socketserver.TCPServer(SERVER_ADDRESS, lambda *args, **kwargs: SearchHandler(*args, app=mainApp, **kwargs))
# Serving checkpoint 
 #print(f'Serving on {SERVER_ADDRESS}')
    
from socketserver import ThreadingMixIn, TCPServer
from concurrent.futures import ThreadPoolExecutor

# Mixin class to make TCPServer work with asyncio
class AsyncTCPServer(ThreadingMixIn, TCPServer):
    pass

# Create a ThreadPoolExecutor for running the HTTP server
executor = ThreadPoolExecutor(max_workers=1)

# Create an HTTP server instance
httpd = AsyncTCPServer(SERVER_ADDRESS, lambda *args, **kwargs: SearchHandler(*args, app=mainApp, **kwargs))

# Start the HTTP server using ThreadPoolExecutor
http_server_task = executor.submit(httpd.serve_forever)

# Start the async function in the event loop
async def main():
    await asyncio.gather(
        runCrawler(mainApp),
    )

if __name__ == "__main__":
    asyncio.run(main())