from variables import *

from nltk.tokenize import sent_tokenize, word_tokenize 

import re
import os
import codecs

class TextProcessor:
    def __init__(self): 
        self.__init_system_variables__()
        return
        
    @staticmethod
    def __init_system_variables__():
        # check variables
        if not WORKING_DIRECTORY: 
            raise Exception("Can not find variable WORKING_DIRECTORY")
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not MAX_TOKEN_LENGTH : 
            raise Exception("Can not find variable MAX_TOKEN_LENGTH")
        
    @staticmethod
    def keepCharactersInStringWithRegex(input_string, reference_string):
        pattern = f"[^{reference_string.lower()}]"
        filtered_string = re.sub(pattern, "", input_string.lower())
        return filtered_string.lower()
        
    @staticmethod
    def makeClearedTextFromRawHtmlText(html_raw: str, 
                                       save_sentences: bool = False, 
                                       save_paragraphs: bool = False, 
                                       save_commas: bool = False) -> str:
        # remove tags and newlines from raw text
        pattern = re.compile('<.*?>')
        html_document_without_tags = re.sub(pattern, ' ', html_raw)

        allowed_dict_prepared = ALLOWED_DICTIONARY
        if save_sentences:
            allowed_dict_prepared += ".!?"
        if save_paragraphs:
            allowed_dict_prepared += "\n"
        if save_commas:
            allowed_dict_prepared += ",;"
        
        # if not save_paragraphs:
        #     html_document_without_tags.replace('\n', ' ')

        text_from_document_re = TextProcessor.keepCharactersInStringWithRegex(
            input_string=html_document_without_tags,
            reference_string=allowed_dict_prepared)

        text_from_document_re = re.sub(" +", " ", text_from_document_re)
        
        if save_paragraphs:
            text_from_document_re = re.sub("\n | \n", "\n", text_from_document_re)
            text_from_document_re = re.sub("\n+", ".\n", text_from_document_re)
            text_from_document_re = re.sub("\.+", ".", text_from_document_re)

        return text_from_document_re
    
    @staticmethod
    def makeClearedTextFromHtmlDocument(html_path: str, 
                                        save_sentences: bool = False, 
                                        save_paragraphs: bool = False, 
                                        save_commas: bool = False) -> str:
        html_document_with_tags=""
        current_path: str = os.path.join(WORKING_DIRECTORY, html_path)

        if os.path.isfile(current_path):
            with codecs.open(current_path, "r", encoding="utf-8") as file:
                html_document_with_tags = file.read()
                        
        text_from_document_re = TextProcessor.makeClearedTextFromRawHtmlText(
            html_document_with_tags, 
            save_sentences, 
            save_paragraphs, 
            save_commas)
        
        return text_from_document_re
    
    @staticmethod
    def tokenizeTextByWords(text: str) -> dict:

        text = TextProcessor.keepCharactersInStringWithRegex(
            input_string=text, 
            reference_string=ALLOWED_DICTIONARY)
        
        tokens = word_tokenize(text)
        
        chars_nums_dict = {}
        char_num = 1
        for char in ALLOWED_DICTIONARY:
            chars_nums_dict[char] = char_num
            char_num += 1

        tokens_with_inedexes = {}
        
        for token in tokens:
            if len(token) > MAX_TOKEN_LENGTH :
                token = token[:MAX_TOKEN_LENGTH]
            index = 0
            num_of_char_in_token = 1
            for char in token:
                if char not in ALLOWED_DICTIONARY:
                    raise Exception("Tokenizer got text with unexpected symbols, check text you try tokenize")
                index += chars_nums_dict[char] * num_of_char_in_token
                num_of_char_in_token += 1
            tokens_with_inedexes[token] = index
            
        return tokens_with_inedexes
    
    @staticmethod
    def tokenizeTextByParagraphs(text: str) -> dict :\
    
        paragraphs_to_return = list()
        paragraphs_to_return.append([])
        paragraphs = text.split("\n")
        # print(*paragraphs[:6], sep="\n\n\n\n\n\n")
        for paragraph in paragraphs:
            sentences = sent_tokenize(paragraph)
            for sentence in sentences:
                if len(sentence.split(" ")) <= 3:
                    continue
                paragraphs_to_return[-1].append(sentence.replace("\n", " "))
            if len(paragraphs_to_return[-1]) > 0:
                paragraphs_to_return.append([])

        return paragraphs_to_return[:len(paragraphs_to_return) - 1]
    
    @staticmethod
    def tokenizeTextBySentences(text: str) -> dict :
        paragraphs = TextProcessor.tokenizeTextByParagraphs(text=text)
        sentences = list()
        for paragraph in paragraphs:
            sentences.extend(paragraph) 
        return sentences



""" Variant 1
########################################################################## Variant 1
import re

def TextProcessor.keepCharactersInStringWithRegex(input_string, reference_string):
    pattern = f"[^{reference_string.lower()}]"
    filtered_string = re.sub(pattern, "", input_string.lower())
    return filtered_string.lower()

# remove tags and newlines from raw text
pattern = re.compile('<.*?>')
html_document_without_tags = re.sub(pattern, ' ', html_document_with_tags)
text_from_document_re = TextProcessor.keepCharactersInStringWithRegex(
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