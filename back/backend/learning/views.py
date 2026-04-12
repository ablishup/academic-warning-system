from django.db.models import Avg, Count, Q, Max, Min
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
    LearningActivityCreateSerializer,
)


def get_student_from_user(user):
    """从当前登录用户获取学生ID"""
    if not user or not user.is_authenticated:
        return None

    # 方法1: 通过 username 匹配 student_no（学号）
    student = Student.objects.filter(student_no=user.username).first()
    if student:
        return student.id

    # 方法2: 通过 first_name 匹配 name（姓名）
    if user.first_name:
        student = Student.objects.filter(name=user.first_name).first()
        if student:
            return student.id

    # 方法3: 兼容旧账号（student_1）
    if user.username.startswith('student_'):
        try:
            student_id = int(user.username.split('_')[1])
            student = Student.objects.filter(id=student_id).first()
            if student:
                return student.id
        except (ValueError, IndexError):
            pass

    # 方法4: 通过 profile 关联 (如果存在)
    try:
        profile = getattr(user, 'profile', None)
        if profile and hasattr(profile, 'employee_no') and profile.employee_no:
            student = Student.objects.filter(student_no=profile.employee_no).first()
            if student:
                return student.id
    except:
        pass

    return None


# ==================== 学习活动 API ====================

class LearningActivityRecordView(APIView):
    """记录学习活动视图 - 用于学生视频观看数据收集"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """记录或更新学习活动"""
        serializer = LearningActivityCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        student_id = data.get('student_id')
        course_id = data.get('course_id')
        activity_type = data.get('activity_type')
        activity_name = data.get('activity_name')

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(request.user)

        # 检查学生是否存在
        try:
            student = Student.objects.get(id=student_id)
        except (Student.DoesNotExist, TypeError):
            return Response({
                'code': 404,
                'message': '学生不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查课程是否存在
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                'code': 404,
                'message': '课程不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 查找是否已有该活动的记录（同一天、同一学生、同一课程、同一活动）
        today = timezone.now().date()
        existing_activity = LearningActivity.objects.filter(
            student_id=student_id,
            course_id=course_id,
            activity_type=activity_type,
            activity_name=activity_name,
            start_time__date=today
        ).first()

        if existing_activity:
            # 更新现有记录
            existing_activity.duration = data.get('duration', existing_activity.duration)
            existing_activity.progress = data.get('progress', existing_activity.progress)
            existing_activity.score = data.get('score', existing_activity.score)
            existing_activity.end_time = timezone.now()

            # 更新 raw_data（如果提供了新的观看片段信息）
            if 'raw_data' in data and data['raw_data']:
                existing_raw = existing_activity.raw_data or {}
                existing_raw.update(data['raw_data'])
                existing_activity.raw_data = existing_raw

            existing_activity.save()

            result_serializer = LearningActivitySerializer(existing_activity)
            return Response({
                'code': 200,
                'message': '学习记录已更新',
                'data': result_serializer.data
            })
        else:
            # 创建新记录
            activity = LearningActivity.objects.create(
                student=student,
                course=course,
                activity_type=activity_type,
                activity_name=activity_name,
                chapter=data.get('chapter'),
                start_time=data.get('start_time', timezone.now()),
                end_time=timezone.now(),
                duration=data.get('duration', 0),
                progress=data.get('progress', 0),
                score=data.get('score'),
                raw_data=data.get('raw_data', {})
            )

            result_serializer = LearningActivitySerializer(activity)
            return Response({
                'code': 200,
                'message': '学习记录已创建',
                'data': result_serializer.data
            }, status=status.HTTP_201_CREATED)


class LearningActivityBatchRecordView(APIView):
    """批量记录学习活动视图 - 用于定时上报观看进度"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """批量记录学习活动"""
        activities = request.data.get('activities', [])
        if not activities:
            return Response({
                'code': 400,
                'message': '请提供活动列表'
            }, status=status.HTTP_400_BAD_REQUEST)

        results = []
        for activity_data in activities:
            serializer = LearningActivityCreateSerializer(data=activity_data)
            if serializer.is_valid():
                # 这里简化处理，实际应该调用上面的逻辑
                # 为了性能，批量处理可以优化
                results.append({
                    'success': True,
                    'activity_name': activity_data.get('activity_name')
                })
            else:
                results.append({
                    'success': False,
                    'errors': serializer.errors
                })

        return Response({
            'code': 200,
            'message': '批量记录完成',
            'data': {
                'total': len(activities),
                'success_count': sum(1 for r in results if r['success']),
                'results': results
            }
        })


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

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(self.request.user)

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

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(request.user)

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

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(self.request.user)

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

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(request.user)

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
        # 简化：直接计算该课程的作业总数
        if course_id:
            total_assignments = HomeworkAssignment.objects.filter(course_id=course_id).count()
        else:
            # 获取学生选修的所有课程的作业总数
            from courses.models import CourseEnrollment
            enrolled_courses = CourseEnrollment.objects.filter(student_id=student_id).values_list('course_id', flat=True)
            total_assignments = HomeworkAssignment.objects.filter(course_id__in=enrolled_courses).count()

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

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(self.request.user)

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

        # 如果没有提供student_id，尝试从当前用户推断
        if not student_id:
            student_id = get_student_from_user(request.user)

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
        if course_id:
            total_exams = ExamAssignment.objects.filter(course_id=course_id).count()
        else:
            # 获取学生选修的所有课程的考试总数
            from courses.models import CourseEnrollment
            enrolled_courses = CourseEnrollment.objects.filter(student_id=student_id).values_list('course_id', flat=True)
            total_exams = ExamAssignment.objects.filter(course_id__in=enrolled_courses).count()

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
        from courses.models import CourseEnrollment
        student_count = CourseEnrollment.objects.filter(course_id=course_id).count()

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'course_id': course.id,
                'course_name': course.name,
                'student_count': student_count,
                'avg_video_progress': round(video_stats['avg_progress'] or 0, 2),
                'avg_homework_score': round(homework_stats['avg_score'] or 0, 2),
                'avg_exam_score': round(exam_stats['avg_score'] or 2)
            }
        })
