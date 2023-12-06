from language_definer import DefinerNGrammsMethod, DefinerAlphabetMethod, DefinerNeuralNetworkMethod
from variables import *
import os
import codecs

working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
document_url = "documents/Incapsulamento_informatica.html"

# get raw text from file
##########################################################################

html_document_with_tags=""
current_path: str = os.path.join(working_directory, document_url)

if os.path.isfile(current_path):
    with codecs.open(current_path, "r", encoding="utf-8") as file:
        html_document_with_tags = file.read()

# clear html
##########################################################################

import re

def clear_html(html_raw):
    def keepCharactersInStringWithRegex(input_string, reference_string):
        pattern = f"[^{reference_string.lower()}]"
        filtered_string = re.sub(pattern, "", input_string.lower())
        return filtered_string.lower()

    # remove tags and newlines from raw text
    pattern = re.compile('<.*?>')
    html_document_without_tags = re.sub(pattern, ' ', html_raw)
    text_from_document_re = keepCharactersInStringWithRegex(
        input_string=html_document_without_tags.replace('\n', ' '),
        reference_string=ALLOWED_DICTIONARY)

    text_from_document_re = re.sub(" +", " ", text_from_document_re)

    #with open("file_re.txt", "w", encoding="utf-8") as file_re:
    #    file_re.write(text_from_document_re)
    
    return text_from_document_re

# check definers
##########################################################################
html_text = clear_html(html_document_with_tags)

# check ngrams
"""
dng = DefinerNGrammsMethod()
dng.updateDefinerDocumentsProfiles()
print(dng.define(html_text))
"""

# check alphabet
dal = DefinerAlphabetMethod()
print(dal.define(html_text))

""" Variant 1
########################################################################## Variant 1
import re

def keepCharactersInStringWithRegex(input_string, reference_string):
    pattern = f"[^{reference_string.lower()}]"
    filtered_string = re.sub(pattern, "", input_string.lower())
    return filtered_string.lower()

# remove tags and newlines from raw text
pattern = re.compile('<.*?>')
html_document_without_tags = re.sub(pattern, ' ', html_document_with_tags)
text_from_document_re = keepCharactersInStringWithRegex(
    input_string=html_document_without_tags.replace('\n', ' '),
    reference_string=ALLOWED_DICTIONARY)

# print (text_from_document)
with open("file_re.txt", "w", encoding="utf-8") as file_re:
    file_re.write(text_from_document_re)

########################################################################## Variant 2

from bs4 import BeautifulSoup

inner_soup = BeautifulSoup(html_document_with_tags, "html.parser")
text_from_document_bs = inner_soup.get_text()

# print(text_from_document_bs)
with open("file_bs.txt", "w", encoding="utf-8") as file_bs:
    file_bs.write(text_from_document_bs)
"""