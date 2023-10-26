from variables import *

from time import time, strptime, mktime
import os
import re
import codecs
import json


# web robot to index files
# searches for files after each set time interval 
# and creates search images of new documents

# this does not use the database context, 
# it only works with the specified list and directory, 
# the app itself must save the data that the crawler generated.


class WebСrawler:

    def __init__(self):
        # documents
        self.__documets_from_db = []
        
        self.__documets_found_in_directory = []
        
        self.__documents_urls_to_add = []
        self.__documents_urls_to_readd = []
        self.__documents_urls_to_delete = []
        
        # server dict
        self.__written_in_dictionary = []
        
        # system
        self.__last_start = ""
        self.__working_directory = ""
        
        # inits
        self.__init_system_variables__()
        self.__init_server_dictionary__()
        
    def __init_system_variables__(self):
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        if not DOCUMENTS_DIRECTORY_URL: 
            raise Exception("Can not find variable DOCUMENTS_DIRECTORY_URL")
        if not SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL: 
            raise Exception("Can not find variable SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL")
        if not TIME_FORMAT: 
            raise Exception("Can not find variable TIME_FORMAT")
        if not CRAWLER_DOCUMENTS_READD_TIMESPAN_SEC: 
            raise Exception("Can not find variable CRAWLER_DOCUMENTS_READD_TIMESPAN_SEC")
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not CRAWLER_TIMESPAN_SEC: 
            raise Exception("Can not find variable CRAWLER_TIMESPAN_SEC")
        if not SERVER_DICTIONARY_DIRECTORY_URL: 
            raise Exception("Can not find variable SERVER_DICTIONARY_DIRECTORY_URL")

        self.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        paths = [
            os.path.join(self.__working_directory, DOCUMENTS_DIRECTORY_URL),
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL),
            os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL),
            os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, DOCUMENTS_DIRECTORY_URL),
            os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp"),
            os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp", DOCUMENTS_DIRECTORY_URL)
        ]
        for path in paths:
            is_exist = os.path.exists(path)
            if not is_exist:
                os.makedirs(path)
                
    def __init_server_dictionary__(self):
        # files of dictionary parts (one part is one character in allowed_dictionary)
        paths = [
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json") for char in ALLOWED_DICTIONARY
        ]
        for path in paths:
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as server_dictionary_part_file:
                    json.dump({}, server_dictionary_part_file)
        
        # common info file
        common_info_path = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, "common_info.json")        
        if not os.path.exists(common_info_path):
            with open(common_info_path, "w", encoding="utf-8") as server_dictionary_common_info_file:
                json.dump({"count_of_words": 0}, server_dictionary_common_info_file)
        
    def start(self, documets_from_db):
        self.__documets_from_db = documets_from_db
        # if last_start is not empty and less time has passed than it set
        if self.__last_start != "" and (time() - self.__last_start) < CRAWLER_TIMESPAN_SEC:
            return 
        
        # work with docs 
        self.__documentCheck()
        self.__createSearchImagesOfDocuments()
        self.__indexingServerDictionary()
        
        # restart timer
        self.__last_start = time()
        
    # ### WORK WITH DOCUMENTS ### #
    
    # main function that work with documents urls
    def __documentCheck(self):
        self.__findDocumentsInDirectory()
        self.__classificationOfFoundDocuments()
        
    # find all available docs in directory
    def __findDocumentsInDirectory(self):
        current_path: str = os.path.join(self.__working_directory, DOCUMENTS_DIRECTORY_URL)
        for filename in os.listdir(current_path):
            filepath: str = os.path.join(current_path, filename)
            if os.path.isfile(filepath):
                filepath_for_db: str = os.path.join(DOCUMENTS_DIRECTORY_URL, filename)
                self.__documets_found_in_directory.append(filepath_for_db)
                
    # classificate documents to add, readd or delete
    def __classificationOfFoundDocuments(self):
        if self.__documets_from_db != []:
            documets_from_db_set = set(item[0] for item in self.__documets_from_db)
        else:
            documets_from_db_set = set()
            
        documets_found_in_directory_set = set(self.__documets_found_in_directory)
        print(f"found: {documets_found_in_directory_set}")

        # documents to add
        self.__documents_urls_to_add    = documets_found_in_directory_set.difference(documets_from_db_set)
        # documents to delete
        self.__documents_urls_to_delete = documets_from_db_set.difference(documets_found_in_directory_set)

        # documents to readd
        common_documents = documets_found_in_directory_set.intersection(documets_from_db_set)
        for document in self.__documets_from_db:
            if document[0] in common_documents:
                document_time = mktime(strptime(document[2], TIME_FORMAT))
                if time() - document_time > CRAWLER_DOCUMENTS_READD_TIMESPAN_SEC:
                    self.__documents_urls_to_readd.append(document[0])

        print(f"add: {self.__documents_urls_to_add}")
        print(f"readd: {self.__documents_urls_to_readd}")
        print(f"delete: {self.__documents_urls_to_delete}")
            
    # ### WORK WITH SEARCG IMAGES ### #
    
    def __createSearchImagesOfDocuments(self):
        for document in self.__documents_urls_to_add:
            self.__createSearchImageDocumentTemp(document)
            
        for document in self.__documents_urls_to_readd:
            self.__createSearchImageDocumentTemp(document)
    
    def __createSearchImageDocumentTemp(self, document_url):
        
        # get raw text from file
        html_document_with_tags=""
        current_path: str = os.path.join(self.__working_directory, document_url)

        if os.path.isfile(current_path):
            with codecs.open(current_path, "r", encoding="utf-8") as file:
                html_document_with_tags = file.read()

        # remove tags and newlines from raw text
        pattern = re.compile('<.*?>')
        text_from_document = self.__keepCharactersInStringWithRegex(
            input_string=re.sub(pattern, '', html_document_with_tags).replace('\n', ' '),
            reference_string=ALLOWED_DICTIONARY)
            
        # split text by spaces and getting words with counts
        list_of_lexems = text_from_document.split(' ')
        dict_of_lexems = {item: {"count": list_of_lexems.count(item), "weight": 0} for item in list_of_lexems}
        dict_of_lexems.pop("")
        
        # print(dict_of_lexems)
        print(f"dict_of_lexems created for {document_url}")

        # create json and write dictionary there
        temp_search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp", document_url + ".json")
        with open(temp_search_image_document_path, "w", encoding="utf-8") as search_image_file:
            json.dump(dict_of_lexems, search_image_file)

    def __keepCharactersInStringWithRegex(self, input_string, reference_string):
        pattern = f"[^{reference_string.lower()}]"
        filtered_string = re.sub(pattern, "", input_string.lower())
        return filtered_string.lower()
        
    # ### WORK WITH SEVER DICTIONARY ### #
    
    def __indexingServerDictionary(self):
        for document in self.__documents_urls_to_add:
            self.__writeLexemsFromTempSearchImageInServerDictionary(document)
            
        # for document in self.__documents_urls_to_readd:
        #     self.__deleteLexemsFromSearchImageFromServerDictionary(document)
        #     self.__writeLexemsFromTempSearchImageInServerDictionary(document)
            
        # for document in self.__documents_urls_to_delete:
        #     self.__deleteLexemsFromSearchImageFromServerDictionary(document)
    
        self.__recalculateInverseFrequencyOfLexemsInServerDictionary()

    def __writeLexemsFromTempSearchImageInServerDictionary(self, document_url):
        # check that document not added to dict before
        if document_url in self.__written_in_dictionary:
            return
        
        # get document with common info
        
        # common info file
        common_info = {}
        common_info_path = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, "common_info.json")        
        with open(common_info_path, "r", encoding="utf-8") as server_dictionary_common_info_file:
            json_content = server_dictionary_common_info_file.read()
            common_info = json.loads(json_content)
        
        # get document search image
        search_image_document = ""
        temp_search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp", document_url + ".json")
        with open(temp_search_image_document_path, "r", encoding="utf-8") as temp_search_image_document_file:
            json_content = temp_search_image_document_file.read()
            search_image_document = json.loads(json_content)
        
        # load full dictionary
        server_dictionary_parts = {} # TAKES REALLY A LOT OF RAM, but this solution faseter then other (load in query for ex)
        char_paths = [
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json") for char in ALLOWED_DICTIONARY
        ]
        for char_path in char_paths:
            with open(char_path, "r", encoding="utf-8") as server_dictionary_part_file:
                json_content = server_dictionary_part_file.read()
                server_dictionary_parts[char_path] = json.loads(json_content)
        
        # for every lexem in image check needed part of dictionary
        for lexem in search_image_document.keys():
            # getting part of dict by first char
            char = lexem[0]
            current_server_dictionary_part = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
            # make structure for this word
            if lexem in server_dictionary_parts[current_server_dictionary_part]:
                if lexem is " " or lexem is "":
                    continue
                server_dictionary_parts[current_server_dictionary_part][lexem]["count"] += search_image_document[lexem]["count"]
            else:
                server_dictionary_parts[current_server_dictionary_part][lexem] = {"count": search_image_document[lexem]["count"], "inverse_frequency": 0.0}
                
            common_info["count_of_words"] += search_image_document[lexem]["count"]
        
        # save full dictionary
        for char_path in char_paths:
            with open(char_path, "w", encoding="utf-8") as server_dictionary_part_file:
                json.dump(server_dictionary_parts[char_path], server_dictionary_part_file)
                
        # save common info file
        with open(common_info_path, "w", encoding="utf-8") as common_info_file:
            json.dump(common_info, common_info_file)
            
        
        # mark, that file added to dictionary
        self.__written_in_dictionary.append(document_url)
        
    # TODO
    def __deleteLexemsFromSearchImageFromServerDictionary(self, document_url):
        temp_search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, document_url)
        
    def __recalculateInverseFrequencyOfLexemsInServerDictionary(self): pass
    