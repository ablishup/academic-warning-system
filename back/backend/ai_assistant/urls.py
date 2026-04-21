from django.urls import path
from . import views

urlpatterns = [
    # 学生端AI评语接口（现有）
    path('comment/', views.generate_comment, name='ai_comment'),

    # 辅导员端AI评语接口（新增）
    path('counselor-comment/', views.generate_counselor_comment, name='counselor_comment'),
    path('stored-comment/<int:warning_id>/', views.get_stored_comment, name='stored_comment'),
    path('send-sms/', views.send_sms_notification, name='send_sms'),
]
