from variables import *

from time import time, strptime, mktime
import os
import re
import codecs
import json
import math


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
        
# NEED TO REWORK IT, SAVE IN JSON IN COMMON DATA
        self.__written_in_dictionary = []
        self.__deleted_from_dictionary = []
        
        # system
        self.__server_dictionary_common_info_path = ""
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
        self.__server_dictionary_common_info_path = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, "common_info.json")        
        
        if not os.path.exists(self.__server_dictionary_common_info_path):
            with open(self.__server_dictionary_common_info_path, "w", encoding="utf-8") as server_dictionary_common_info_file:
                common_info_init_data = {
                    "count_of_words": 0,
                    "count_of_documents": 0,
                }
                json.dump(common_info_init_data, server_dictionary_common_info_file)
        
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
        list_of_lexems = [item for item in list_of_lexems if item != ""]
        
        dict_of_lexems = {
            item: {
                "count": list_of_lexems.count(item), 
                "weight": 0
            } for item in list_of_lexems
        }
        
        search_image_document = {
            "count_of_words": len(list_of_lexems),
            "dict_of_lexems": dict_of_lexems
        }

        # create json and write dictionary there
        self.__setSearchImageDocument(document_url, search_image_document, temp=True)

    def __keepCharactersInStringWithRegex(self, input_string, reference_string):
        pattern = f"[^{reference_string.lower()}]"
        filtered_string = re.sub(pattern, "", input_string.lower())
        return filtered_string.lower()
        
    def __setSearchImageDocument(self, document_url, search_image_document, temp=False):
        if temp:
            search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp", document_url + ".json")
        else:
            search_image_document_path = os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, document_url + ".json")
            
        with open(search_image_document_path, "w", encoding="utf-8") as search_image_file:
            json.dump(search_image_document, search_image_file)
        
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
        
    # ### WORK WITH SEVER DICTIONARY ### #
    
    def __indexingServerDictionary(self):
        for document in self.__documents_urls_to_add:
            self.__writeLexemsFromTempSearchImageInServerDictionary(document)
            
        for document in self.__documents_urls_to_readd:
            self.__deleteLexemsFromSearchImageFromServerDictionary(document)
            self.__writeLexemsFromTempSearchImageInServerDictionary(document)
            
        for document in self.__documents_urls_to_delete:
            self.__deleteLexemsFromSearchImageFromServerDictionary(document)
    
        self.__recalculateInverseFrequencyOfLexemsInServerDictionary()
        self.__recalculateWeightOfLexemsInImages()
        
    # server dictionary common info get
    def __getServerDictionaryCommonInfo(self):
        common_info = {}        
        with open(self.__server_dictionary_common_info_path, "r", encoding="utf-8") as server_dictionary_common_info_file:
            json_content = server_dictionary_common_info_file.read()
            common_info = json.loads(json_content)
            
        return common_info
            
    # server dictionary common info set
    def __setServerDictionaryCommonInfo(self, common_info):   
        with open(self.__server_dictionary_common_info_path, "w", encoding="utf-8") as common_info_file:
            json.dump(common_info, common_info_file)
       
    # server dictionary get
    def __getServerDictionaryParts(self):
        server_dictionary_parts = {} # TAKES REALLY A LOT OF RAM, but this solution faster then other (load in query for ex)
        char_paths = [
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json") for char in ALLOWED_DICTIONARY
        ]
        for char_path in char_paths:
            with open(char_path, "r", encoding="utf-8") as server_dictionary_part_file:
                json_content = server_dictionary_part_file.read()
                server_dictionary_parts[char_path] = json.loads(json_content)
                
        return server_dictionary_parts
        
    # server dictionary set
    def __setServerDictionaryParts(self, server_dictionary_parts):   
        char_paths = [
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json") for char in ALLOWED_DICTIONARY
        ]
        for char_path in char_paths:
            with open(char_path, "w", encoding="utf-8") as server_dictionary_part_file:
                json.dump(server_dictionary_parts[char_path], server_dictionary_part_file)
        
    # write lexems in dict
    def __writeLexemsFromTempSearchImageInServerDictionary(self, document_url):
        # check that document not added to dict before
        if document_url in self.__written_in_dictionary:
            return
                
        # get temp document search image
        search_image_document = self.__getSearchImageDocument(document_url, temp=True)
        if search_image_document == {}:
            return
        
        # common info file
        common_info = self.__getServerDictionaryCommonInfo()
        
        # load full dictionary
        server_dictionary_parts = self.__getServerDictionaryParts()
        
        # for every lexem in image check needed part of dictionary
        for lexem in search_image_document["dict_of_lexems"].keys():
            # getting part of dict by first char
            char = lexem[0]
            current_server_dictionary_part = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
            # make structure for this word
            if lexem is " " or lexem is "":
                continue
            if lexem in server_dictionary_parts[current_server_dictionary_part]:
                server_dictionary_parts[current_server_dictionary_part][lexem]["count"] += search_image_document["dict_of_lexems"][lexem]["count"]
                server_dictionary_parts[current_server_dictionary_part][lexem]["documents_with_term"] += 1
            else:
                server_dictionary_parts[current_server_dictionary_part][lexem] = {
                    "count": search_image_document["dict_of_lexems"][lexem]["count"], 
                    "inverse_frequency": 0.0,
                    "documents_with_term": 1
                }
                
            common_info["count_of_words"] += search_image_document["dict_of_lexems"][lexem]["count"]
        
        common_info["count_of_documents"] += 1

        # save full dictionary
        self.__setServerDictionaryParts(server_dictionary_parts)
        
        # save common info file
        self.__setServerDictionaryCommonInfo(common_info)
        
        # mark, that file added to dictionary
        self.__written_in_dictionary.append(document_url)
        
    # delete lexems from dict
    def __deleteLexemsFromSearchImageFromServerDictionary(self, document_url):
        # check that document not already deleted from dict before
        if document_url in self.__deleted_from_dictionary:
            return
                
        # try to get document search image
        search_image_document = self.__getSearchImageDocument(document_url, temp=False)
        if search_image_document == {}:
            return
        
        # common info file
        common_info = self.__getServerDictionaryCommonInfo()
        
        # load full dictionary
        server_dictionary_parts = self.__getServerDictionaryParts()
        
        # for every lexem in image check needed part of dictionary
        for lexem in search_image_document["dict_of_lexems"].keys():
            # getting part of dict by first char
            char = lexem[0]
            current_server_dictionary_part = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
            # make structure for this word
            if lexem is " " or lexem is "":
                continue
            if lexem in server_dictionary_parts[current_server_dictionary_part]:
                server_dictionary_parts[current_server_dictionary_part][lexem]["count"] = \
                max(server_dictionary_parts[current_server_dictionary_part][lexem]["count"] - search_image_document["dict_of_lexems"][lexem]["count"], 0)
                server_dictionary_parts[current_server_dictionary_part][lexem]["documents_with_term"] = \
                max(server_dictionary_parts[current_server_dictionary_part][lexem]["documents_with_term"] - 1, 0)
                
            common_info["count_of_words"] = max(common_info["count_of_words"] - search_image_document["dict_of_lexems"][lexem]["count"], 0)

        common_info["count_of_documents"] -= 1
        
        # save full dictionary
        self.__setServerDictionaryParts(server_dictionary_parts)
                
        # save common info file
        self.__setServerDictionaryCommonInfo(common_info)
        
        # mark, that file added to dictionary
        self.__written_in_dictionary.append(document_url)
        
    def __recalculateInverseFrequencyOfLexemsInServerDictionary(self): 
        # common info file
        common_info = self.__getServerDictionaryCommonInfo()
        
        # load full dictionary
        server_dictionary_parts = self.__getServerDictionaryParts()
        
        count_of_documents = common_info["count_of_documents"]
        
        for part in server_dictionary_parts.keys():
            for lexem in server_dictionary_parts[part].keys():
                if server_dictionary_parts[part][lexem]["documents_with_term"] != 0:
                    inverse_frequency_of_lexem = math.log((count_of_documents / server_dictionary_parts[part][lexem]["documents_with_term"])) 
                    server_dictionary_parts[part][lexem]["inverse_frequency"] = round(inverse_frequency_of_lexem, 10)
                    
        # save full dictionary
        self.__setServerDictionaryParts(server_dictionary_parts)
        
        # save common info file
        self.__setServerDictionaryCommonInfo(common_info)
        
    # https://ru.wikipedia.org/wiki/TF-IDF
    def __recalculateWeightOfLexemsInImages(self): 
        
        def update_weights(document_url):
            search_image_document = self.__getSearchImageDocument(document_url, temp=True)
            if search_image_document == {}:
                return
            for lexem in search_image_document["dict_of_lexems"].keys():
                search_image_document["count_of_words"] = max(search_image_document["count_of_words"], 1)
                search_image_document["dict_of_lexems"][lexem]["weight"] = \
                round((search_image_document["dict_of_lexems"][lexem]["count"] / search_image_document["count_of_words"]), 10)
            self.__setSearchImageDocument(document_url, search_image_document, temp=True)
        
        for document in self.__documents_urls_to_add:
            update_weights(document)
                
        for document in self.__documents_urls_to_readd:
            update_weights(document)
        