from variables import *
from time import time
import os

# SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL


# web robot to index files
# searches for files after each set time interval 
# and creates search images of new documents

# this does not use the database context, 
# it only works with the specified list and directory, 
# the app itself must save the data that the crawler generated.

class WebСrawler:

    def __init__(self):
        self.__documets_from_db = list()
        self.documets_found_in_directory = list()
        self.last_start = ""

    def setDocumentsFromDB(self, documets_from_db):
        self.__documets_from_db = documets_from_db
    
    def start(self):
        # last_start is not empty and less time has passed than it set
        if self.last_start != "" and (time() - self.last_start) < CRAWLER_TIMESPAN_SEC:
            return 
            
        self.__findDocumentsInDirectory()
        self.__checkFoundDocuments()
        self.__convertNewDocumentsToDatabaseFormat()
        # self.__addDocumentsToDatabase()
        # self.__deleteDocumentsFromDatabase()
        
        self.last_start = time()

    
    def __findDocumentsInDirectory(self):
        current_path: str = os.path.join(os.getcwd(), DOCUMENTS_DIRECTORY_URL)
        
        for filename in os.listdir(current_path):
            filepath: str = os.path.join(current_path, filename)
            # checking if it is a file
            if os.path.isfile(filepath):
                filepath_for_db: str = os.path.join(DOCUMENTS_DIRECTORY_URL, filename)
                self.documets_found_in_directory.append(filepath_for_db)
                
                
    def __checkFoundDocuments(self):
        documets_from_db_set = set(item[0] for item in self.__documets_from_db)
        documets_found_in_directory_set = set(self.documets_found_in_directory)

        documents_to_add = documets_found_in_directory_set.difference(documets_from_db_set)
        documents_to_delete = documets_from_db_set.difference(documets_found_in_directory_set)

        print(f"delete: {documents_to_delete}")
        print(f"add: {documents_to_add}")
        
    def __convertNewDocumentsToDatabaseFormat(self):
        
        # ### need class for docs analize
        # finding words in text, need russian (+parse html)
        # create common file for database with words
        # find words in doc with this class, calculate data for vector search
        # ### in this class
        # get from analizer info about doc
        # create json file search_image_document_id
        # add json in search_image_document/temp/ directory
        # add document in temp_converted_list_of_new_documents
        # create record in needed format about doc for documents table
        pass
    
    def addDocumentsToDatabase(self, database_cursor): pass
        # make transaction for table record and file 
        # add new files 
 
    def deleteDocumentsFromDatabase(self, database_cursor): pass
        # delete old files from database
    