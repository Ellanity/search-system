from database import DatabaseDocuments
from crawler import WebСrawler

from variables import SERVER_ADDRESS, CRAWLER_TIMESPAN_SEC, WORKING_DIRECTORY, DOCUMENTS_DIRECTORY_URL


class App:
    
    def __init__(self):
        self.database = DatabaseDocuments()
        self.crawler = WebСrawler()
        
    def run(self):
        self.crawlerRun()
        
    def crawlerRun(self):
        if self.crawler.current_state == "wait":
            self.crawler.start(self.database)

"""        
if __name__ == "__main__":
    app = App()
    app.crawlerRun()

"""        

import http.server
import socketserver
import urllib.parse
import asyncio
import threading

# Define the custom handler for the search request
# class SearchHandler(http.server.BaseHTTPRequestHandler):
class SearchHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, app=None, **kwargs):
        self.__app = app
        super().__init__(*args, directory=WORKING_DIRECTORY, **kwargs)
    
    def do_GET(self):
        # Search
        if self.path.startswith('/search?request_content='):
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            if 'request_content' in query_params:
                search_text = query_params['request_content'][0]
                result = self.perform_search(search_text)
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(result.encode('utf-8'))
            else:
                self.send_error(400, 'Bad Request')
        # Documents
        elif self.path.startswith(f'/{DOCUMENTS_DIRECTORY_URL}/'):
            super().do_GET()    
        else:
            self.send_error(400, 'Bad Request')

    def perform_search(self, search_text):
        print(self.__app.crawler.current_state)
        # Implement your search logic here, for example:
        # search_result = search_function(search_text)
        search_result = f"Searching for: {search_text}\nThis is a placeholder for search results."
        return search_result

# Define a crawler coroutine that runs every 10 minutes
async def runCrawler(app: App):
    while True:
        # Replace this with your crawler logic
        print("Crawler is running...")
        app.run()
        print("Crawler done...")
        await asyncio.sleep(CRAWLER_TIMESPAN_SEC)  # Wait for timespan 
    

def main():
    mainApp = App()
    # Create an HTTP server for handling search requests
    search_server = socketserver.TCPServer(SERVER_ADDRESS, lambda *args, **kwargs: SearchHandler(*args, app=mainApp, **kwargs))
    # Serving checkpoint 
    print(f'Serving on {SERVER_ADDRESS}')
    
    try:
        # Start the crawler as an asynchronous background task
        # loop = asyncio.get_event_loop()
        # asyncio.run(runCrawler(mainApp))
        # Start serving both file requests and search requests
        search_server.serve_forever()
    except KeyboardInterrupt:
        # loop.stop()
        search_server.shutdown()
    """

    try:
        # Create a thread for the crawler and start it
        crawler_thread = threading.Thread(target=asyncio.run, args=(runCrawler(mainApp),))
        crawler_thread.start()

        # Start the server
        search_server.serve_forever()
    except KeyboardInterrupt:
        search_server.shutdown()
    """
    
if __name__ == "__main__":
    main()
