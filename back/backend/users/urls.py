# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
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
    # 学生搜索接口
    path('search/', views.search_students_view, name='search_students'),
    # 辅导员班级管理接口
    path('counselors/<int:pk>/classes/', views.counselor_classes_view, name='counselor_classes'),
    path('counselors/<int:pk>/assign-classes/', views.assign_class_to_counselor_view, name='assign_class_to_counselor'),
    path('counselors/<int:pk>/remove-class/', views.remove_class_from_counselor_view, name='remove_class_from_counselor'),
    path('available-classes/', views.available_classes_view, name='available_classes'),
    # 辅导员Dashboard统计
    path('counselor/dashboard-stats/', views.counselor_dashboard_stats_view, name='counselor_dashboard_stats'),
    # 院系列表
    path('departments/', views.department_list_view, name='department_list'),
    # 管理员Dashboard统计
    path('admin/dashboard-stats/', views.admin_dashboard_stats_view, name='admin_dashboard_stats'),
]
