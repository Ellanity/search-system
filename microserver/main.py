# custom modules
from variables import SERVER_ADDRESS, CRAWLER_TIMESPAN_SEC, WORKING_DIRECTORY, DOCUMENTS_DIRECTORY_URL  
from crawler import WebСrawler
from searcher import Searcher
# standard modules
import http.server
import urllib.parse
import asyncio


# Main app class
class App:
    
    def __init__(self):
        self.crawler = WebСrawler()
        self.searcher = Searcher()
                
    ### command to start Crawler
    def crawlerRun(self) -> None:
        if self.crawler.current_state == "wait":
            self.crawler.start()

    ### command to start Searcher 
    def searcherRun(self, request_content) -> str:
        result = ""
        # check if crawler doesn't touch database now
        if self.crawler.current_state == "wait":
            result = self.searcher.search(request_content)
        return result

# Custom handler class (for the search and other requests)
class SearchHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, app=None, **kwargs):
        self.__app = app
        super().__init__(*args, directory=WORKING_DIRECTORY, **kwargs)
    
    # GET method
    def do_GET(self):

        ### search api endpoint
        if self.path.startswith("/search?request_content="):

            # get url path and params
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            
            # check if search request_content (string to search) is not empty
            if "request_content" in query_params:
                request_content = query_params["request_content"][0]
                result = self.perform_search(request_content)
                
                # check that the Searcher engine will return a string answer
                if result == None or type(result) != str or len(result) <= 0 or result == "":
                    self.send_error(503, "Service Unavailable")

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(result.encode("utf-8"))
            # can not parse request content
            else:
                self.send_error(400, "Bad Request")
        
        ### documents api endpoint
        elif self.path.startswith(f"/{DOCUMENTS_DIRECTORY_URL}/"):
            super().do_GET()    
           
        else:
            self.send_error(404, "Not found") 
        
        """
        ### favicon api endpoint
        elif self.path == "/favicon.ico":
            self.send_response(200)
            self.send_header("Content-type", "image/x-icon")
            self.end_headers()
            self.wfile.write(load_binary("/favicon.icon"))
        """

    # Searcher call:
    def perform_search(self, request_content):
        return self.__app.searcherRun(request_content.lower())


# Define a crawler async coroutine that runs every 
# time period specified in the variables (default 10 mins)
async def runCrawler(app: App):
    while True:
        print("Crawler is running...")
        app.crawlerRun()
        print("Crawler done...")
        # Wait for timespan
        await asyncio.sleep(CRAWLER_TIMESPAN_SEC)  

mainApp = App()

# ### async HTTP server logic ### #
    
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

# Run http server 
if __name__ == "__main__":
    asyncio.run(main())