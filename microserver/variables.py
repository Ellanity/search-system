# common
WORKING_DIRECTORY=r"C:\Users\Eldar\Documents\GitHub\search-system\microserver"

# database
DATABASE_URL="documents.db"
DB_INSTRUCTIONS_DIRECTORY_URL="db_instructions"
TIME_FORMAT="%Y.%m.%dT%H:%M:%S"

# crawler
DOCUMENTS_DIRECTORY_URL="documents"
SEARCH_IMAGES_DOCUMENTS_DIRECTORY_URL="search_images_documents"

# CRAWLER_TIMESPAN_SEC=300
CRAWLER_TIMESPAN_SEC=600

# CRAWLER_DOCUMENTS_READD_TIMESPAN_SEC=200
CRAWLER_DOCUMENTS_READD_TIMESPAN_SEC=86400

ALLOWED_DICTIONARY="ёйцукенгшщзхъфывапролджэячсмитьибюabcdefghijklmnopqrstuvwxyzàèéìíîòóùú "
# ALLOWED_DICTIONARY="ёйцукенгшщзхъфывапролджэячсмитьибю "

DELIMETERS_OF_TEXT=" |.|,|_|-|!|&|?|\"|'|%|^|*|(|)|@|#|~|:|/|\\|=|$"


# language_definer
DOCUMENTS_FOR_DEFINER_DIRECTORY_URL="documents_for_language_definer"
DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL="documents_sources"
DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL="documents_profiles"
NEURAL_NETWORK_DATA_DIRECTORY_URL="neural_network_data"
# # # # # Languages 
LANGUAGES_TO_DEFINE=("ru", "it")
LANGUAGES_ALPHABETS={"ru": "ёйцукенгшщзхъфывапролджэячсмитьибю",
                     "it": "abcdefghijklmnopqrstuvwxyzàèéìíîòóùú"}
# # # # # Constants for definers
NGRAMM_SIZE = 4 
MAX_TOKEN_LENGTH = 20 
MAX_TOKEN_INDEX = ((MAX_TOKEN_LENGTH + 1) / 2) * MAX_TOKEN_LENGTH * len(ALLOWED_DICTIONARY) + 2 

# Analyzer
SERVER_DICTIONARY_DIRECTORY_URL="server_dictionary"

# http
HTTP_PORT=3000
HOST="0.0.0.0"
SERVER_ADDRESS = (HOST, HTTP_PORT)