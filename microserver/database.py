import sqlite3
import os
from variables import *
from string import Formatter


class Database:

    def __init__(self, **kwargs):
        # work variables
        self.__connection = None
        
        self._cursor = None
        self._db_instructions = dict()
        
        # start database here
        self.__loadDBInstructions()
        
        # self.__start()
        
    def __init_system_variables__(self):
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        if not DATABASE_URL: 
            raise Exception("Can not find variable DATABASE_URL")
        if not DB_INSTRUCTIONS_DIRECTORY_URL: 
            raise Exception("Can not find variable DB_INSTRUCTIONS_DIRECTORY_URL")
        
    def __del__(self, **kwargs):
        # stop database here
        self.__stop()
            
    # Database connection and cursor creation
    def __start(self):
        working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        current_path_db: str = os.path.join(working_directory, DATABASE_URL)
    
        self.__connection = self.__connect(current_path_db)
        self._cursor = self.__connection.cursor()
        
    # Save db state and close connection
    def __stop(self):
        try:
            self.__connection.commit()
        except Exception as ex:
            pass
        
        try:
            self.__connection.close()
        except Exception as ex:
            pass
        
    # Here you can change the database type
    # if you do, make sure you also changed
    # the instructions in db_instructions
    def __connect(self, database_name):
        return sqlite3.connect(database_name)
        
    def __loadDBInstructions(self) -> None:
        # we run through all the files in the directory
        
        working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        current_path: str = os.path.join(working_directory, DB_INSTRUCTIONS_DIRECTORY_URL)
        for filename in os.listdir(current_path):
            filepath: str = os.path.join(current_path, filename)
            # checking if it is a file
            if os.path.isfile(filepath):
                with open(filepath, "r") as file:
                    self._db_instructions[filename.split('.')[0]] = file.read()
                    
    # formatter for instructions
    class UnseenFormatter(Formatter):
        def get_value(self, key, args, kwds):
            if isinstance(key, str):
                try:
                    return kwds[key]
                except KeyError:
                    return key
            else:
                return Formatter.get_value(key, args, kwds)
        
    # check standart instructions and set kwargs to them
    def _excuteStandardInstruction(self, instruction_name, **kwargs):
        try:
            self.__start()
            if kwargs:
                fmt = self.UnseenFormatter()
                instruction = fmt.format(self._db_instructions.get(instruction_name), **kwargs)
                # print(instruction)
                response = self._cursor.execute(instruction)
                self.__connection.commit()
                
                response = response.fetchall()
                self.__stop()
                return response
            else:
                response = self._cursor.execute(self._db_instructions.get(instruction_name))
                self.__connection.commit()
                
                response = response.fetchall()
                self.__stop()
                return response
        except Exception as ex:
            print("Instruction can not be run: ", ex)
        
        self.__stop()
        return None
            
    def _excuteExternalInstruction(self, instruction, **kwargs):
        try:
            self.__start()
            response = self._cursor.execute(instruction)
            self.__connection.commit()
            
            response = response.fetchall()
            self.__stop()
            return response
        except Exception as ex:
            print("Instruction can not be run: ", ex)
            
        self.__stop()
        return None

class DatabaseDocuments(Database):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.get_document_all_last = []
        
    def __del__(self, **kwargs):
        super().__del__(**kwargs)
        
    ### Methods open to external use
    
    def getDocumentAll(self):
        self.get_document_all_last = self._excuteStandardInstruction("getDocumentAll")
        return self.get_document_all_last
    
    def getTables(self):
        return self._excuteStandardInstruction("getTables")
        
    def addDocument(self, url_document, search_image_document, last_update_document):
        # print (f"--- add ---\nurl_document: {url_document} \nsearch_image_document: {search_image_document} \nlast_update_document: {last_update_document}")
        return self._excuteStandardInstruction(
            instruction_name="addDocument", 
            url_document=f'"{url_document}"', 
            search_image_document=f'"{search_image_document}"', 
            last_update_document=f'"{last_update_document}"')
            
    def updateDocument(self, url_document, search_image_document, last_update_document):
        # print (f"--- update ---\nurl_document: {url_document} \nsearch_image_document: {search_image_document} \nlast_update_document: {last_update_document}")
        return self._excuteStandardInstruction(
            instruction_name="updateDocument", 
            url_document=f'"{url_document}"', 
            search_image_document=f'"{search_image_document}"', 
            last_update_document=f'"{last_update_document}"')
        
    def deleteDocument(self, url_document):
        # print (f"--- delete ---\nurl_document: {url_document}")
        return self._excuteStandardInstruction(
            instruction_name="deleteDocument", 
            url_document=f'"{url_document}"')
        
    
    """
    # its not safe, but if you need it, you can uncomment it
    def execute(self, instruction):
        return self._excuteExternalInstruction(instruction)
    """