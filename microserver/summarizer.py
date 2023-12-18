# custom lib of global variables 
from variables import *

# all definers must get already cleared text 
from text_processor import TextProcessor

# work with files
import os   
import stat
import shutil
import json
import codecs

class Summarizer(object):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_system_variables__()

    @staticmethod
    def __init_system_variables__():
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        
        # for text handling
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_DOCUMENT")

        Summarizer.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        Summarizer._paths = {
            "DOCUMENTS_DIRECTORY_URL": os.path.join(Summarizer.__working_directory, DOCUMENTS_DIRECTORY_URL)
        }

        for _, path in Summarizer._paths.items():
            is_exist = os.path.exists(path)
            if not is_exist:
                os.makedirs(path)

# With sentence extraction
class SummarizerClassicSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @staticmethod   
        def summarize(text: str) -> list:
            sentenses = []
            sentenses = text.split(".")[:10]
            return sentenses

class SummarizerKeywordsSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        @staticmethod   
        def summarize(text: str) -> list:
            sentenses = []
            sentenses = text.split(" ")[:10]
            return sentenses

class SummarizerMLSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        
        @staticmethod   
        def summarize(text: str) -> list:
            sentenses = []
            sentenses = text.split(" ")[:10]
            return sentenses

