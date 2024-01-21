###############################################
###               Common info               ### 
###############################################
# The directory from which the project is 
# launched
WORKING_DIRECTORY=r"C:\Users\...\GitHub\search-system\microserver"
# HTTP settings
HTTP_PORT=3000
HOST="0.0.0.0"
SERVER_ADDRESS = (HOST, HTTP_PORT)

###############################################
###               Database info             ### 
###############################################
# Database name
DATABASE_URL="documents.db" 
# the directory where sql queries used by the 
# orm system are stored
DB_INSTRUCTIONS_DIRECTORY_URL="db_instructions" 
# The time format used in the database
TIME_FORMAT="%Y.%m.%dT%H:%M:%S"

###############################################
###               Crawler info              ### 
###############################################
# The name of the directory where all documents
# are stored
DOCUMENTS_DIRECTORY_URL="documents"
# The name of the directory where all search 
# images documents are stored
SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL="search_images_documents"
# Time period in seconds - how often the web 
# crawler is launched
CRAWLER_TIMESPAN_SEC=600
# Time period in seconds - after what period of 
# time information about the file is considered 
# outdated
CRAWLER_DOCUMENTS_READD_TIMESPAN_SEC=86400

###############################################
###                Text info                ### 
###############################################
# The list of characters that is used in 
# documents, the remaining characters are 
# ignored. A dictionary is created from these 
# characters
ALLOWED_DICTIONARY="ёйцукенгшщзхъфывапролджэячсмитьибюabcdefghijklmnopqrstuvwxyzàèéìíîòóùú "
# A list of characters used to separate the text
DELIMETERS_OF_TEXT=" |.|,|_|-|!|&|?|\"|'|%|^|*|(|)|@|#|~|:|/|\\|=|$"

###############################################
###              Tokenizer info             ### 
###############################################
# The maximum length of a word in the text, to
# allocate an index to tokens with a tokenizer 
MAX_TOKEN_LENGTH = 25 
# The maximum value of the token index
MAX_TOKEN_INDEX = int(((MAX_TOKEN_LENGTH + 1) / 2) * MAX_TOKEN_LENGTH * len(ALLOWED_DICTIONARY) + 2)

###############################################
###          Language definer info          ### 
###############################################
# The name of the directory where the documents 
# for teaching language detection methods are 
# stored
DOCUMENTS_FOR_DEFINER_DIRECTORY_URL="documents_for_language_definer"
# A subdirectory with raw files for training
DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL="documents_sources"
# A subdirectory with generated training data
DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL="documents_profiles"
# A subdirectory that stores information for 
# the neural network text detection method
NEURAL_NETWORK_DATA_DIRECTORY_URL="neural_network_data"

### ### ### Languages 
# Standardized language abbreviations that the 
# system can define
LANGUAGES_TO_DEFINE=("ru", "it")
# Standardized abbreviations of languages that 
# can be defined by the system and their 
# corresponding alphabets
LANGUAGES_ALPHABETS={"ru": "ёйцукенгшщзхъфывапролджэячсмитьибю",
                     "it": "abcdefghijklmnopqrstuvwxyzàèéìíîòóùú"}

###############################################
###          Ngram method (LangDef)         ### 
###############################################
### ### ### Constants for definers
# The length of the ngram used in the ngram 
# method of language definition
NGRAMM_SIZE = 4

###############################################
###      Nural network method (LangDef)     ### 
###############################################
### ### ### num of neurons on input layer
# Determining the size of sequences of tokens 
# transmitted to the neural network to 
# determine the language
MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN = 50 

###############################################
###             Summarizers info            ### 
###############################################
# The number of sentences that automatic text 
# summarizers returns
COUNT_OF_SENTENCES_TO_RETURN = 10

###############################################
###              Analyzer info              ### 
###############################################
# The directory where the microserver 
# dictionary is stored
SERVER_DICTIONARY_DIRECTORY_URL="server_dictionary"