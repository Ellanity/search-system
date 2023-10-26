import sqlite3
import os
from variables import *
 

class Database:

    def __init__(self, **kwargs):
        # work variables
        self.__connection = None
        
        self._cursor = None
        self._db_instructions = dict()
        
        # start database here
        self.__loadDBInstructions()
        self.__start()
        
    def __del__(self, **kwargs):
        # stop database here
        self.__stop()
            
    # Database connection and cursor creation
    def __start(self):
        self.__connection = self.__connect(DATABASE_URL)
        self._cursor = self.__connection.cursor()
    
    # Save db state and close connection
    def __stop(self):
        self.__connection.commit()
        self.__connection.close()
    
    # Here you can change the database type
    # if you do, make sure you also changed
    # the instructions in db_instructions
    def __connect(self, database_name):
        return sqlite3.connect(database_name)
        
    def __loadDBInstructions(self) -> None:
        # we run through all the files in the directory
        current_path: str = os.path.join(os.getcwd(), DB_INSTRUCTIONS_DIRECTORY_URL)
        for filename in os.listdir(current_path):
            filepath: str = os.path.join(current_path, filename)
            # checking if it is a file
            if os.path.isfile(filepath):
                with open(filepath, "r") as file:
                    self._db_instructions[filename.split('.')[0]] = file.read()
                    
    def _excuteStandardInstruction(self, instruction_name):
        try:
            return self._cursor.execute(self._db_instructions.get(instruction_name)).fetchall()
        except Exception as ex:
            print("Instruction can not be run: ", ex)
        return None
            
    def _excuteExternalInstruction(self, instruction):
        try:
            return self._cursor.execute(instruction).fetchall()
        except Exception as ex:
            print("Instruction can not be run: ", ex)
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
    
    
    """
    # its not safe, but if you need it, you can uncomment it
    def execute(self, instruction):
        return self._excuteExternalInstruction(instruction)
    """