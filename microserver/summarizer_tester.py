from variables import *
from text_processor import TextProcessor
import os

from summarizer import SummarizerClassicSummary, SummarizerKeywordsSummary, SummarizerMLSummary

tp = TextProcessor()
working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
# document_url = "documents/Engineering_ingegneria_informatica.html"
# document_url = "documents_for_language_definer/documents_sources/it/Base_di_dati_it.html"
# document_url = "documents/Incapsulamento_informatica.html"
document_url = "documents/Алгоритм.html"

html_text = tp.makeClearedTextFromHtmlDocument(document_url, True, True)

scs = SummarizerClassicSummary()
# print(html_text)
# print(scs.summarize(html_text))
print(*scs.summarize(html_text), sep="\n")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
print("done")