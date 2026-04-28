# courses/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<int:pk>/', views.course_detail_view, name='course_detail'),
    path('<int:course_id>/knowledge-points/', views.course_knowledge_points_view, name='course_knowledge_points'),
    path('teacher/', views.teacher_courses_view, name='teacher_courses'),
    path('student/', views.student_courses_view, name='student_courses'),
    path('<int:course_id>/students/', views.course_students_view, name='course_students'),
    path('<int:course_id>/add-students/', views.course_add_students_view, name='course_add_students'),
    path('<int:course_id>/remove-student/', views.course_remove_student_view, name='course_remove_student'),
    # 课程资源相关路由
    path('resources/', views.CourseResourceListCreateView.as_view(), name='course_resource_list_create'),
    path('resources/<int:pk>/', views.CourseResourceDetailView.as_view(), name='course_resource_detail'),
    path('resources/<int:pk>/download/', views.course_resource_download_view, name='course_resource_download'),
]
