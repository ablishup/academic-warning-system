"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/courses/", include("courses.urls")),
    path("api/classes/", include("classes.urls")),
    path("api/warnings/", include("warning_system.urls")),
    path("api/learning/", include("learning.urls")),
    path("api/algorithm/", include("algorithm.urls")),
    path("api/interventions/", include("interventions.urls")),
    path("api/import/", include("import_app.urls")),
    path("api/teacher/", include("teacher_dashboard.urls")),
]

# 开发环境提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
