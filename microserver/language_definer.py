from variables import *
import os   
import re
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
        
        # for text handling
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_DOCUMENT")

        Definer.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        Definer.__paths = {
            "DOCUMENTS_DIRECTORY_URL": os.path.join(Definer.__working_directory, DOCUMENTS_DIRECTORY_URL),
            "DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                         DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL),
            "DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                         DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL)
        }

        for _, path in Definer.__paths.items():
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
        return text_from_document_re
            
    # get source documents from dir, divided by language
    @staticmethod
    def _getSourcesDocumentsPaths():
        documents_by_language = {} 
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = Definer.__findDocumentsInDirectory(
                os.path.join(Definer.__paths["DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL"], language))
            documents_by_language[language] = language_sources_documents_paths
        return documents_by_language

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
                
                ngrams_profiles[language][current_path] =  DefinerNGrammsMethod.__createNGramsProfileForText(html_text)
        return ngrams_profiles

    # create profile for got text 
    @staticmethod
    def __createNGramsProfileForText(text): 
        return text[-10:]
    
    # create or rewrite doc of ngrams for every found source doc 
    # and created profiles for them 
    @staticmethod
    def __saveNgramsProfiles(ngrams_profiles):
        print(ngrams_profiles)

    # update profiles of tests documents, create them or rewrite
    def updateDefinerDocumentsProfiles(self):
        ngrams_profiles = DefinerNGrammsMethod.__documentsNGramsProfilesFromSources()
        self.__saveNgramsProfiles(ngrams_profiles)

    # create profile for got text
    # compare it with created before profiles of tests documents
    def define(text: str) -> str: 
        # DefinerNGrammsMethod.__createNGramsProfileForText(text)
        return "ru"

class DefinerAlphabetMethod(Definer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def define(text: str) -> str:
        return "ru"

class DefinerNeuralNetworkMethod(Definer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def define(text: str) -> str:
        return "ru"