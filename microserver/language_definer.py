from variables import *
import os   
import stat
import shutil

import re
import json
import codecs

class Definer(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_system_variables__()

    @staticmethod
    def __init_system_variables__():
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        if not DOCUMENTS_FOR_DEFINER_DIRECTORY_URL: 
            raise Exception("Can not find variable DOCUMENTS_FOR_DEFINER_DIRECTORY_URL")
        if not DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL: 
            raise Exception("Can not find variable DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL")
        if not DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL: 
            raise Exception("Can not find variable DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL")
        if not LANGUAGES_TO_DEFINE: 
            raise Exception("Can not find variable LANGUAGES_TO_DEFINE")
        
        # ngram
        if not NGRAMM_SIZE: 
            raise Exception("Can not find variable NGRAMM_SIZE")
        # alphabet
        if not LANGUAGES_ALPHABETS: 
            raise Exception("Can not find variable LANGUAGES_ALPHABETS")
        
        # for text handling
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_DOCUMENT")

        Definer.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        Definer._paths = {
            "DOCUMENTS_DIRECTORY_URL": os.path.join(Definer.__working_directory, DOCUMENTS_DIRECTORY_URL),
            "DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                         DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL),
            "DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                         DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL)
        }

        for _, path in Definer._paths.items():
            is_exist = os.path.exists(path)
            if not is_exist:
                os.makedirs(path)

    # just find documents in directory, return array of pathes 
    # in path last part is filename 
    @staticmethod
    def __findDocumentsInDirectory(directory_url):
        docpaths = []
        for filename in os.listdir(directory_url):
            filepath: str = os.path.join(directory_url, filename)
            if os.path.isfile(filepath):
                docpaths.append(filepath)
        return docpaths
    
    # from html to text, for test documents
    # definers must get already cleared text 
    @staticmethod
    def _getClearTextFromHtml(html_text):
        def keepCharactersInStringWithRegex(input_string, reference_string):
            pattern = f"[^{reference_string.lower()}]"
            filtered_string = re.sub(pattern, "", input_string.lower())
            return filtered_string.lower()
        # remove tags and newlines from raw text
        pattern = re.compile('<.*?>')
        html_document_without_tags = re.sub(pattern, ' ', html_text)
        text_from_document_re = keepCharactersInStringWithRegex(
            input_string=html_document_without_tags.replace('\n', ' '),
            reference_string=ALLOWED_DICTIONARY)    
        text_from_document_re = re.sub(" +", " ", text_from_document_re)        
        
        return text_from_document_re
            
    # get source documents from dir, divided by language
    @staticmethod
    def _getSourcesDocumentsPaths():
        documents_by_language = {} 
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = Definer.__findDocumentsInDirectory(
                os.path.join(Definer._paths["DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL"], language))
            documents_by_language[language] = language_sources_documents_paths
        return documents_by_language
            
    # get source documents from dir, divided by language
    @staticmethod
    def _getProfilesDocumentsPaths(definition_type_str):
        documents_by_language = {} 
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = Definer.__findDocumentsInDirectory(
                os.path.join(Definer._paths["DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL"], definition_type_str, language))
            
            documents_by_language[language] = language_sources_documents_paths
        return documents_by_language
            
    # remove source documents from dir, by type of definition
    @staticmethod
    def _removeProfileDocumentsByType(definition_type_str): #, lang: bool = False):
        
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = os.path.join(
                Definer._paths["DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL"], 
                definition_type_str, 
                language)
            
            if os.path.exists(language_sources_documents_paths):
                def onRmError(func, path, exc_info):
                # path contains the path of the file that couldn't be removed
                # let's just assume that it's read-only and unlink it.
                    os.chmod(path, stat.S_IWRITE)
                    os.unlink(path)
                shutil.rmtree(language_sources_documents_paths, onerror = onRmError)    
                # os.remove(language_sources_documents_paths)
            
            if not os.path.exists(language_sources_documents_paths):
                os.makedirs(language_sources_documents_paths, stat.S_IWRITE)
            
        return 


class DefinerNGrammsMethod(Definer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # get source documents from directories by language
    # create and return profiles for them
    @staticmethod
    def __documentsNGramsProfilesFromSources(): 
        sources_docs_paths = super(DefinerNGrammsMethod, DefinerNGrammsMethod)._getSourcesDocumentsPaths()
        
        ngrams_profiles = {}
        for language in LANGUAGES_TO_DEFINE:
            ngrams_profiles[language] = {}

        for language in sources_docs_paths.keys():
            for current_path in sources_docs_paths[language]:
                html_document_with_tags=""
            
                if os.path.isfile(current_path):
                    with codecs.open(current_path, "r", encoding="utf-8") as file:
                        html_document_with_tags = file.read()
                        
                html_text = DefinerNGrammsMethod._getClearTextFromHtml(html_document_with_tags)
                
                ngrams_profiles[language][os.path.join(os.path.split(current_path)[1])] = \
                    DefinerNGrammsMethod.__createNGramsProfileForText(html_text)
        return ngrams_profiles

    # create profile for got text 
    @staticmethod
    def __createNGramsProfileForText(text): 
        created_ngrams_list: list = []
        
        def getNgramsFromWord(word, ngram_size) -> list:
            ngrams = list()
            if bool(re.search(r'\d', word)) or type(word) != str:
                return []
            elif len(word) <= ngram_size:
                ngrams.append(word)
            else:
                for i in range(len(word) - (ngram_size - 1)):
                    ngram = word[i:i + ngram_size]
                    ngrams.append(ngram)
            return ngrams
            
        for word in text.split(" "):
            if word != "" and word is not None:
                ngrams = getNgramsFromWord(word, NGRAMM_SIZE)
                created_ngrams_list += ngrams

        created_ngrams: dict = {}
        for ngram in created_ngrams_list:
            if created_ngrams.get(ngram):
                created_ngrams[ngram] += 1
            else:
                created_ngrams[ngram] = 1

        ngrams_to_return = list(dict(sorted(created_ngrams.items(), key=lambda x:x[1], reverse=True)))
        return ngrams_to_return 
    
    # create or rewrite doc of ngrams for every found source doc 
    # and created profiles for them 
    @staticmethod
    def __saveNgramsProfiles(ngrams_profiles):
        definition_type_str="ngrams"
        DefinerNGrammsMethod._removeProfileDocumentsByType(definition_type_str=definition_type_str)
        
        # documents_by_language = {} 
        ngrams_dir_name = Definer._paths["DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL"]
        for language in ngrams_profiles.keys():
            for document_in_lang in ngrams_profiles[language].keys():
                # dict ngrams_profiles[language][document_in_lang]                
                profiles_documents_path_full = os.path.join(ngrams_dir_name, definition_type_str, language, document_in_lang)
                ### write in file 
                with codecs.open(profiles_documents_path_full, "w+", encoding="utf-8") as profile_file:
                    json.dump(ngrams_profiles[language][document_in_lang], profile_file)
        return 
    
    # update profiles of tests documents, create them or rewrite
    def updateDefinerDocumentsProfiles(self):
        ngrams_profiles = DefinerNGrammsMethod.__documentsNGramsProfilesFromSources()
        self.__saveNgramsProfiles(ngrams_profiles)

    @staticmethod
    def __calculatingTheOutOfPlaceMeasureBetweenTwoProfiles(ngram_profile_1, ngram_profile_2):
        distance_measure = 0
        # ngram_profile_1 = list(ngram_profile_1)
        # ngram_profile_2 = list(ngram_profile_2)
        max_diff = len(ngram_profile_1)
        for ngram in ngram_profile_1:
            if ngram in ngram_profile_2:
                distance_measure += abs(ngram_profile_1.index(ngram) - ngram_profile_2.index(ngram))  
            else:
                distance_measure += max_diff
        return distance_measure

    # returns dict {"path": path, "language": language_of_doc, "profile": ngrams}
    @staticmethod
    def __findNearestNgramProfile(ngram_profile, ngram_profiles) -> dict:
        nearest_document = {}
        for language in ngram_profiles.keys():
            for profile_path in ngram_profiles[language]:
                profile = None
                if os.path.isfile(profile_path):
                    with codecs.open(profile_path, "r", encoding="utf-8") as profile_file:
                        json_content = profile_file.read()
                        profile = json.loads(json_content)
                #
                if profile and type(language) == str and len(language) == 2:
                    distance_measure = DefinerNGrammsMethod.__calculatingTheOutOfPlaceMeasureBetweenTwoProfiles(
                        ngram_profile, profile)
                    if nearest_document == {}:
                        nearest_document = {"path":profile_path, "language":language,"profile":profile, "distance_measure":distance_measure}
                    else:
                        if nearest_document["distance_measure"] > distance_measure:
                            nearest_document = {"path": profile_path, "language": language, "profile": profile, "distance_measure":distance_measure}
                    
        return nearest_document

    # create profile for got text
    # compare it with created before profiles of tests documents
    def define(self, text: str) -> str: 
        ngram_profile = DefinerNGrammsMethod.__createNGramsProfileForText(text)
        ngram_profiles = Definer._getProfilesDocumentsPaths("ngrams")
        nearest_document = DefinerNGrammsMethod.__findNearestNgramProfile(
            ngram_profile=ngram_profile, 
            ngram_profiles=ngram_profiles)
        
        # print(nearest_document["path"], nearest_document["language"])
        print("ngram: ", nearest_document["language"])
        
        return nearest_document["language"]


class DefinerAlphabetMethod(Definer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def define(text: str) -> str:
        text = Definer._getClearTextFromHtml(text)
        
        chars = {}
        for char in text:
            if char == " ": continue
            if not chars.get(char): chars[char] = 1 
            else: chars[char] += 1 

        languages_weights = {language: 0 for language in LANGUAGES_TO_DEFINE}
        for char in chars:
            for language in LANGUAGES_TO_DEFINE:
                if char in LANGUAGES_ALPHABETS[language]:
                    languages_weights[language] += chars[char]
        
        # print(chars)

        result = max(languages_weights, key=languages_weights.get)
        if languages_weights[result] == 0:
            return ""
        
        print("alph: ", result)
        return result

class DefinerNeuralNetworkMethod(Definer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def define(text: str) -> str:
        return "ru"