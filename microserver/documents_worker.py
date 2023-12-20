from variables import *

# work with files
import os   
import stat
import shutil

import json
import codecs


class DocumentsWorker(object):
        
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

        DocumentsWorker.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        DocumentsWorker._paths = {
            "DOCUMENTS_DIRECTORY_URL": 
                os.path.join(DocumentsWorker.__working_directory, DOCUMENTS_DIRECTORY_URL)
        }

        for _, path in DocumentsWorker._paths.items():
            is_exist = os.path.exists(path)
            if not is_exist:
                os.makedirs(path)

    # just find documents in directory, return array of pathes 
    # in path last part is filename 
    @staticmethod
    def getDocumentsPathesInDirectory(directory_url: str) -> list:
        docpaths = []
        for filename in os.listdir(directory_url):
            filepath: str = os.path.join(directory_url, filename)
            if os.path.isfile(filepath):
                docpaths.append(filepath)
        return docpaths
    
    # Retruns info about directory existing (remove if exists) 
    @staticmethod
    def removeDirectoryByPath(file_path: str) -> bool:
        if not os.path.exists(file_path):
            return True
        
        # try to remove
        try:
            def onRmError(func, path, exc_info):
                # path contains the path of the file that couldn't be removed
                # let's just assume that it's read-only and unlink it.
                os.chmod(path, stat.S_IWRITE)
                os.unlink(path)
                os.remove(path)

            shutil.rmtree(file_path, onerror = onRmError)    
            
        except Exception as ex:
            print(ex)

        if not os.path.exists(file_path):
            return True
        return False
    
    # Retruns info about directory existing (create if not exists) 
    @staticmethod
    def createDirectoryByPath(file_path: str) -> bool:
        if os.path.exists(file_path):
            return True
        
        # try to create
        try:
            if not os.path.exists(file_path):
                os.makedirs(file_path, stat.S_IWRITE)  
        except Exception as ex:
            print(ex)

        if os.path.exists(file_path):
            return True
        return False