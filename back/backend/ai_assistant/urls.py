from django.urls import path
from . import views

urlpatterns = [
    path('comment/', views.generate_comment, name='ai_comment'),
]
