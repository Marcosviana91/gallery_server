from django.urls import path
from client import views as client_views

urlpatterns = [
    path('login', client_views.home_login, name="login"),
    path('logout', client_views.user_logout, name="logout"),
    path('', client_views.home, name="home"),
    path('user', client_views.home_user, name="home_user"),
    path('user/new', client_views.new_user, name="new_user"),
]
