"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.urls")),
    path("api/courses/", include("courses.urls")),
    path("api/classes/", include("classes.urls")),
    path("api/warnings/", include("warning_system.urls")),
    path("api/learning/", include("learning.urls")),
    path("api/algorithm/", include("algorithm.urls")),
    path("api/interventions/", include("interventions.urls")),
]
