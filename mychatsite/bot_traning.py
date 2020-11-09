"""
대화 말뭉치를 학습합니다.
먼저 어플리케이션 이름, 예로서 장고 프로젝트 폴더에 만든 장고 App이름을 입력합니다.
실행방법 : 
1. python bot_traning.py 실행
2. App이름을 입력
"""
import os
# 홈페이지 대화 말뭉치 텐서플로우 딥러닝 학습모델 챗봇 연결
from chatapp.ArkChatFramework.ArkChat import chatting_home
# 말뭉치 학습
current_work_dir = os.path.dirname(os.path.realpath('__file__'))
print("현재 디렉토리 : [" + current_work_dir + "]")

app_name = input("App이름을 입력하세요: ")

work_dir = os.path.join(current_work_dir, app_name)
print("학습 작업 디렉토리 : [" + work_dir + "]")

chatting_home.home_NLULearning(work_dir)
