'''
Created on 2018. 3. 17.

@author: phs
'''

import os


# Start process
if __name__ == '__main__':
#    test_ChatClient()
#    test_NLULearning()
    pwd = os.getcwd()
    for (path, dirs, files) in os.walk(pwd):
        for dirname in dirs:
            if dirname == 'ArkChatFramework':
                print("[%s]==>%s" % (dirs, os.path.abspath("ArkChatFramework")))
                break
            