from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from chatapp.models import Info

# 홈페이지 대화 말뭉치 텐서플로우 딥러닝 학습모델 챗봇 연결
from chatapp.ArkChatFramework.ArkChat.chatting_home import ChattingHomepage
# 챗봇 프레임워크에서 로깅
import os
import logging

# Create your views here.
context = {}

# 챗봇 초기화
logger = logging.getLogger(__name__)
work_dir = os.path.dirname(os.path.realpath(__file__))
bot = ChattingHomepage(work_dir)

# def index(request):
#     msg = '박형식 홈페이지'
#     return render(request, 'chatapp/index.html', {'message': msg})

def index(request):
    template = loader.get_template('chatapp/base_contents_kr.html')
    # template = loader.get_template('chatapp/base_mycareer_kr.html')
    info = Info.objects.get(user_id='user')
    info.step = 1
    info.tag = ''
    info.category = ''
    info.result = ''
    info.save()
    context = {
         'login_success' : False,
         'latest_question_list': 'test'
    }
    # default_info = Info(user_id="user", step=0, tag="", result="")
    # default_info.save()

    return HttpResponse(template.render(context, request))

def chat_home(request):
    template = loader.get_template('chatapp/chat_home_screen.html')
    context = {
        'login_success' : False,
        'initMessages' : ["다나와","딥러닝 기반 화장품 추천 시스템", "Hi"]
    }
    return HttpResponse(template.render(context, request))

def popup_chat_home(request):
    template = loader.get_template('chatapp/popup_chat_home_screen.html')
    # template = loader.get_template('chatapp/popup_mycareer_chatting_screen.html')
    context = {
        'login_success' : False,
        'initMessages' : ["딥러닝 기반 화장품 추천 시스템", "Hi"]
    }
    # context = {
    #     'login_success' : False,
    #     'initMessages' : ["인공지능 기반 업무자동화 RPA 컨설턴트 직무를 찾고 있는 홍길동입니다.",
    #                       "귀사를 위한 업무자동화 서비스 제공자로서 준비된 저의 역량을 소개해 드리겠습니다."]
    # }
    return HttpResponse(template.render(context, request))

def call_chatbot(request):
    if request.method == 'POST':
        if request.is_ajax():
            userID = request.POST['user']
            sentence = request.POST['message']
            logger.debug("question[{}]".format(sentence))
            answer = make_answer(sentence, userID)
            print(answer)
            logger.debug("answer[{}]".format(answer))
            return HttpResponse(answer)
    return ''

def make_answer(sentence, userID):
    cate_list = ["스킨", "로션", "에센스", "앰플", "크림"] # category list
    filter_list = ["복합성","건성","지성","쿨톤","웜톤","잡티","미백","주름","각질","트러블","블랙헤드",\
                    "피지과다","민감성","모공","탄력","홍조","아토피"] # 17개 태그 리스트
    type_list = filter_list[:3] # 피부 타입 리스트
    tone_list = filter_list[3:5] # 피부 톤 리스트
    porb_list = filter_list[5:] # 피부 고민 리스트

    answer = bot.get_answer(sentence, userID)  # intents['responses']
    info = Info.objects.get(user_id='user')
    step = info.step
    tag = info.tag
    category = info.category
    result = info.result
    result_list = result.split()

    if step == 1: # 제품 카테고리 선택 단계
        if tag in cate_list:
            info.step = step + 1
            info.category= tag
            info.save()
            answer += "\n피부 타입을 입력해주세요."
        else:
            answer = "잘못 입력하셨습니다." + tag + " 제품 카테고리를 입력해주세요."

    elif step == 2: # 피부 타입 선택 단계
        if tag in type_list:
            info.step = step + 1
            info.result += tag
            info.save()
            answer += "\n피부톤을 입력해주세요."
        else:
            answer = "잘못 입력하셨습니다." + tag + " 피부 타입을 입력해주세요."

    elif step == 3: # 피부톤 선택 단계
        if tag in tone_list:
            info.step = step + 1
            info.result += (' ' + tag)
            info.save()
            answer += "\n피부 고민을 입력해주세요."
        else:
            answer = "잘못 입력하셨습니다." + tag + " 피부톤을 입력해주세요."

    elif step == 4: # 피부 고민 선택 단계
        if tag in porb_list:
            if tag in result_list[2:]:
                answer = "이미 입력한 피부 고민입니다. 다른 피부 고민이 있으면 추가로 입력해주세요"
            else:
                info.result += (' ' + tag)
                answer += "\n다른 피부 고민이 있으면 추가로 입력해주세요"
        elif tag == 'end':
            name, price, url = predict_code_value(category, result_list)
            answer = "제품: " + name + "\n가격: " + price + "\n링크: " + url
            info.step = 1
            info.tag = None
            info.result = ''
            info.save()
        else:
            answer = "잘못 입력하셨습니다." + tag + " 피부 고민을 입력해주세요."

    else:
        answer = "Error"

    return answer

#############################

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from keras.utils import to_categorical
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import ModelCheckpoint
import os

def readdata_and_savemodel(filename):
    #INPUT = 1000001000100010001.csv,1000001000100010002.csv,1000001000100010003.csv,1000001000100010004.csv,1000001000100010011.csv
    #OUTPUT : 모델이 경로에 저장됨
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.feature_extraction.text import TfidfTransformer
    from keras.utils import to_categorical
    from sklearn.preprocessing import LabelEncoder,OneHotEncoder
    from keras.models import Sequential
    from keras.layers import Dense
    from keras.callbacks import ModelCheckpoint
    import os
    
    # 파일로부터 X,Y데이터를 읽어서 전처리(백터화 및 원핫인코딩)
    x_data,y_data = load_from_dataset(filename) #읽어옴
    x_train = make_x_train(x_data) #전처리
    y_train = make_y_train(y_data) #전처리
    name=filename.split(".")[0] #파일이름에서 카테고리 키워드를 받아옴

    #모델 저장경로 설정
    MODEL_DIR = './model/'
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)
    modelpath = '/model/'+name+'.hdf5'
    checkpointer = ModelCheckpoint(filepath=modelpath, monitor = 'loss', save_best_only=True, verbose=1)

    #모델 선언 및 layer설정
    model = Sequential()
    model.add(Dense(64,input_dim = len(x_train[0]),activation='relu'))
    model.add(Dense(128,activation='relu'))
    model.add(Dense(len(y_train[0]),activation='softmax'))
    model.compile(loss = 'categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
    
    #가장 마지막에 있는 모델 하나만 저장
    history = model.fit(x_train,y_train,epochs=2000,verbose=1,batch_size=1,callbacks=[checkpointer])

    
def make_y_train(result2):
    #INPUT : load_from_dataset로 읽어온 Y값 전처리 함수
    import numpy as np
    from keras.utils import to_categorical
    from sklearn.preprocessing import OneHotEncoder,LabelEncoder
    f=LabelEncoder()
    f.fit(result2)
    y_train = f.transform(result2)
    #OUTPUT = [0....1....0] 원핫벡터
    return to_categorical(y_train)

def x_onehot_encoding(input_list):
    # X데이터 Preprocessing 하는 1단계함수 직접사용할 일이 거의 없음
    # make_x_train 함수에서 사용됨
    # INPUT = ['복합성', '웜톤', '트러블', '모공', '민감성', '잡티']
    name_list=["복합성","건성","지성","쿨톤","웜톤","잡티","미백","주름","각질","트러블","블랙헤드","피지과다","민감성","모공","탄력","홍조","아토피"]
    result=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for i in input_list:
        index = name_list.index(i)
        result[index]+=1
    # OUTPUT = [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0]
    return result

def make_x_train(result1):
    #INPUT : load_from_dataset로 읽어온 Y값 전처리 함수
    # X데이터를 가공하는함수
    # 내부에서 x_onehot_encoding을 사용하며 for문으로 모든 x값을 처리
    import numpy as np
    temp=[]
    result = list(result1)
    for i in result:
        temp.append(x_onehot_encoding(i))
    #여기서 나온 값을 바로 model.fit 시키면 됨
    #OUTPUT
    #[
    #    [1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
    #    [1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],
    #    [1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0]
    #]
    return np.array(temp)

def load_from_dataset(string):
    # INPUT : string은 csv 파일 이름
    import pandas as pd
    #df = pd.read_csv('C:/Users/kimsuhyun/Dropbox/Cosmetic_Recommandation_Chatbot/mychatsite/chatapp/model/'+string,encoding='utf-8')
    df = pd.read_csv('C:/Users/Administrator/Dropbox/Cosmetic_Recommandation_Chatbot/mychatsite/chatapp/model/'+string,encoding='utf-8')
    y_data = df.values[:,1]
    x_data = df.values[:,-1]
    temp=[]
    for i in x_data:
        willappend = i.split(" ")
        willappend.pop()
        temp.append(willappend)
    # csv파일로 부터 x값, y값을 각각 읽어서 반환
    # 아직 전처리 안됨
    return temp,y_data

def load_model_hdf5(filename):
    # INPUT : 1000001000100010001.csv
    # hdf파일 읽어옴
    from tensorflow import keras
    #loaded_model = keras.models.load_model("C:/Users/kimsuhyun/Dropbox/Cosmetic_Recommandation_Chatbot/mychatsite/chatapp/model/"+filename)
    loaded_model = keras.models.load_model("C:/Users/Administrator/Dropbox/Cosmetic_Recommandation_Chatbot/mychatsite/chatapp/model/"+filename)
    # load한 모델을 리턴
    return loaded_model

def predict_code_value(category_name,input_value):
    # categoty_name  ex)로션, 세럼, 토너
    #input_value = ["복합성",등등등]
    categoryno = Name_to_CategoryNo(category_name)
    import numpy as np
    import pandas as pd
    b=np.array(x_onehot_encoding(input_value)).reshape(1,-1)
    model = load_model_hdf5(categoryno+'.hdf5')
    x,y=load_from_dataset(categoryno+'.csv')
    df = pd.read_csv("C:/Users/Administrator/Dropbox/Cosmetic_Recommandation_Chatbot/mychatsite/chatapp/model/"+categoryno+'.csv',encoding='utf-8')
    #df = pd.read_csv("C:/Users/kimsuhyun/Dropbox/Cosmetic_Recommandation_Chatbot/mychatsite/chatapp/model/"+categoryno+'.csv',encoding='utf-8')
    code = y[model.predict_classes(b)]
    url = 'https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?goodsNo={}&dispCatNo={}'.format(code[0],categoryno)
    #          'A000000103112'
    # 이름 가격 url
    row = df[df['id']==code[0]]
    pre_price = row['price'].astype(str)
    pre_name = row['name'].astype(str)
    price=text_processing(pre_price.iloc[0])
    name=text_processing(pre_name.iloc[0])
    return name,price,url 

def get_url(code,filename):
    #url을 가공해서 리턴하는 함수
    catno = filename.split(".")[0]
    base_url='https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?'+'goodsNo={}&dispCatNo={}'.format(code,catno)
    # 필요에 따라 print함수와 함께 사용
    return base_url

def GoodsNo_to_Name(goodsnum):
    # 상품번호에서 이름으로 변환하는 함수
    if goodsnum=='1000001000100010001' or goodsnum==1000001000100010001:
        return "스킨/토너"
    elif goodsnum=='1000001000100010002' or goodsnum==1000001000100010002:
        return "로션"
    elif goodsnum=='1000001000100010003' or goodsnum==1000001000100010003:
        return "에센스/세럼"
    elif goodsnum=='1000001000100010011' or goodsnum==1000001000100010011:
        return "앰플"
    elif goodsnum=='1000001000100010004' or goodsnum==1000001000100010004:
        return "크림"
    else:
        print("없는 코드입니다.")
        return 

def Name_to_CategoryNo(category_name):
    # 이름에서 상품번호로 변환하는 함수
    if category_name=='토너' or category_name=='스킨' or category_name=='스킨토너' or category_name=='토너스킨' or category_name=="스킨/토너" or category_name=="토너/스킨":
        return '1000001000100010001'
    elif category_name=='로션':
        return '1000001000100010002'
    elif category_name=='에센스' or category_name=='세럼' or category_name=='새럼' or category_name=='에센스/세럼' or category_name=='에센스/새럼' or category_name=='세럼/에센스' or category_name=='새럼/에센스':
        return '1000001000100010003'
    elif category_name=='앰플' or category_name=='엠플':
        return '1000001000100010011'
    elif category_name=='크림':
        return '1000001000100010004'
    else:
        print("없는 코드코드입니다.")
        return 

def get_url(goods_num,filename):
    #url을 가공해서 리턴하는 함수
    catno = filename.split(".")[0]
    base_url='https://www.oliveyoung.co.kr/store/goods/getGoodsDetail.do?'+'goodsNo={}&dispCatNo={}'.format(goods_num,catno)
    # 필요에 따라 print함수와 함께 사용
    return base_url

def text_processing(string):
    # 택스트 가공함수
    # INPUT string="한번 써보고 너무 좋아서(^_^)매번 구입해서 사용 중이에요:). 바이오더마 제품이라 믿음도 가요.물스킨 타입이라 닦아내는 용도로 쓰고 있는 데 적당히 쿨링감 있고 좋아요저는 건성이긴 하지만 이 제품은 가볍고 깨끗한 느낌이라지성한테 더 잘 어울리는 제품인 거 같아요보습이 강하지는 않고 진정이랑 산뜻함?? 이런 느낌이 강해요. 향도 쎄지 않은 그냥 쿨한 느낌이고 어름에 쓰기 딱 좋은 거 같아요냉장고에 보관하고 사용 중인데 더 피부진정에도움이 되는 거 같아요.자극도 없이 순하고 세네통 넘게 사용 중이에요 남자친구도 안끈적거리고 시원하고 좋다고 애용중입니다:)"
    # 줄바꿈, 특수기호, 불규칙한 인덴트 제거
    file = open("test.txt",'w',encoding='utf-8')
    file.write(string)
    file.write("\n")
    file.close()
    file=open("test.txt",'r',encoding='utf-8')
    result=''
    while True:
        line = file.readline()
        if not line:
            break
        result+=line.replace("\n",'')
    file.close()
    return result

def category_tag_to_dictionary(category_name,input_value):
    a,b,c = predict_code_value(category_name,input_value)
    result = {
        'name' : a,
        "price" : b,
        "url" : c,
    }
    return result

#readdata_and_savemodel("1000001000100010001.csv")

#############3
# def db_initializer():
    # step = 1
    # tag = None
    # category = None
    # result = None