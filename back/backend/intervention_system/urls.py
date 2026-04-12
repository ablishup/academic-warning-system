"""
干预系统URL配置
"""
from django.urls import path

from . import views

urlpatterns = [
    # 干预记录
    path('', views.InterventionRecordListView.as_view(), name='intervention-list'),
    path('create/', views.InterventionRecordCreateView.as_view(), name='intervention-create'),
    path('<int:pk>/', views.InterventionRecordDetailView.as_view(), name='intervention-detail'),
    path('<int:pk>/update/', views.InterventionRecordUpdateView.as_view(), name='intervention-update'),
    path('<int:pk>/delete/', views.InterventionRecordDeleteView.as_view(), name='intervention-delete'),
    path('<int:pk>/evaluate/', views.InterventionEvaluateView.as_view(), name='intervention-evaluate'),

    # 统计
    path('stats/', views.InterventionStatsView.as_view(), name='intervention-stats'),
    path('student/<int:student_id>/summary/', views.StudentInterventionSummaryView.as_view(), name='student-intervention-summary'),

    # 跟进记录
    path('follow-ups/', views.InterventionFollowUpListView.as_view(), name='follow-up-list'),
    path('follow-ups/create/', views.InterventionFollowUpCreateView.as_view(), name='follow-up-create'),
]
