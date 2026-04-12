# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('current/', views.current_user_view, name='current_user'),
    path('list/', views.user_list_view, name='user_list'),
    path('<int:pk>/', views.user_detail_view, name='user_detail'),
    path('<int:pk>/reset-password/', views.reset_password_view, name='reset_password'),
    path('<int:pk>/toggle-status/', views.toggle_user_status_view, name='toggle_status'),
    # 教师/辅导员信息接口
    path('teachers/', views.teacher_list_view, name='teacher_list'),
    path('teachers/<int:pk>/', views.teacher_detail_view, name='teacher_detail'),
    path('counselors/', views.counselor_list_view, name='counselor_list'),
    path('counselors/<int:pk>/', views.counselor_detail_view, name='counselor_detail'),
    path('profile/teacher/', views.teacher_profile_view, name='teacher_profile'),
    path('profile/counselor/', views.counselor_profile_view, name='counselor_profile'),
]
