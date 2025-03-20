from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('inbox/', views.inbox, name='inbox'),
    path('decrypt/<int:message_id>/', views.decrypt_message, name='decrypt_message'),
    path('signup/', views.signup, name='signup'),
    path('users/', views.user_list, name='user_list'),
]