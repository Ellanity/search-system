from variables import *

import json


class Searcher:
    def __init__(self):
        self.__init_system_variables__()
        self.__documents_to_return = [
            "documents/doc1.html",
            "documents/doc3.html"
        ]
        
    def __init_system_variables__(self):
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        if not SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL: 
            raise Exception("Can not find variable SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL")
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        
        self.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
    def search(self, request_content) -> dict:
        return json.dumps({"urls": self.__documents_to_return}, indent=4)
        
    