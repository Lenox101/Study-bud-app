from django.urls import path, include
from . import views

urlpatterns = [
    path('login/', views.LoginView, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),
    path('', views.home, name="home"), #here...we call the home function in the views folder
    path('room/<str:pk>/', views.room, name='room'), #passing in the id into the url(it not yet passed)
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateform, name='update-room'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('update-user/', views.updateUser, name='update-user'),
]