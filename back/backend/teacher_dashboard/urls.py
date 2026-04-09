# teacher_dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 教师课程列表
    path('courses/', views.TeacherCourseListView.as_view(), name='teacher-courses'),

    # 课程学生列表（含学情概要）
    path('courses/<int:course_id>/students/', views.TeacherCourseStudentsView.as_view(), name='teacher-course-students'),

    # 课程统计
    path('courses/<int:course_id>/stats/', views.TeacherCourseStatsView.as_view(), name='teacher-course-stats'),

    # 学生学情详情
    path('students/<int:student_id>/summary/', views.TeacherStudentSummaryView.as_view(), name='teacher-student-summary'),
]
