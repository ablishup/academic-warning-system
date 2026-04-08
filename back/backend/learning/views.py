from django.db.models import Avg, Count, Q
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from classes.models import Student
from courses.models import Course

from .models import (
    LearningActivity, HomeworkAssignment, HomeworkSubmission,
    ExamAssignment, ExamResult
)
from .serializers import (
    LearningActivitySerializer, LearningActivitySummarySerializer,
    HomeworkAssignmentSerializer, HomeworkSubmissionSerializer,
    HomeworkSubmissionListSerializer, StudentHomeworkStatsSerializer,
    ExamAssignmentSerializer, ExamResultSerializer, ExamResultListSerializer,
    StudentExamStatsSerializer, CourseLearningStatsSerializer,
)


# ==================== 学习活动 API ====================

class LearningActivityListView(generics.ListAPIView):
    """学习活动列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = LearningActivitySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'activity_name']
    ordering_fields = ['start_time', 'duration', 'progress']
    ordering = ['-start_time']

    def get_queryset(self):
        queryset = LearningActivity.objects.all()

        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')
        activity_type = self.request.query_params.get('type')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)

        return queryset.select_related('student', 'course', 'chapter')


class LearningActivitySummaryView(generics.GenericAPIView):
    """学习活动统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        course_id = request.query_params.get('course_id')

        queryset = LearningActivity.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        stats = queryset.aggregate(
            total_activities=Count('id'),
            video_count=Count('id', filter=Q(activity_type='video')),
            sign_in_count=Count('id', filter=Q(activity_type='sign_in')),
            total_duration=Avg('duration'),
            avg_progress=Avg('progress')
        )

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': stats
        })


# ==================== 作业 API ====================

class HomeworkAssignmentListView(generics.ListAPIView):
    """作业任务列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = HomeworkAssignmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['deadline', 'created_at']
    ordering = ['-deadline']

    def get_queryset(self):
        queryset = HomeworkAssignment.objects.all()

        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('course', 'knowledge_point')


class HomeworkAssignmentDetailView(generics.RetrieveAPIView):
    """作业任务详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = HomeworkAssignmentSerializer
    queryset = HomeworkAssignment.objects.all()

    def get_queryset(self):
        return HomeworkAssignment.objects.select_related('course', 'knowledge_point')


class HomeworkSubmissionListView(generics.ListAPIView):
    """作业提交列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = HomeworkSubmissionListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'student__student_no']
    ordering_fields = ['submit_time', 'score']
    ordering = ['-submit_time']

    def get_queryset(self):
        queryset = HomeworkSubmission.objects.all()

        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')
        assignment_id = self.request.query_params.get('assignment_id')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)
        if course_id:
            queryset = queryset.filter(assignment__course_id=course_id)

        return queryset.select_related('student', 'assignment')


class HomeworkSubmissionDetailView(generics.RetrieveAPIView):
    """作业提交详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = HomeworkSubmissionSerializer
    queryset = HomeworkSubmission.objects.all()

    def get_queryset(self):
        return HomeworkSubmission.objects.select_related('student', 'assignment')


class StudentHomeworkStatsView(generics.GenericAPIView):
    """学生作业统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        course_id = request.query_params.get('course_id')

        if not student_id:
            return Response({
                'code': 400,
                'message': '需要指定student_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        submissions = HomeworkSubmission.objects.filter(student_id=student_id)
        if course_id:
            submissions = submissions.filter(assignment__course_id=course_id)

        stats = submissions.aggregate(
            submitted_count=Count('id'),
            avg_score=Avg('score'),
            on_time_count=Count('id', filter=Q(is_late=0))
        )

        # 获取该学生在该课程的总作业数
        total_query = HomeworkAssignment.objects.filter(
            course_enrollments__student_id=student_id
        )
        if course_id:
            total_query = total_query.filter(course_id=course_id)
        total_assignments = total_query.count()

        on_time_rate = 0
        if stats['submitted_count'] and stats['submitted_count'] > 0:
            on_time_rate = round(stats['on_time_count'] / stats['submitted_count'] * 100, 2)

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total_assignments': total_assignments,
                'submitted_count': stats['submitted_count'],
                'avg_score': round(stats['avg_score'] or 0, 2),
                'on_time_rate': on_time_rate
            }
        })


# ==================== 考试 API ====================

class ExamAssignmentListView(generics.ListAPIView):
    """考试任务列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = ExamAssignmentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time', 'end_time']
    ordering = ['-start_time']

    def get_queryset(self):
        queryset = ExamAssignment.objects.all()

        course_id = self.request.query_params.get('course_id')
        exam_type = self.request.query_params.get('type')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if exam_type:
            queryset = queryset.filter(exam_type=exam_type)

        return queryset.select_related('course')


class ExamAssignmentDetailView(generics.RetrieveAPIView):
    """考试任务详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = ExamAssignmentSerializer
    queryset = ExamAssignment.objects.all()

    def get_queryset(self):
        return ExamAssignment.objects.select_related('course')


class ExamResultListView(generics.ListAPIView):
    """考试结果列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = ExamResultListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'student__student_no']
    ordering_fields = ['submit_time', 'score']
    ordering = ['-submit_time']

    def get_queryset(self):
        queryset = ExamResult.objects.all()

        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')
        exam_id = self.request.query_params.get('exam_id')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        if course_id:
            queryset = queryset.filter(exam__course_id=course_id)

        return queryset.select_related('student', 'exam')


class ExamResultDetailView(generics.RetrieveAPIView):
    """考试结果详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = ExamResultSerializer
    queryset = ExamResult.objects.all()

    def get_queryset(self):
        return ExamResult.objects.select_related('student', 'exam')


class StudentExamStatsView(generics.GenericAPIView):
    """学生考试统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')
        course_id = request.query_params.get('course_id')

        if not student_id:
            return Response({
                'code': 400,
                'message': '需要指定student_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        results = ExamResult.objects.filter(student_id=student_id)
        if course_id:
            results = results.filter(exam__course_id=course_id)

        stats = results.aggregate(
            taken_count=Count('id'),
            avg_score=Avg('score'),
            highest_score=Max('score'),
            lowest_score=Min('score')
        )

        # 获取总考试数
        total_query = ExamAssignment.objects.filter(
            course_enrollments__student_id=student_id
        )
        if course_id:
            total_query = total_query.filter(course_id=course_id)
        total_exams = total_query.count()

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total_exams': total_exams,
                'taken_count': stats['taken_count'],
                'avg_score': round(stats['avg_score'] or 0, 2),
                'highest_score': round(stats['highest_score'] or 0, 2),
                'lowest_score': round(stats['lowest_score'] or 0, 2)
            }
        })


# ==================== 综合统计 API ====================

from django.db.models import Max, Min


class CourseLearningStatsView(generics.GenericAPIView):
    """课程学习统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        course_id = request.query_params.get('course_id')

        if not course_id:
            return Response({
                'code': 400,
                'message': '需要指定course_id'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'code': 404,
                'message': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 视频进度统计
        video_stats = LearningActivity.objects.filter(
            course_id=course_id,
            activity_type='video'
        ).aggregate(avg_progress=Avg('progress'))

        # 作业平均分
        homework_stats = HomeworkSubmission.objects.filter(
            assignment__course_id=course_id
        ).aggregate(avg_score=Avg('score'))

        # 考试平均分
        exam_stats = ExamResult.objects.filter(
            exam__course_id=course_id
        ).aggregate(avg_score=Avg('score'))

        # 学生人数
        student_count = Student.objects.filter(
            course_enrollments__course_id=course_id
        ).count()

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'course_id': course.id,
                'course_name': course.name,
                'student_count': student_count,
                'avg_video_progress': round(video_stats['avg_progress'] or 0, 2),
                'avg_homework_score': round(homework_stats['avg_score'] or 0, 2),
                'avg_exam_score': round(exam_stats['avg_score'] or 0, 2)
            }
        })
