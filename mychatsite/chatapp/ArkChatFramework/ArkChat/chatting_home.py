'''
Created on 2018. 3. 21.

@author: phs
'''
import os
import logging
import random
from chatapp.ArkChatFramework.DialogManager.tf_learning_model import ChatClient
from chatapp.models import Info


class ChattingHomepage(ChatClient):
    '''
    classdocs
    '''


    def __init__(self, work_dir):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)
        # logger.info("작업디렉토리 : %s" % os.getcwd())
        self.intents_file_name = os.path.join(work_dir, "ArkChatFramework/ArkNLU/DialogIntents/intents.json")
        # logger.info("intents       파일 디렉토리[%s]" % input_file_name)
        self.input_training_data_file_name = os.path.join(work_dir, "ArkChatFramework/ArkNLU/NLUModel/training_data_home_kr")
        # logger.info("training      파일 디렉토리[%s]" % input_training_data_file_name)
        self.tflearn_logs_dir = os.path.join(work_dir, 'ArkChatFramework/ArkNLU/NLUModel/home_tflearn_kr_logs')
        # logger.info("tflearn_logs     디렉토리[%s]" % tflearn_logs_dir)
        self.tflearn_model_file_name = os.path.join(work_dir, 'ArkChatFramework/ArkNLU/NLUModel/model_home_kr.tflearn')
        # logger.info("tflearn_model 파일 디렉토리[%s]" % tflearn_model_file_name)
        #     intents_file, training_data_file, tflearn_logs_dir, tflearn_model_file
        learning_model_files = dict(intents_file = self.intents_file_name, 
                                    training_data_file = self.input_training_data_file_name, 
                                    tflearn_logs_dir = self.tflearn_logs_dir, 
                                    tflearn_model_file = self.tflearn_model_file_name)
        
        ChatClient.__init__(self, 'ko-KR', learning_model_files)
        self.context = {}
        self.criteria_coincidence = 0.50
        self.not_matching_count = 1
        self.previous_not_matching = False
        self.slang_matching_count = 1
        self.previous_slang_matching = False
        self.context_filter_message = "제품과 서비스에 대한 문의 이후에 관련 기술에 대한 설명이 가능합니다."
        self.not_matching_message = "에 대해 이해하지 못했습니다."
        self.usage_guide_message = "여기서는 음성과 문자 채팅으로 아크위드 주식회사의  vision, mission, 제품, 서비스와 관련된 내용만 채팅이 가능합니다."

    def get_answer(self, sentence, userID='123', show_details=False):

        #If a conversation that is not understood during the chatting is in progress more than 3 times,
        # send a usage guide message.
        if self.not_matching_count >= 3:
            self.not_matching_count = 1
            self.previous_not_matching = False
            return self.usage_guide_message

        results = ChatClient.get_classify(self, sentence)
        
        #Echo processing when using bad language three times in a row.
        if self.slang_matching_count >= 3:
            if results[0][0] != 'Slang':
                self.slang_matching_count = 1
                self.previous_slang_matching = False
            else:
                return sentence

        # if we have a classification then find the matching intent tag
        if results:
            # loop as long as there are matches to process
            while results:
                for i in self.dialog_intents['intents']:
                    # find a tag matching the first result
                    if i['tag'] == results[0][0]:
                        # send message when the matching rate of the message is lower than self.criteria_coincidence.
                        if self.criteria_coincidence > results[0][1]:
                            return_message = '"' + sentence + '"' + self.not_matching_message
                            if self.previous_not_matching:
                                self.not_matching_count += 1
                            self.previous_not_matching = True
                            return return_message
                            
                        # check when using bad language three times in a row.
                        if results[0][0] == 'Slang':
                            if self.previous_slang_matching:
                                self.slang_matching_count += 1
                            self.previous_slang_matching = True

                        # set context for this intent if necessary
                        if 'context_set' in i:
                            if show_details: self.logger.debug('context:', i['context_set'])
                            self.context[userID] = i['context_set']
    
                        # check if this intent is contextual and applies to this user's conversation
                        if not 'context_filter' in i or \
                            (userID in self.context and 'context_filter' in i and i['context_filter'] == self.context[userID]):
                            if show_details: self.logger.debug ('tag:', i['tag'])
                            # DB에 tag 정보 저장.
                            info = Info.objects.get(user_id='user')
                            info.tag = i['tag']
                            info.save()
                            # a random response from the intent
                            return random.choice(i['responses'])
                        else:
                            return self.context_filter_message
    
                results.pop(0)

def home_NLULearning(work_dir):

    print("현재 프로세스의 작업 디렉토리 [%s]" % os.getcwd())
    print("부모 디렉토리로 변경[%s]" % os.chdir(os.pardir))
    print("변경후 현재 프로세스의 작업 디렉토리 [%s]" % os.getcwd())
 
    print("intents 파일 디렉토리[%s]" % os.path.join(work_dir, "ArkChatFramework/ArkNLU/DialogIntents/intents.json"))

    input_file_name = os.path.join(work_dir, "ArkChatFramework/ArkNLU/DialogIntents/intents.json")
    print("intents       파일 디렉토리[%s]" % input_file_name)
    
    input_training_data_file_name = os.path.join(work_dir, "ArkChatFramework/ArkNLU/NLUModel/training_data_home_kr")
    print("training      파일 디렉토리[%s]" % input_training_data_file_name)
    
    tflearn_logs_dir = os.path.join(work_dir, 'ArkChatFramework/ArkNLU/NLUModel/home_tflearn_kr_logs')
    print("tflearn_logs     디렉토리[%s]" % tflearn_logs_dir)
    
    tflearn_model_file_name = os.path.join(work_dir, 'ArkChatFramework/ArkNLU/NLUModel/model_home_kr.tflearn')
    print("tflearn_model 파일 디렉토리[%s]" % tflearn_model_file_name)

#     intents_file, training_data_file, tflearn_logs_dir, tflearn_model_file
    learning_model_files = dict(intents_file=input_file_name, 
                                training_data_file=input_training_data_file_name, 
                                tflearn_logs_dir=tflearn_logs_dir, 
                                tflearn_model_file=tflearn_model_file_name)

    bot = ChatClient('ko-KR', learning_model_files)
    print("home NLULearning instance...")
    
    if bot.create_learning_model(show_details=True):
        print("home model creation success....")
    else:
        print("home model creation fail....")

# if __name__=='__main__':
    
#     home_NLULearning()

        