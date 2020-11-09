# import json
# import logging
# import logging.config
# import os
# 
# from .DialogManager.tf_learning_model import LearningModel, NLULearning, ChatClient
# 
# 
# print("ArkChatFramework 작업디렉토리 : %s" % os.getcwd())  
# 
# # If applicable, delete the existing log file to generate a fresh log file during each execution
# if os.path.isfile("ArkChatFramework_logging.log"):
#     os.remove("ArkChatFramework_logging.log")
#  
# with open("ArkChatFramework_logging_configuration.json", 'r') as logging_configuration_file:
#     config_dict = json.load(logging_configuration_file)
#  
# logging.config.dictConfig(config_dict)
#  
# # Log that the logger was configured
# logger = logging.getLogger(__name__)
# logger.info('Completed configuring logger()!')