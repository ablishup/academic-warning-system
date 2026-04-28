# classes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_list_view, name='student_list'),
    path('students/search/', views.student_search_view, name='student_search'),
    path('students/<int:pk>/', views.student_detail_view, name='student_detail'),
    path('majors/', views.major_list_view, name='major_list'),
    path('', views.class_list_view, name='class_list'),
    path('<int:pk>/', views.class_detail_view, name='class_detail'),
    path('<int:class_id>/students/', views.class_students_view, name='class_students'),
    path('<int:class_id>/add-students/', views.class_add_students_view, name='class_add_students'),
    path('<int:class_id>/remove-student/', views.class_remove_student_view, name='class_remove_student'),
]
