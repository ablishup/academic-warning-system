from django.urls import path
from . import views

urlpatterns = [
    # 预警记录
    path('', views.WarningRecordListView.as_view(), name='warning-list'),
    path('<int:pk>/', views.WarningRecordDetailView.as_view(), name='warning-detail'),
    path('<int:pk>/resolve/', views.WarningResolveView.as_view(), name='warning-resolve'),

    # 预警计算
    path('calculate/', views.WarningCalculateView.as_view(), name='warning-calculate'),

    # 预警统计
    path('stats/', views.WarningStatsView.as_view(), name='warning-stats'),

    # 学生课程得分
    path('scores/', views.StudentCourseScoreListView.as_view(), name='student-course-scores'),
]
