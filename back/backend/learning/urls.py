from django.urls import path
from . import views

urlpatterns = [
    # 学习活动
    path('activities/', views.LearningActivityListView.as_view(), name='learning-activities'),
    path('activities/summary/', views.LearningActivitySummaryView.as_view(), name='learning-activity-summary'),

    # 作业
    path('homework/assignments/', views.HomeworkAssignmentListView.as_view(), name='homework-assignments'),
    path('homework/assignments/<int:pk>/', views.HomeworkAssignmentDetailView.as_view(), name='homework-assignment-detail'),
    path('homework/submissions/', views.HomeworkSubmissionListView.as_view(), name='homework-submissions'),
    path('homework/submissions/<int:pk>/', views.HomeworkSubmissionDetailView.as_view(), name='homework-submission-detail'),
    path('homework/stats/', views.StudentHomeworkStatsView.as_view(), name='homework-stats'),

    # 考试
    path('exams/assignments/', views.ExamAssignmentListView.as_view(), name='exam-assignments'),
    path('exams/assignments/<int:pk>/', views.ExamAssignmentDetailView.as_view(), name='exam-assignment-detail'),
    path('exams/results/', views.ExamResultListView.as_view(), name='exam-results'),
    path('exams/results/<int:pk>/', views.ExamResultDetailView.as_view(), name='exam-result-detail'),
    path('exams/stats/', views.StudentExamStatsView.as_view(), name='exam-stats'),

    # 综合统计
    path('course-stats/', views.CourseLearningStatsView.as_view(), name='course-learning-stats'),
]
