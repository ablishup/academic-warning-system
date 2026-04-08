from django.urls import path
from . import views

urlpatterns = [
    # 干预记录CRUD
    path('', views.InterventionRecordListView.as_view(), name='intervention-list'),
    path('create/', views.InterventionRecordCreateView.as_view(), name='intervention-create'),
    path('<int:pk>/', views.InterventionRecordDetailView.as_view(), name='intervention-detail'),
    path('<int:pk>/update/', views.InterventionRecordUpdateView.as_view(), name='intervention-update'),
    path('<int:pk>/delete/', views.InterventionRecordDeleteView.as_view(), name='intervention-delete'),

    # 干预统计
    path('stats/', views.InterventionStatsView.as_view(), name='intervention-stats'),

    # 学生干预汇总
    path('student/<int:student_id>/summary/', views.StudentInterventionSummaryView.as_view(), name='student-intervention-summary'),
]
