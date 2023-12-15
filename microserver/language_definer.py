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

# work with text
import re


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
        
        # ngram
        if not NGRAMM_SIZE: 
            raise Exception("Can not find variable NGRAMM_SIZE")
        # alphabet
        if not LANGUAGES_ALPHABETS: 
            raise Exception("Can not find variable LANGUAGES_ALPHABETS")
        # neural network
        if not NEURAL_NETWORK_DATA_DIRECTORY_URL: 
            raise Exception("Can not find variable NEURAL_NETWORK_DATA_DIRECTORY_URL")
        if not MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN: 
            raise Exception("Can not find variable MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN")
        
        # for text handling
        if not ALLOWED_DICTIONARY: 
            raise Exception("Can not find variable ALLOWED_DICTIONARY")
        if not DELIMETERS_OF_TEXT: 
            raise Exception("Can not find variable DELIMETERS_OF_DOCUMENT")

        Definer.__working_directory: str = WORKING_DIRECTORY if not None else os.getcwd()
        
        # create a directories if not exist
        Definer._paths = {
            "DOCUMENTS_DIRECTORY_URL": os.path.join(Definer.__working_directory, DOCUMENTS_DIRECTORY_URL),
            "DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL),
            "DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL),
            "NEURAL_NETWORK_DATA_DIRECTORY_URL": os.path.join(Definer.__working_directory, 
                DOCUMENTS_FOR_DEFINER_DIRECTORY_URL, NEURAL_NETWORK_DATA_DIRECTORY_URL)
        }

        for _, path in Definer._paths.items():
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
    
    # get source documents from dir, divided by language
    @staticmethod
    def _getSourcesDocumentsPaths() -> dict:
        documents_by_language = {} 
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = Definer.__findDocumentsInDirectory(
                os.path.join(Definer._paths["DOCUMENTS_FOR_DEFINER_SOURCES_DIRECTORY_URL"], language))
            documents_by_language[language] = language_sources_documents_paths
        return documents_by_language
            
    # get source documents from dir, divided by language
    @staticmethod
    def _getProfilesDocumentsPaths(definition_type_str) -> dict:
        documents_by_language = {} 
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = Definer.__findDocumentsInDirectory(
                os.path.join(Definer._paths["DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL"], definition_type_str, language))
            
            documents_by_language[language] = language_sources_documents_paths
        return documents_by_language
            
    # remove source documents from dir, by type of definition
    @staticmethod
    def _removeProfileDocumentsByType(definition_type_str) -> None:
        
        for language in LANGUAGES_TO_DEFINE:
            language_sources_documents_paths = os.path.join(
                Definer._paths["DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL"], 
                definition_type_str, 
                language)
            
            try:
                if os.path.exists(language_sources_documents_paths):
                    def onRmError(func, path, exc_info):
                        # path contains the path of the file that couldn't be removed
                        # let's just assume that it's read-only and unlink it.
                        os.chmod(path, stat.S_IWRITE)
                        os.unlink(path)
                        os.remove(path)

                shutil.rmtree(language_sources_documents_paths, onerror = onRmError)    
                # os.remove(language_sources_documents_paths)
            
                if not os.path.exists(language_sources_documents_paths):
                    os.makedirs(language_sources_documents_paths, stat.S_IWRITE)
            except:
                pass            
        return 


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
                        
                html_text = TextProcessor.makeClearedTextFromRawHtmlText(html_document_with_tags)
                # html_text = DefinerNGrammsMethod._getClearTextFromHtml(html_document_with_tags)
                
                ngrams_profiles[language][os.path.join(os.path.split(current_path)[1])] = \
                    DefinerNGrammsMethod.__createNGramsProfileForText(html_text)
        return ngrams_profiles

    # create profile for got text 
    @staticmethod
    def __createNGramsProfileForText(text): 
        created_ngrams_list: list = []
        
        def getNgramsFromWord(word, ngram_size) -> list:
            ngrams = list()
            if bool(re.search(r'\d', word)) or type(word) != str:
                return []
            elif len(word) <= ngram_size:
                ngrams.append(word)
            else:
                for i in range(len(word) - (ngram_size - 1)):
                    ngram = word[i:i + ngram_size]
                    ngrams.append(ngram)
            return ngrams
            
        for word in text.split(" "):
            if word != "" and word is not None:
                ngrams = getNgramsFromWord(word, NGRAMM_SIZE)
                created_ngrams_list += ngrams

        created_ngrams: dict = {}
        for ngram in created_ngrams_list:
            if created_ngrams.get(ngram):
                created_ngrams[ngram] += 1
            else:
                created_ngrams[ngram] = 1

        ngrams_to_return = list(dict(sorted(created_ngrams.items(), key=lambda x:x[1], reverse=True)))
        return ngrams_to_return 
    
    # create or rewrite doc of ngrams for every found source doc 
    # and created profiles for them 
    @staticmethod
    def __saveNgramsProfiles(ngrams_profiles):
        definition_type_str="ngrams"
        DefinerNGrammsMethod._removeProfileDocumentsByType(definition_type_str=definition_type_str)
        
        # documents_by_language = {} 
        ngrams_dir_name = Definer._paths["DOCUMENTS_FOR_DEFINER_PROFILES_DIRECTORY_URL"]
        for language in ngrams_profiles.keys():
            for document_in_lang in ngrams_profiles[language].keys():
                # dict ngrams_profiles[language][document_in_lang]                
                profiles_documents_path_full = os.path.join(ngrams_dir_name, definition_type_str, language, document_in_lang)
                ### write in file 
                with codecs.open(profiles_documents_path_full, "w+", encoding="utf-8") as profile_file:
                    json.dump(ngrams_profiles[language][document_in_lang], profile_file)
        return 
    
    # update profiles of tests documents, create them or rewrite
    def updateDefinerDocumentsProfiles(self):
        ngrams_profiles = DefinerNGrammsMethod.__documentsNGramsProfilesFromSources()
        self.__saveNgramsProfiles(ngrams_profiles)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    def __calculatingTheOutOfPlaceMeasureBetweenTwoProfiles(ngram_profile_1, ngram_profile_2):
        distance_measure = 0
        # ngram_profile_1 = list(ngram_profile_1)
        # ngram_profile_2 = list(ngram_profile_2)
        max_diff = len(ngram_profile_1)
        for ngram in ngram_profile_1:
            if ngram in ngram_profile_2:
                distance_measure += abs(ngram_profile_1.index(ngram) - ngram_profile_2.index(ngram))  
            else:
                distance_measure += max_diff
        return distance_measure

    # returns dict {"path": path, "language": language_of_doc, "profile": ngrams}
    @staticmethod
    def __findNearestNgramProfile(ngram_profile, ngram_profiles) -> dict:
        nearest_document = {}
        for language in ngram_profiles.keys():
            for profile_path in ngram_profiles[language]:
                profile = None
                if os.path.isfile(profile_path):
                    with codecs.open(profile_path, "r", encoding="utf-8") as profile_file:
                        json_content = profile_file.read()
                        profile = json.loads(json_content)
                #
                if profile and type(language) == str and len(language) == 2:
                    distance_measure = DefinerNGrammsMethod.__calculatingTheOutOfPlaceMeasureBetweenTwoProfiles(
                        ngram_profile, profile)
                    if nearest_document == {}:
                        nearest_document = {"path":profile_path, "language":language,"profile":profile, "distance_measure":distance_measure}
                    else:
                        if nearest_document["distance_measure"] > distance_measure:
                            nearest_document = {"path": profile_path, "language": language, "profile": profile, "distance_measure":distance_measure}
                    
        return nearest_document

    # create profile for got text
    # compare it with created before profiles of tests documents
    def define(self, text: str) -> str: 
        ngram_profile = DefinerNGrammsMethod.__createNGramsProfileForText(text)
        ngram_profiles = Definer._getProfilesDocumentsPaths("ngrams")
        nearest_document = DefinerNGrammsMethod.__findNearestNgramProfile(
            ngram_profile=ngram_profile, 
            ngram_profiles=ngram_profiles)
        
        print("ngram: ", nearest_document["language"])
        result = nearest_document["language"]
        return result

class DefinerAlphabetMethod(Definer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def define(text: str) -> str:
        text = TextProcessor.makeClearedTextFromRawHtmlText(text)
        
        chars = {}
        for char in text:
            if char == " ": continue
            if not chars.get(char): chars[char] = 1 
            else: chars[char] += 1 

        languages_weights = {language: 0 for language in LANGUAGES_TO_DEFINE}
        for char in chars:
            for language in LANGUAGES_TO_DEFINE:
                if char in LANGUAGES_ALPHABETS[language]:
                    languages_weights[language] += chars[char]
        
        result = max(languages_weights, key=languages_weights.get)
        if languages_weights[result] == 0:
            return ""
        
        print("alph: ", result)
        return result

# TODO: need to make CUDA GPU trainig
# https://stackoverflow.com/questions/40690598/can-keras-with-tensorflow-backend-be-forced-to-use-cpu-or-gpu-at-will
# os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np
import keras
from keras.layers import Dense, Embedding, LSTM
from keras.models import model_from_json
from keras.utils import pad_sequences, to_categorical

# for charts 
import matplotlib.pyplot as plt

# https://cloud.croc.ru/blog/about-technologies/keras-i-tensorflow-klassifikatsiya-teksta/
class DefinerNeuralNetworkMethod(Definer):    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DefinerNeuralNetworkMethod.model_path = \
            os.path.join(Definer._paths["NEURAL_NETWORK_DATA_DIRECTORY_URL"], "model.json")
        DefinerNeuralNetworkMethod.weights_path = \
            os.path.join(Definer._paths["NEURAL_NETWORK_DATA_DIRECTORY_URL"], "weights.h5")

    class NeuralNetwork:
                        
        def __init__(self):
            pass

        @staticmethod   
        def defineTextLanguage(text: str) -> str:
            # create input data for prediction
            text = TextProcessor.makeClearedTextFromRawHtmlText(text)
            tokens_with_indexes = DefinerNeuralNetworkMethod.NeuralNetwork.tokenizeText(text)
            
            sequences: list = []
            sequences.append(list())

            count_of_tokens_in_current_list = 0
            for token_index in list(tokens_with_indexes.values()):
                sequences[-1].append(token_index)
                count_of_tokens_in_current_list += 1
                if count_of_tokens_in_current_list >= MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN:
                    sequences.append(list())
            
            data_for_input_layer = pad_sequences(sequences=sequences, 
                                                 maxlen=MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN)

            # load model from file
            model_path = DefinerNeuralNetworkMethod.model_path
            weights_path = DefinerNeuralNetworkMethod.weights_path
            if not os.path.exists(model_path) or not os.path.exists(weights_path):
                raise Exception("Need to train model before predict")
            
            # load model

            loaded_model_json = None
            
            # print("model_path: ", model_path)
            with codecs.open(model_path, 
                             mode="r", 
                             encoding="utf-8") as model_file:
                loaded_model_json = model_file.read()
                model = model_from_json(loaded_model_json)

            if model is None:
                raise Exception("Model of neural network was not loaded")
            
            # load weights
            model.load_weights(weights_path)

            # predict            
            predictions = model.predict(data_for_input_layer)
            expected_results = DefinerNeuralNetworkMethod.NeuralNetwork.getExpectedResultsForNetworkWork()
            
            # # # # # most common language 
            # for evert predict (it returns result for every language) 
            # finding indexd of max value
            indexes = []
            for prediction in predictions:
                max_predicted_value = max(prediction)
                index_of_max_predicted_value = 0
                for index in prediction:
                    if index == max_predicted_value:
                        break
                    index_of_max_predicted_value += 1
                indexes.append(index_of_max_predicted_value)

            # print(indexes.count(0), indexes.count(1))
            most_common_index = max(set(indexes), key = indexes.count)
            
            for language in expected_results:
                if expected_results[language] == most_common_index:
                    return language
                    
            return ""

        @staticmethod           
        def tokenizeText(text: str) -> dict:
            tokens = TextProcessor.tokenizeText(text)
            
            def normilizeTokens(tokens: dict) -> dict:
                for token in tokens.keys():
                    tokens[token] = tokens[token] / MAX_TOKEN_INDEX 
            
            # normilizeTokens(tokens)
            return tokens 

        @staticmethod    
        def getExpectedResultsForNetworkWork():
            expected_results = {}
            num_of_result = 0
            for result in LANGUAGES_TO_DEFINE:
                expected_results[result] = num_of_result
                num_of_result += 1
            return expected_results

        @staticmethod    
        def createNetwork():
            # model 
            model = keras.Sequential()
            model.add(Embedding(MAX_TOKEN_INDEX, MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN))
            model.add(LSTM(32, dropout=0.2, recurrent_dropout=0.2))
            model.add(Dense(len(LANGUAGES_TO_DEFINE), activation='sigmoid'))

            model.compile(loss='binary_crossentropy',
                        optimizer='adam',
                        metrics=['accuracy'])

            return model

        @staticmethod    
        def getDataForTraining() -> dict:

            sources_docs_paths = Definer._getSourcesDocumentsPaths()

            texts_for_training = {}

            for language in LANGUAGES_TO_DEFINE:
                texts_for_training[language] = list()
                texts_for_training[language].append(list())

            tokens_vocabulary = set()

            for language in sources_docs_paths.keys():

                for current_path in sources_docs_paths[language]:
                    print("tokenizing text: ", current_path)
                    html_document_with_tags = ""
                
                    if os.path.isfile(current_path):
                        with codecs.open(current_path, "r", encoding="utf-8") as file:
                            html_document_with_tags = file.read()
                            
                    html_text = TextProcessor.makeClearedTextFromRawHtmlText(html_document_with_tags)
                    
                    list_of_indexes_from_text = \
                        list(DefinerNeuralNetworkMethod.NeuralNetwork.tokenizeText(html_text).values())
                    
                    # split text by max_len_of_input
                    count_of_tokens_in_current_list = 0
                    for token in list_of_indexes_from_text:
                        texts_for_training[language][-1].append(token)
                        count_of_tokens_in_current_list += 1
                        if count_of_tokens_in_current_list >= MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN:
                            texts_for_training[language].append(list())
                        # vocab of input data
                        tokens_vocabulary.add(token)

            data_for_input_layer: list = [] 
            data_for_otput_layer: list = [] 
            expected_results = DefinerNeuralNetworkMethod.NeuralNetwork.getExpectedResultsForNetworkWork()
            
            # create pad input and ouputd data
            sequences = []
            for language in LANGUAGES_TO_DEFINE:
                for text in texts_for_training[language]:
                    sequences.append(np.array(text))
                # for every input index set output of language 
                data_for_otput_layer.extend([expected_results[language]] * len(texts_for_training[language]))
               
            data_for_input_layer = pad_sequences(sequences=sequences, 
                              maxlen=MAX_NUM_OF_TOKENS_IN_INPUT_SEQUENCE_FOR_NN)
            
            num_of_languages = len(LANGUAGES_TO_DEFINE)
            data_for_otput_layer = to_categorical(data_for_otput_layer, num_of_languages)

            return {
                    "input": np.array(data_for_input_layer),
                    "output": np.array(data_for_otput_layer)
                }

        @staticmethod    
        def trainNetwork(data_to_train) -> None:
            model = DefinerNeuralNetworkMethod.NeuralNetwork.createNetwork()

            batch_size = 32
            epochs = 3 #500
            # print(data_to_train["input"], data_to_train["output"])
            history = model.fit(data_to_train["input"],
                                data_to_train["output"],
                                batch_size=batch_size,
                                epochs=epochs,
                                verbose=True)
            
            # save model
            model_json = model.to_json()
            with codecs.open(DefinerNeuralNetworkMethod.model_path, 
                             mode="w+", 
                             encoding="utf-8") as model_file:
                model_file.write(model_json)
            
            # save weights
            model.save_weights(DefinerNeuralNetworkMethod.weights_path)
            
            # show chart 
            try:
                plt.plot(history.history["loss"])
                plt.grid(True)
                plt.show()
            except Exception as ex:
                print(ex)

            return
 
    @staticmethod
    def updateDefinerNeuralNetworkWeights() -> None:
        data_for_training = DefinerNeuralNetworkMethod.NeuralNetwork.getDataForTraining()
        DefinerNeuralNetworkMethod.NeuralNetwork.trainNetwork(data_for_training)
        return

    @staticmethod
    def define(text: str) -> str:
        result = DefinerNeuralNetworkMethod.NeuralNetwork.defineTextLanguage(text)
        print("nn: ", result)
        return result
