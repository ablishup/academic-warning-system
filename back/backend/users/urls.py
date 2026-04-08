# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('current/', views.current_user_view, name='current_user'),
    path('list/', views.user_list_view, name='user_list'),
]
