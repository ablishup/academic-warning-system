from django.urls import path
from . import views

urlpatterns = [
    # 模型管理
    path('train/', views.TrainModelView.as_view(), name='train-model'),
    path('status/', views.ModelStatusView.as_view(), name='model-status'),
    path('feature-importance/', views.FeatureImportanceView.as_view(), name='feature-importance'),

    # 预测与特征
    path('predict/', views.PredictWarningView.as_view(), name='predict-warning'),
    path('features/', views.ExtractFeaturesView.as_view(), name='extract-features'),
]
