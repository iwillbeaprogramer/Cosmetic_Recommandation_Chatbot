'''
Created on 2018. 3. 14.

@author: phs
'''
import json
import logging
import pickle
import random

import jpype
from konlpy.tag import Okt
import nltk
from nltk.stem.lancaster import LancasterStemmer
import tflearn

import numpy as np
import tensorflow as tf
#from chatapp.models import Info


#from konlpy.tag import Komoran
class LearningModel(object):
    '''
    Tensorflow 딥러닝으로 생성한 자연어 이해 모델을 읽어들여서 반환한다.
    '''

    ERROR_THRESHOLD = 0.25

    def __init__(self, language, learning_model_files):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)

# ['English',         ['en-US', 'United States']],
# ['한국어',            ['ko-KR']],
# ['中文',             ['cmn-Hans-CN', '普通话 (中国大陆)']],
# ['日本語',           ['ja-JP']],

        self.lang = language
        # Iterates just through value, ignoring the keys
        for key, value in learning_model_files.items():
            if key == "intents_file":
                self.intents_file = value
            elif key == "training_data_file":
                self.training_data_file = value
            elif key == "tflearn_logs_dir":
                self.tflearn_logs_dir = value
            elif key == "tflearn_model_file":
                self.tflearn_model_file = value
            else:
                pass
            
        self.dialog_classes = []
        self.dialog_words = []
        self.train_x = []
        self.train_y = []
        self.tf_learning_model = '' 
        #tflearn.initializations.zeros (shape=None, dtype=tf.float32, seed=None)

        # things we need for NLP
        if (self.lang == 'ko-KR'):
            #komoran = Komoran()
            self.twitter = Okt()
        elif self.lang == 'cmn-Hans-CN':
            pass
        elif self.lang == 'ja-JP':
            pass
        else:
            self.stemmer = LancasterStemmer()

    # import our chat-bot intents file
    def read_dialog_intents_jsonfile(self):
        """
        Dialog Intents JSON파일경로와 파일이름을 인수로 받아  대화 의도와 대화 말뭉치가 정의된 JSON파일을 읽어 JSON객체에 적재하여  반환한다.
        """
#         with open(self.intents_file, 'rt', encoding='UTF8') as json_data:
        with open(self.intents_file, "r", encoding="utf-8") as json_data:
            intents = json.load(json_data)
            
        return intents

    # restore all of our data structures
    def restore_training_data_structures(self):
        """
        Tensorflow 딥러닝 모델 생성에 사용한 자료구조를 읽어 들여서 반환한다.
        """
        # restore all of our data structures
        data = pickle.load( open( self.training_data_file, "rb" ) )
        words = data['words']
        classes = data['classes']
        train_x = data['train_x']
        train_y = data['train_y']
        
        self.dialog_classes = classes
        self.dialog_words = words
        self.train_x = train_x
        self.train_y = train_y
        
    
    # restore all of trained tflearn model file
    def restore_training_model(self):
        """
        Tensorflow 딥러닝으로 생성한 자연어 이해 모델을 읽어들여서 반환한다.
        """
        if not (self.train_x and self.train_y):
            self.restore_training_data_structures()
            
        #다음과 같은 에러 대응(2018.5.10)NotFoundError (see above for traceback): Key Accuracy/Mean/moving_avg_1 not found in checkpoint
        tf.compat.v1.reset_default_graph()
            
        # Build neural network
        net = tflearn.input_data(shape=[None, len(self.train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(self.train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        
        # Define model and setup tensorboard
        model = tflearn.DNN(net, tensorboard_dir = self.tflearn_logs_dir)
        model.load(self.tflearn_model_file)
        
        self.tf_learning_model = model

    def get_words_from_sentence(self, sentence):
        # tokenize the pattern
        if (self.lang == 'ko-KR'):
            # I just called the Twitter class in Django 2.0, and jpype dies with a Java Fatal Error. At this time,
            if jpype.isJVMStarted():
                jpype.attachThreadToJVM()
            pos_result = self.twitter.pos(sentence, norm=True, stem=True)
            sentence_words = [lex for lex, pos in pos_result]
        elif self.lang == 'cmn-Hans-CN':
            pass
        elif self.lang == 'ja-JP':
            pass
        else:
            sentence_words = nltk.word_tokenize(sentence)
            # stem each word
            sentence_words = [self.stemmer.stem(word.lower()) for word in sentence_words]
            
        self.logger.debug("sentence_words : %s" % sentence_words)
            
        return sentence_words
    
    # return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
    def get_bag_of_words(self, sentence, show_details=False):

        # tokenize the pattern
        sentence_words = self.get_words_from_sentence(sentence)

        # bag of words
        if not self.dialog_words:
            self.restore_training_data_structures()
        
        info_bag_of_words = []
        bag = [0]*len(self.dialog_words)  
        for s in sentence_words:
            for i,w in enumerate(self.dialog_words):
                if w == s: 
                    bag[i] = 1
                    info_bag_of_words.append(w)
                    
        if show_details:
            self.logger.debug("found in bag: %s" % info_bag_of_words)
    
        return(np.array(bag))
    
    
    def get_classify(self, sentence):

        if not (self.dialog_classes and self.dialog_words):
            self.restore_training_data_structures()
        # generate probabilities from the model
        if not self.tf_learning_model:
            self.restore_training_model()

        # generate probabilities from the model
        results = self.tf_learning_model.predict([self.get_bag_of_words(sentence, self.dialog_words)])[0]
        # filter out predictions below a threshold
        results = [[i,r] for i,r in enumerate(results) if r>LearningModel.ERROR_THRESHOLD]
        # sort by strength of probability
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append((self.dialog_classes[r[0]], r[1]))
        # return tuple of intent and probability
        self.logger.debug("get_classify() success.. : %s" % return_list)
        return return_list

class NLULearning(LearningModel):
    '''
    Tensorflow 딥러닝으로 자연어 이해 모델을 생성한 한다.
    '''
    def __init__(self, language, learning_model_files):
        '''
        NLULearning Constructor
        '''           
        LearningModel.__init__(self, language, learning_model_files)
        self.dialog_intents = LearningModel.read_dialog_intents_jsonfile(self)
        self.dialog_documents = []

        self.logger = logging.getLogger(__name__)

    def dialog_nlp_processing(self):
        """
         대화 말뭉치를 읽어서 자연어 처리 및  Bag of word 생성
        """
        words = []
        classes = []
        documents = []
        ignore_words = ['?']
        # loop through each sentence in our intents patterns
        for intent in self.dialog_intents['intents']:
            for pattern in intent['patterns']:
                # tokenize each word in the sentence
                # w = nltk.word_tokenize(pattern)
                #pos_result = twitter.pos(pattern, norm=True, stem=True)
                #w = [lex for lex, pos in pos_result]
                w = LearningModel.get_words_from_sentence(self, pattern)
                # add to our words list
                words.extend(w)
                # add to documents in our corpus
                documents.append((w, intent['tag']))
                # add to our classes list
                if intent['tag'] not in classes:
                    classes.append(intent['tag'])
        
        # stem and lower each word and remove duplicates
    #     words = [stemmer.stem(w.lower()) for w in words if w not in ignore_words]
    #     words = sorted(list(set(words)))
        words = [w for w in words if w not in ignore_words]
        words = sorted(list(set(words)))
        
        # remove duplicates
        classes = sorted(list(set(classes)))
        
        self.dialog_classes = classes
        self.dialog_documents = documents
        self.dialog_words = words
    
    def prepare_machine_learning(self):
        """
        Bag of word를 딥러닝 알고리즘 활용을 위한 입력으로 변환
        """
        
        if not (self.dialog_classes and self.dialog_documents and self.dialog_words):
            self.dialog_nlp_processing()
            
        # create our training data
        training = []
        output_row = []
        # create an empty array for our output
        output_empty = [0] * len(self.dialog_classes)
        
        # training set, bag of words for each sentence
        for doc in self.dialog_documents:
            # initialize our bag of words
            bag = []
            # list of tokenized words for the pattern
            pattern_words = doc[0]
            # stem each word
    #         pattern_words = [stemmer.stem(word.lower()) for word in pattern_words]
            # create our bag of words array
            for w in self.dialog_words:
                bag.append(1) if w in pattern_words else bag.append(0)
        
            # output is a '0' for each tag and '1' for current tag
            output_row = list(output_empty)
            output_row[self.dialog_classes.index(doc[1])] = 1
        
            training.append([bag, output_row])
        
        # shuffle our features and turn into np.array
        random.shuffle(training)
        training = np.array(training)
        
        # create train and test lists
        self.train_x = list(training[:,0])
        self.train_y = list(training[:,1])
    
    def create_tensorflow_learning_model(self):
        """
        딥러닝(tensorflow)을 통한 자연어 이해 모델 생성
        """
        if not (self.train_x and self.train_y):
            self.prepare_machine_learning()
        
        # reset underlying graph data
        tf.compat.v1.reset_default_graph()
        # Build neural network
        net = tflearn.input_data(shape=[None, len(self.train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(self.train_y[0]), activation='softmax')
        net = tflearn.regression(net)
        
        # Define model and setup tensorboard
        model = tflearn.DNN(net, tensorboard_dir=self.tflearn_logs_dir)
        # Start training (apply gradient descent algorithm)
        model.fit(self.train_x, self.train_y, n_epoch=1000, batch_size=8, show_metric=True)
        # save the trained model to directory
        model.save(self.tflearn_model_file)
        self.logger.debug("create_tensorflow_learning_model() success... : %s" % self.tflearn_model_file)

        self.tf_learning_model = model
    
    # save all of our data structures
    def save_training_data_structures(self):
        """
        자연어 이해 모델을 관리한다(저장,읽기)
        """
        if not (self.dialog_classes and self.dialog_words):
            self.dialog_nlp_processing()
            
        if not (self.train_x and self.train_y):
            self.prepare_machine_learning()
        
        # save all of our data structures
        pickle.dump( {'words':self.dialog_words, 'classes':self.dialog_classes, 'train_x':self.train_x, 'train_y':self.train_y}, open( self.training_data_file, "wb" ) )
        self.logger.debug("save_training_data_structures() success... : %s" % self.training_data_file)
    
class ChatClient(NLULearning, LearningModel):
    '''
    User 발화에 대응하는 응답을 생성하여 반환한다.
    '''

    def __init__(self, language, learning_model_files):
        '''
        ChatClient Constructor
        '''           
        NLULearning.__init__(self, language, learning_model_files)
        LearningModel.__init__(self, language, learning_model_files)
#         self.dialog_classes
#         self.dialog_words
#         self.train_x
#         self.train_y
#         self.tf_learning_model
#         self.dialog_intents = LearningModel.read_dialog_intents_jsonfile()
#         self.dialog_documents
        # create a data structure to hold user context
        self.context = {}

        self.logger = logging.getLogger(__name__)

    def response(self, sentence, userID='123', show_details=False):
        try:
            results = LearningModel.get_classify(self, sentence)
        except Exception as ex:
            self.logger.error(ex)
        # if we have a classification then find the matching intent tag
        if results:
            # loop as long as there are matches to process
            while results:
                for i in self.dialog_intents['intents']:
                    # find a tag matching the first result
                    if i['tag'] == results[0][0]:
                        # set context for this intent if necessary
                        if 'context_set' in i:
                            if show_details: self.logger.debug('context:', i['context_set'])
                            self.context[userID] = i['context_set']
    
                        # check if this intent is contextual and applies to this user's conversation
                        if not 'context_filter' in i or \
                            (userID in self.context and 'context_filter' in i and i['context_filter'] == self.context[userID]):
                            if show_details: self.logger.debug ('tag:', i['tag'])
                            # a random response from the intent
                            return random.choice(i['responses'])
    
                results.pop(0)

    def create_learning_model(self, show_details=False):
        
        try:
            NLULearning.dialog_nlp_processing(self)
            
            NLULearning.prepare_machine_learning(self)
            
            NLULearning.create_tensorflow_learning_model(self)
            
            NLULearning.save_training_data_structures(self)
            
            if show_details:
                self.logger.debug (len(self.dialog_documents), "documents")
                self.logger.debug (len(self.dialog_classes), "classes", self.dialog_classes)
                self.logger.debug (len(self.dialog_words), "unique stemmed words", self.dialog_words)

        except Exception as ex:
            self.logger.error (ex)
            return False

        self.logger.info("NLU model creation success....")
        return True
            
