# classes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_list_view, name='student_list'),
    path('students/search/', views.student_search_view, name='student_search'),
    path('students/<int:pk>/', views.student_detail_view, name='student_detail'),
    path('classes/', views.class_list_view, name='class_list'),
    path('classes/<int:class_id>/students/', views.class_students_view, name='class_students'),
]
