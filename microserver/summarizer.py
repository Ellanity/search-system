# custom lib of global variables 
from variables import *

# all definers must get already cleared text 
from text_processor import TextProcessor

# work with files
import os   
import stat
import shutil
import json
import codecs

class Summarizer(object):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__init_system_variables__()

    @staticmethod
    def __init_system_variables__():
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        
        # sentence extraction
        if not COUNT_OF_SENTENCES_TO_RETURN: 
            raise Exception("Can not find variable COUNT_OF_SENTENCES_TO_RETURN")
        
        # for text handling
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_DOCUMENT")

        Summarizer.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        Summarizer._paths = {
            "DOCUMENTS_DIRECTORY_URL": os.path.join(Summarizer.__working_directory, DOCUMENTS_DIRECTORY_URL)
        }

        for _, path in Summarizer._paths.items():
            is_exist = os.path.exists(path)
            if not is_exist:
                os.makedirs(path)

# With sentence extraction
class SummarizerClassicSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        @staticmethod
        def sentenceExtraction(paragraphs: list) -> list:
            
            # count_of_symbols in text 
            count_of_symbols_in_doc = 0 
            for paragraph_index in range(len(paragraphs)):
                count_of_symbols_before_in_paragraph = 0
                for sentence_index in range(len(paragraphs[paragraph_index])):
                    
                    paragraphs[paragraph_index][sentence_index] = {
                        "sentence" : paragraphs[paragraph_index][sentence_index],
                        "count_of_symbols_before_in_doc": count_of_symbols_in_doc, 
                        "count_of_symbols_before_in_paragraph": count_of_symbols_before_in_paragraph, 
                    }

                    count_of_symbols_in_doc += len(paragraphs[paragraph_index][sentence_index]["sentence"])
                    count_of_symbols_before_in_paragraph += len(paragraphs[paragraph_index][sentence_index]["sentence"])
                    
                paragraphs[paragraph_index] = {
                    "paragraph": paragraphs[paragraph_index],
                    "count_of_symbols_in_paragraph": count_of_symbols_before_in_paragraph
                }

            COUNT_OF_SENTENCES_TO_RETURN = 10
            sentences_to_return = []
            min_weight_in_sentences_to_return = 0

            for paragraph_index in range(len(paragraphs)):
                for sentence_index in range(len(paragraphs[paragraph_index]["paragraph"])):
                    
                    # calculate weight of sentence
                    count_of_symbols_before_in_doc = paragraphs[paragraph_index]["paragraph"][sentence_index]["count_of_symbols_before_in_doc"]
                    count_of_symbols_before_in_paragraph = paragraphs[paragraph_index]["paragraph"][sentence_index]["count_of_symbols_before_in_paragraph"]
                    count_of_symbols_in_paragraph = paragraphs[paragraph_index]["count_of_symbols_in_paragraph"]

                    Posd = 1 - (count_of_symbols_before_in_doc / count_of_symbols_in_doc)
                    Posp = 1 - (count_of_symbols_before_in_paragraph / count_of_symbols_in_paragraph)
                    sentence_weight = Posd * Posp

                    paragraphs[paragraph_index]["paragraph"][sentence_index]["sentence_weight"] = sentence_weight
                    
                    # add sentence to return list
                    if sentence_weight > min_weight_in_sentences_to_return or len(sentences_to_return) < COUNT_OF_SENTENCES_TO_RETURN:
                        # # # # # print(sentence_weight, min_weight_in_sentences_to_return)

                        # delete sentence with minimal weight
                        if sentence_weight > min_weight_in_sentences_to_return and \
                            len(sentences_to_return) >= COUNT_OF_SENTENCES_TO_RETURN :
                            sentence_index_to_remove = -1

                            # find lowest weight
                            lowest_weight = min_weight_in_sentences_to_return + 1e-5
                            for sentence_to_retrun_index in range(len(sentences_to_return)):
                                if sentences_to_return[sentence_to_retrun_index]["sentence_weight"] <= lowest_weight:
                                    lowest_weight = sentences_to_return[sentence_to_retrun_index]["sentence_weight"]
                                    sentence_index_to_remove = sentence_to_retrun_index
                            min_weight_in_sentences_to_return = lowest_weight
                            # # # # # print(sentence_index_to_remove)

                            # remove sentence
                            if sentence_index_to_remove >= 0:
                                # # # # # print("\nremove: ", sentences_to_return[sentence_index_to_remove], "\n")
                                sentences_to_return.pop(sentence_index_to_remove)
                                
                        # add new sentence
                        sentences_to_return.append({
                            "sentence": paragraphs[paragraph_index]["paragraph"][sentence_index]["sentence"], 
                            "sentence_weight": sentence_weight
                        })

                        # update weight min
                        min_weight_in_sentences_to_return = sentence_weight
                        for sentence_to_retrun_index in range(len(sentences_to_return)):
                            min_weight_in_sentences_to_return = min(
                                min_weight_in_sentences_to_return,
                                sentences_to_return[sentence_to_retrun_index]["sentence_weight"])

            # print(sentences_to_return)
            return [sentence["sentence"].capitalize() for sentence in sentences_to_return]

        @staticmethod   
        def summarize(text: str) -> list:
             
            tokenized_text = TextProcessor.tokenizeTextByParagraphs(text=text)
            result = SummarizerClassicSummary.sentenceExtraction(tokenized_text)
            print("sentence extraction: done")
            return result

class SummarizerKeywordsSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        @staticmethod   
        def summarize(text: str) -> list:
            sentenses = []
            sentenses = text.split(" ")[:10]
            return sentenses

class SummarizerMLSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        
        @staticmethod   
        def summarize(text: str) -> list:
            sentenses = []
            sentenses = text.split(" ")[:10]
            return sentenses

