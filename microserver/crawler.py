# custom modules
from database import DatabaseDocuments
from language_definer import DefinerNGrammsMethod, DefinerAlphabetMethod, DefinerNeuralNetworkMethod
from variables import *

# stadard modules
from time import time, strptime, mktime, strftime # , gmtime
from datetime import datetime
from bs4 import BeautifulSoup
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
        self.__database = DatabaseDocuments()
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
        
        # states
        self.possible_states = {
            0:"wait", 
            1:"indexing_files", 
            2:"creating_search_images", 
            3:"updating_server_dictionary", 
            4:"work_with_database"
        }
        self.current_state = self.possible_states[0]
        
    def __update_state(self, state):
        self.current_state = self.possible_states[state]
    
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
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_TEXT")
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
       
    def __reinit_variables__(self):
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
        
        self.current_state = self.possible_states[0]
       
    def start(self):
        # if last_start is not empty and less time has passed than it set
        if self.__last_start != "" and (time() - self.__last_start) < CRAWLER_TIMESPAN_SEC:
            return 
        
        self.__update_state(4)
        self.__documets_from_db = self.__database.getDocumentAll()
        self.__update_state(0)
        
        # work with docs 
        self.__update_state(1)
        self.__documentCheck()
        self.__update_state(2)
        self.__createSearchImagesOfDocuments()
        self.__update_state(3)
        self.__indexingServerDictionary()
        self.__update_state(4)
        self.__commitDataInDatabase()
        self.__update_state(0)
        
        self.__reinit_variables__()

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
            documets_from_db_set = set(documemt_record_in_db[0] for documemt_record_in_db in self.__documets_from_db)
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
        html_document_without_tags = re.sub(pattern, ' ', html_document_with_tags)
        text_from_document = self.__keepCharactersInStringWithRegex(
            input_string=html_document_without_tags.replace('\n', ' '),
            reference_string=ALLOWED_DICTIONARY)
            
        # split text by spaces and getting words with counts
        # list_of_lexems = re.split(DELIMETERS_OF_TEXT, text_from_document, flags=re.IGNORECASE)
        # list_of_lexems = [lexem for lexem in list_of_lexems if lexem != ""]
        list_of_lexems = re.sub(r'(?:(?!\u0301)[\W\d_])+', ' ', ("".join(character for character in text_from_document if character in ALLOWED_DICTIONARY)))
        list_of_lexems = [lexem for lexem in list_of_lexems.split(" ") if len(lexem) > 2]
        
        dict_of_lexems = {
            lexem: {
                "count": list_of_lexems.count(lexem), 
                "weight": 0
            } for lexem in list_of_lexems
        }
        
        # language definition
        language_defined_by_ngramms_method = ""
        language_defined_by_alphabet_method = ""
        language_defined_by_neural_network_method = ""

        try: language_defined_by_ngramms_method = DefinerNGrammsMethod.define(html_document_without_tags)
        except: pass
        try: language_defined_by_alphabet_method =DefinerAlphabetMethod.define(html_document_without_tags)
        except: pass
        try: language_defined_by_neural_network_method = DefinerNeuralNetworkMethod.define(html_document_without_tags)
        except: pass

        search_image_document = {
            "count_of_words": len(list_of_lexems),
            "language_defined": {
                "by_ngramms_method": language_defined_by_ngramms_method,
                "by_alphabet_method": language_defined_by_alphabet_method,
                "by_neural_network_method": language_defined_by_neural_network_method,
            },
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
        """
        server_dictionary_parts = {} # TAKES REALLY A LOT OF RAM, but this solution faster then other (load in query for ex)
        char_paths = [
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json") for char in ALLOWED_DICTIONARY
        ]
        
        for char_path in char_paths:
            with open(char_path, "r", encoding="utf-8") as server_dictionary_part_file:
                json_content = server_dictionary_part_file.read()
                server_dictionary_parts[char_path] = json.loads(json_content)
        """
        server_dictionary_parts = {}
        for char in ALLOWED_DICTIONARY:
            char_path = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
            with open(char_path, "r", encoding="utf-8") as server_dictionary_part_file:
                json_content = server_dictionary_part_file.read()
                server_dictionary_parts[f"{char}.json"] = json.loads(json_content)
                
        return server_dictionary_parts
        
    # server dictionary set
    def __setServerDictionaryParts(self, server_dictionary_parts):   
        """
        char_paths = [
            os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json") for char in ALLOWED_DICTIONARY
        ]
        for char_path in char_paths:
            with open(char_path, "w", encoding="utf-8") as server_dictionary_part_file:
                json.dump(server_dictionary_parts[char_path], server_dictionary_part_file)
        """        
        for char in ALLOWED_DICTIONARY:
            char_path = os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
            with open(char_path, "w", encoding="utf-8") as server_dictionary_part_file:
                json.dump(server_dictionary_parts[f"{char}.json"], server_dictionary_part_file)
        
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
            current_server_dictionary_part = char + ".json" #os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
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
            current_server_dictionary_part = char + ".json" #os.path.join(self.__working_directory, SERVER_DICTIONARY_DIRECTORY_URL, char + ".json")
            # make structure for this word
            if lexem is " " or lexem is "":
                continue
            if lexem in server_dictionary_parts[current_server_dictionary_part]:
                server_dictionary_parts[current_server_dictionary_part][lexem]["count"] = \
                max(server_dictionary_parts[current_server_dictionary_part][lexem]["count"] - search_image_document["dict_of_lexems"][lexem]["count"], 0)
                server_dictionary_parts[current_server_dictionary_part][lexem]["documents_with_term"] = \
                max(server_dictionary_parts[current_server_dictionary_part][lexem]["documents_with_term"] - 1, 0)
                
            common_info["count_of_words"] = max(common_info["count_of_words"] - search_image_document["dict_of_lexems"][lexem]["count"], 0)

        common_info["count_of_documents"] = max(common_info["count_of_documents"] - 1, 0)
        
        # save full dictionary
        self.__setServerDictionaryParts(server_dictionary_parts)
                
        # save common info file
        self.__setServerDictionaryCommonInfo(common_info)
        
        # mark, that file added to dictionary
        self.__written_in_dictionary.append(document_url)
        
    # https://ru.wikipedia.org/wiki/TF-IDF
    def __recalculateInverseFrequencyOfLexemsInServerDictionary(self): 
        # common info file
        common_info = self.__getServerDictionaryCommonInfo()
        
        # load full dictionary
        server_dictionary_parts = self.__getServerDictionaryParts()
        
        count_of_documents = common_info["count_of_documents"]
        
        for part in server_dictionary_parts.keys():
            for lexem in server_dictionary_parts[part].keys():
                if server_dictionary_parts[part][lexem]["documents_with_term"] != 0 and count_of_documents != 0:
                    #idf
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
                
            print(document_url)
            # load full dictionary
            server_dictionary_parts = self.__getServerDictionaryParts()
                
            for lexem in search_image_document["dict_of_lexems"].keys():
                # count of all words, can not be zero
                search_image_document["count_of_words"] = max(search_image_document["count_of_words"], 1)
                # frequency of the term in the document
                # tf
                frequency = round((search_image_document["dict_of_lexems"][lexem]["count"] / search_image_document["count_of_words"]), 10)
                # tf * idf
                search_image_document["dict_of_lexems"][lexem]["weight"] = round(frequency * server_dictionary_parts[f"{lexem[0]}.json"][lexem]["inverse_frequency"], 10)
                
            self.__setSearchImageDocument(document_url, search_image_document, temp=True)
        
        for document in self.__documents_urls_to_add:
            update_weights(document)
                
        for document in self.__documents_urls_to_readd:
            update_weights(document)
        
    # ### WORK WITH DATABASE ### #
    
    def __commitDataInDatabase(self):
        for document in self.__documents_urls_to_add:
            self.__transactionDocumentSearchImageAdd(document)
            
        for document in self.__documents_urls_to_readd:
            self.__transactionDocumentSearchImageDelete(document)
            self.__transactionDocumentSearchImageAdd(document)
        
        for document in self.__documents_urls_to_delete:
            self.__transactionDocumentSearchImageDelete(document)
            
    def __transactionDocumentSearchImageAdd(self, document_url):
        # create record in db        
        time_structure = datetime.now()

        self.__database.addDocument(
            url_document=(os.path.join(document_url)),
            search_image_document=(os.path.join(SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, document_url + ".json")),
            last_update_document=time_structure.strftime(TIME_FORMAT))
        
        self.__database.updateDocument(
            url_document=(os.path.join(document_url)),
            search_image_document=(os.path.join(SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, document_url + ".json")),
            last_update_document=time_structure.strftime(TIME_FORMAT))
            
        # move json from temp to search images dir 
        search_image_document = self.__getSearchImageDocument(document_url, temp=True)
        self.__setSearchImageDocument(document_url, search_image_document, temp=False)
        
        # remove json from temp
        try:
            os.remove(os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, "temp", document_url + ".json"))
        except Exception as ex:
            print(f"__transactionDocumentSearchImageAdd | No such temp search image {document_url} | {ex}")
        
    def __transactionDocumentSearchImageDelete(self, document_url):
        # delete record from db
        self.__database.deleteDocument(url_document=document_url)
        
        # delete residual files
        try:
            os.remove(os.path.join(self.__working_directory, SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL, document_url + ".json"))
        except Exception as ex:
            print(f"__transactionDocumentSearchImageDelete | No such search image {document_url} | {ex}")
           