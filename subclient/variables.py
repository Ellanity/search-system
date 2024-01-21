###############################################
###               Common info               ### 
###############################################
# The directory from which the project is 
# launched
WORKING_DIRECTORY=r"C:\Users\...\GitHub\search-system\subclient"
# HTTP settings
HTTP_PORT=13000
HOST="0.0.0.0"
SERVER_ADDRESS = (HOST, HTTP_PORT)

###############################################
###               Database info             ### 
###############################################
# The directory where the files of the site 
# client are located
SITE_FILES_DIRECTORY_URL = "site"

###############################################
###            Microservers info            ### 
###############################################
# The format in which all microservers of 
# the local network should be defined
SERVERS = {
    "example": {
        "host":"127.0.0.1",
        "port":3000
    }
}