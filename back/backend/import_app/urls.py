# import_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 导入模板下载
    path('template/', views.ImportTemplateDownloadView.as_view(), name='import-template'),

    # 数据导入
    path('activities/', views.ActivityImportView.as_view(), name='import-activities'),
    path('homework/', views.HomeworkImportView.as_view(), name='import-homework'),
    path('exams/', views.ExamImportView.as_view(), name='import-exams'),
    path('enrollments/', views.EnrollmentImportView.as_view(), name='import-enrollments'),

    # 导入记录
    path('logs/', views.ImportLogListView.as_view(), name='import-logs'),
]
