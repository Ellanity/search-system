from database import DatabaseDocuments
from variables import *

import json
import re
import os
from math import sqrt


class Searcher:
    def __init__(self):
        self.__init_system_variables__()
        self.__database = DatabaseDocuments() 
        # documents data
        self.documets_from_db = []
        self.documets_search_images = {}

    def __reinit_variables__(self):
        self.documets_from_db = []
        self.documets_search_images = {}
        
    def __init_system_variables__(self):
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        if not SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL: 
            raise Exception("Can not find variable SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL")
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_TEXT")
        if not SERVER_DICTIONARY_DIRECTORY_URL: 
            raise Exception("Can not find variable SERVER_DICTIONARY_DIRECTORY_URL")
        
        self.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
    
    def __findVectorsSimilarWithRequest(self, vector_request, vectors_documents):
        similarities_list = []
        
        for document in vectors_documents.keys():
            similarity = self.__calculateSimilarityOfVectors(vector_request, vectors_documents[document])
            if similarity != 0:
                similarities_list.append({
                    "document": document, 
                    "similarity": similarity,
                    "weights": vectors_documents[document],
                    "language_defined": self.documets_search_images[document]["language_defined"]
                    })
        
        return similarities_list
    
    # https://ru.wikipedia.org/wiki/%D0%92%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F_%D0%BC%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C
    # https://fkn.ktu10.com/?q=node/9828
    def __calculateSimilarityOfVectors(self, vector_request, vector_document):
        lexems = vector_request.keys()
        # scalar
        def scalarFunc(vector_request, vector_document, lexems):
            answer_scalar = 0 
            for lexem in lexems:
                answer_scalar += vector_request[lexem] * vector_document[lexem]
            return answer_scalar
        # module
        def moduleFunc(vector, lexems):
            answer_module = 0
            for lexem in lexems:
                answer_module += vector[lexem] ** 2
            return sqrt(answer_module)
        # cos
        module = (moduleFunc(vector_request, lexems) * moduleFunc(vector_document, lexems))
        if module == 0:
            return 0
        similarity = scalarFunc(vector_request, vector_document, lexems) / module
        return similarity
    
    def __vectorsSearchImagesDocuments(self, vector_request) -> dict:
        # get documents from database
        self.documets_from_db = self.__database.getDocumentAll()
        
        if self.documets_from_db == []:
            return
            
        vectors_documents = {}
        for document in self.documets_from_db:
            # save image in search images of documents
            search_image_document = self.__getSearchImageDocument(document_url=document[0], temp=False)
            self.documets_search_images[document[0]] = search_image_document
            
            # save vector in vectors of documents
            vector_document = self.__vectorSearchImageDocument(vector_request, search_image_document)
            vectors_documents[document[0]] = vector_document
        
        return vectors_documents
    
    def __getSearchImageDocument(self, document_url, temp=False):
        search_image_document = {}
        try:
            if temp:
                search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp", document_url + ".json")
            else:
                search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, document_url + ".json")
                
            with open(search_image_document_path, "r", encoding="utf-8") as temp_search_image_document_file:
                json_content = temp_search_image_document_file.read()
                search_image_document = json.loads(json_content)
        except Exception as ex:
            print(f"No temp search image for {document_url} | {ex}")
        
        return search_image_document    
    
    def __vectorSearchImageDocument(self, vector_request, search_image_document) -> dict:
        # Here we can make vectors with size of all server dictionary
        # or with size of search request contetn
        
        list_of_lexems = vector_request.keys()
        
        vector_document = {
            lexem: 0 for lexem in list_of_lexems
        }
        
        for lexem in list_of_lexems:
            lexem_data = search_image_document["dict_of_lexems"].get(lexem)
            if lexem_data:
                vector_document[lexem] = search_image_document["dict_of_lexems"][lexem]["weight"]
        
        return vector_document
        
    def __vectorSearchImageRequest(self, request_content):             
        # split text and getting words with counts        
        # list_of_lexems = re.split(DELIMETERS_OF_TEXT, text_from_document, flags=re.IGNORECASE)
        # list_of_lexems = [lexem for lexem in list_of_lexems if lexem != ""]
        list_of_lexems = re.sub(r'(?:(?!\u0301)[\W\d_])+', ' ', ("".join(character for character in request_content if character in ALLOWED_DICTIONARY)))
        list_of_lexems = [lexem for lexem in list_of_lexems.split(" ") if lexem != ""]
    
        vector_request = {
            lexem: 1 for lexem in list_of_lexems
        }
        
        return vector_request        
    
    def search(self, request_content) -> str:
        
        try:
            self.__reinit_variables__()

            vector_request = self.__vectorSearchImageRequest(request_content)
            vectors_documents = self.__vectorsSearchImagesDocuments(vector_request)
            response = self.__findVectorsSimilarWithRequest(vector_request, vectors_documents)
        
            return json.dumps(response, indent=4)
        except Exception as ex: 
            print("Searcher error: ", ex)
            return ""