from django.urls import path

from chatapp import views


urlpatterns = [
    path('', views.index, name='index'),
    path('chat_home', views.chat_home, name='chat_home'),
    path('popup_chat_home', views.popup_chat_home, name='popup_chat_home'),
    path('call_chatbot', views.call_chatbot, name='call_chatbot'),
]