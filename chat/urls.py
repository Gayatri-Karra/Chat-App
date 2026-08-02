from django.urls import path

from . import views

urlpatterns = [
    path('log-in/', views.log_in, name="log_in"),
    path('sign-up/', views.sign_up, name="sign_up"),
    path('log_out/', views.log_out, name="log_out"),
    path('', views.user_page_view, name="user_chats"),
    path('chat/<str:pk>/', views.messages, name="chat"),
    path('api/chat/<str:pk>/', views.api_messages, name="api-chat"),

    path('new-friend-request/', views.new_friend_request, name="new-friend-request"),

    path('friend-request/<int:friend_request_id>/<str:friend_request_response>/', views.friend_requests_view, name="friend_request"),

]