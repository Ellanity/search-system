# custom lib of global variables 
from variables import *

# all definers must get already cleared text 
from text_processor import TextProcessor

# work with files
import os

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

        Summarizer.working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        Summarizer._paths = {
            "DOCUMENTS_DIRECTORY_URL": os.path.join(Summarizer.working_directory, DOCUMENTS_DIRECTORY_URL)
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
            cleared_text = TextProcessor.makeClearedTextFromRawHtmlText(text, True, True)
            tokenized_text = TextProcessor.tokenizeTextByParagraphs(text=cleared_text)
            sentences = SummarizerClassicSummary.sentenceExtraction(tokenized_text)
            
            print("sentence extraction: done")
            return list(sentences)


import spacy
# https://github.com/talmago/spacy_ke
# https://spacy.io/models/it (it_core_news_lg)
# https://spacy.io/models/ru (ru_core_news_lg)
import spacy_ke

class SummarizerKeywordsSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            
        @staticmethod   
        def summarize(text: str, language) -> list:
            
            result = []
            cleared_text = TextProcessor.makeClearedTextFromRawHtmlText(text, True, True, True)
            try:
                nlp = spacy.load(language + "_core_news_lg")
                nlp.add_pipe("yake")
                doc = nlp(cleared_text)

                for keyword, score in doc._.extract_keywords(n=15):
                    result.append(f"{keyword}")
            except Exception as ex:
                print(ex) 
            print("keywords: done")
            return list(result)

class SummarizerMLSummary(Summarizer):
    
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        
        @staticmethod   
        def summarize(text: str) -> list:
            luhn = LuhnSummarizer() #verbose=True)
            result = list()
            result.extend([luhn(text=text, 
                                target_sentences_count=3)])

            print("ml summary: done")
            return list(result)

from collections import Counter

class LuhnSummarizer:
    """
    Метод Луна.
    Статья: https://habr.com/ru/articles/595517/
    Исходник: https://colab.research.google.com/drive/1qeENj0BKdlhrNrPzUFnCpS1EE4l0qrJq#scrollTo=maEg_cazJ082
    
    Основано на https://github.com/miso-belica/sumy/blob/main/sumy/summarizers/luhn.py
    Оригинальная статья: https://courses.ischool.berkeley.edu/i256/f06/papers/luhn58.pdf
    """
    
    """
    @staticmethod
    def sentenize(text):
        paragraphs = TextProcessor.tokenizeTextByParagraphs(text=text)
        sentences = list()
        for paragraph in paragraphs:
            sentences.extend(paragraph) 
        return sentences
    """

    def __init__(
        self,
        significant_percentage = 0.7, # 70% самых частотных токенов мы считаем значимыми.
        min_token_freq = 1, # Кроме того, слова должны встречаться минимум 1 раз.
        max_gap_size = 6, # Максимальное количество подряд идущих незначимых токенов в промежутках.
        # verbose = False # Отладочный вывод для наглядности.
    ):
        self.significant_percentage = significant_percentage
        self.min_token_freq = min_token_freq
        self.max_gap_size = max_gap_size
        self.chunk_ending_mask = [0] * self.max_gap_size
        # self.verbose = verbose

    def __call__(self, text, target_sentences_count):
        # Считаем значимые токены.
        all_significant_tokens = self._getSignificantTokens(text)
        # if self.verbose:
        #     print("Значимые токены: ", all_significant_tokens)

        sentences = TextProcessor.tokenizeTextBySentences(text)

        # Считаем значимости предложений.
        ratings = []
        for sentence_index, sentence in enumerate(sentences):
            # Значимость предложений - максимум из значимостей промежутков.
            sentence_rating = max(self._getChunkRatings(sentence, all_significant_tokens))
            # if self.verbose:
            #     print("\tПРЕДЛОЖЕНИЕ. Значимость: {}, текст: {}".format(sentence_rating, sentence))
            ratings.append((sentence_rating, sentence_index))

        # Сортируем предложения по значимости.
        ratings.sort(reverse=True)

        # Оставляем топовые и собираем реферат.
        ratings = ratings[:target_sentences_count]
        indices = [index for _, index in ratings]
        indices.sort()

        return " ".join([sentences[index] for index in indices])

    """
    def __tokenizeSentenceLocal(sentence):
        sentence = sentence.strip().replace("\xa0", "")
        BAD_POS = ("PREP", "NPRO", "CONJ", "PRCL", "NUMR", "PRED", "INTJ", "PUNCT", "CCONJ", "ADP", "DET", "ADV")
        tokens = [token.lemma_ for token in spacy_model(sentence) if token.pos_ not in BAD_POS]
        tokens = [token for token in tokens if len(token) > 2]
        return tokens
    """

    """
    def __tokenizeTextLocal(sentence):
        all_tokens = []
        for sentence in sentenize(text):
            all_tokens.extend(tokenize_sentence(sentence))
        return all_tokens
    """
    
    def _getSignificantTokens(self, text):
        """ Метод для подсчёта того, какие токены являются значимыми. """
        ### var 1 
        # tokens_counter = Counter(tokenize_text(text))
        ###

        ### var 2
        tokens_with_indexes = TextProcessor.tokenizeTextByWords(text)
        tokens = list(tokens_with_indexes)
        tokens_counter = Counter(tokens)
        ### 
        significant_tokens_max_count = int(len(tokens_counter) * self.significant_percentage)
        significant_tokens = tokens_counter.most_common(significant_tokens_max_count)
        significant_tokens = {token for token, cnt in significant_tokens if cnt >= self.min_token_freq}
        
        return significant_tokens

    def _getChunkRatings(self, sentence, significant_tokens):
        """ Разбиваем предложение на промежтуки и считаем их значимости. """

        # tokens = LuhnSummarizer.__tokenizeSentenceLocal(sentence)
        tokens_with_indexes = TextProcessor.tokenizeTextByWords(sentence)
        tokens = list(tokens_with_indexes)

        chunks, masks = [], []
        in_chunk = False

        for token in tokens:
            is_significant_token = token in significant_tokens
            
            if is_significant_token and not in_chunk:
                in_chunk = True
                masks.append([int(is_significant_token)])
                chunks.append([token])
            elif in_chunk:
                last_mask = masks[-1]
                last_mask.append(int(is_significant_token))
                last_chunk = chunks[-1]
                last_chunk.append(token)
            if not chunks:
                continue

            # Проверяем на наличие 4 подряд идущих незначимых токенов.
            # Если встретили - завершаем промежуток.
            last_chunk_ending_mask = masks[-1][-self.max_gap_size:]
            if last_chunk_ending_mask == self.chunk_ending_mask:
                in_chunk = False
        
        ratings = []
        for chunk, mask in zip(chunks, masks):
            rating = self._getChunkRating(mask, chunk)
            ratings.append(rating)

        if len(ratings) == 0: 
            ratings.append(0.0)

        return ratings

    def _getChunkRating(self, original_mask, chunk): 
        """ Подсчёт значимости одного промежутка """

        # Убираем незначимые токены в конце промежутка
        original_mask = "".join(map(str, original_mask))
        mask = original_mask.rstrip("0")

        end_index = original_mask.rfind("1") + 1
        chunk = chunk[:end_index]
        assert len(mask) == len(chunk)
        chunk = " ".join(chunk)

        # Считаем значимость
        words_count = len(mask)
        assert words_count > 0
        significant_words_count = mask.count("1")
        assert significant_words_count > 0

        rating = significant_words_count * significant_words_count / words_count
        # if self.verbose:
        #     print("ПРОМЕЖУТОК. Значимость: {}, маска: {}, текст: {}".format(rating, mask, chunk))
        
        return rating

