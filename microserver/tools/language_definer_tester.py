from language_definer import DefinerNGrammsMethod, DefinerAlphabetMethod, DefinerNeuralNetworkMethod
from text_processor import TextProcessor
from variables import *
import os
import codecs

tp = TextProcessor()
working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
document_url = "documents/Engineering_ingegneria_informatica.html"
# document_url = "documents_for_language_definer/documents_sources/it/Base_di_dati_it.html"
# document_url = "documents/Incapsulamento_informatica.html"
# document_url = "documents/Алгоритм.html"
html_text = tp.makeClearedTextFromHtmlDocument(document_url)

# check ngrams
"""
dng = DefinerNGrammsMethod()
dng.updateDefinerDocumentsProfiles()
print(dng.define(html_text))
"""

# check alphabet
"""
dal = DefinerAlphabetMethod()
print(dal.define(html_text))
"""

# check nn method
dnn = DefinerNeuralNetworkMethod()
# dnn.updateDefinerNeuralNetworkWeights()
print(dnn.define(html_text))