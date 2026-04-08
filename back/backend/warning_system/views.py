from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Student
from courses.models import Course

from .models import WarningRecord, StudentCourseScore
from .serializers import (
    WarningRecordListSerializer,
    WarningRecordDetailSerializer,
    WarningCalculateSerializer,
    WarningResolveSerializer,
    StudentCourseScoreSerializer,
    WarningStatsSerializer,
)


class WarningRecordListView(generics.ListAPIView):
    """预警列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = WarningRecordListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'student__student_no', 'course__name']
    ordering_fields = ['calculation_time', 'composite_score', 'created_at']
    ordering = ['-calculation_time']

    def get_queryset(self):
        queryset = WarningRecord.objects.all()

        # 筛选参数
        risk_level = self.request.query_params.get('risk_level')
        status = self.request.query_params.get('status')
        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')

        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        if status:
            queryset = queryset.filter(status=status)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('student', 'course')


class WarningRecordDetailView(generics.RetrieveAPIView):
    """预警详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = WarningRecordDetailSerializer
    queryset = WarningRecord.objects.all()
    lookup_field = 'pk'

    def get_queryset(self):
        return WarningRecord.objects.select_related('student', 'course', 'resolved_by')


class WarningCalculateView(APIView):
    """计算预警视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = WarningCalculateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        student_id = serializer.validated_data.get('student_id')
        course_id = serializer.validated_data.get('course_id')

        # 获取需要计算的学生-课程组合
        scores_query = StudentCourseScore.objects.all()
        if student_id:
            scores_query = scores_query.filter(student_id=student_id)
        if course_id:
            scores_query = scores_query.filter(course_id=course_id)

        # 计算预警
        created_count = 0
        updated_count = 0

        for score in scores_query.select_related('student', 'course'):
            # 计算综合得分（加权平均）
            composite_score = self._calculate_composite_score(score)

            # 确定风险等级
            risk_level = self._determine_risk_level(composite_score)

            # 检查是否已存在预警记录
            existing_warning = WarningRecord.objects.filter(
                student=score.student,
                course=score.course,
                status='active'
            ).first()

            if existing_warning:
                # 更新现有预警
                existing_warning.composite_score = composite_score
                existing_warning.risk_level = risk_level
                existing_warning.attendance_score = score.attendance_rate
                existing_warning.progress_score = score.video_progress
                existing_warning.homework_score = score.homework_avg
                existing_warning.exam_score = score.exam_avg
                existing_warning.calculation_time = timezone.now()
                existing_warning.save()
                updated_count += 1
            else:
                # 创建新预警（只对非normal等级）
                if risk_level != 'normal':
                    WarningRecord.objects.create(
                        student=score.student,
                        course=score.course,
                        risk_level=risk_level,
                        composite_score=composite_score,
                        attendance_score=score.attendance_rate,
                        progress_score=score.video_progress,
                        homework_score=score.homework_avg,
                        exam_score=score.exam_avg,
                    )
                    created_count += 1

        return Response({
            'code': 200,
            'message': '预警计算完成',
            'data': {
                'created': created_count,
                'updated': updated_count,
            }
        })

    def _calculate_composite_score(self, score):
        """计算综合得分
        权重：出勤30%、进度20%、作业30%、考试20%
        """
        attendance = float(score.attendance_rate or 0) * 0.3
        progress = float(score.video_progress or 0) * 0.2
        homework = float(score.homework_avg or 0) * 0.3
        exam = float(score.exam_avg or 0) * 0.2
        return round(attendance + progress + homework + exam, 2)

    def _determine_risk_level(self, score):
        """确定风险等级"""
        if score < 60:
            return 'high'      # 红色预警
        elif score < 75:
            return 'medium'    # 橙色预警
        elif score < 85:
            return 'low'       # 黄色预警
        else:
            return 'normal'    # 正常


class WarningResolveView(APIView):
    """解决预警视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            warning = WarningRecord.objects.get(pk=pk)
        except WarningRecord.DoesNotExist:
            return Response({
                'code': 404,
                'message': '预警记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = WarningResolveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        warning.status = 'resolved'
        warning.resolved_at = timezone.now()
        warning.resolved_by = request.user
        warning.resolve_note = serializer.validated_data.get('resolve_note', '')
        warning.save()

        return Response({
            'code': 200,
            'message': '预警已解决',
            'data': {
                'id': warning.id,
                'status': warning.status,
                'resolved_at': warning.resolved_at,
            }
        })


class WarningStatsView(APIView):
    """预警统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = WarningRecord.objects.aggregate(
            total_warnings=Count('id'),
            high_risk_count=Count('id', filter=Q(risk_level='high')),
            medium_risk_count=Count('id', filter=Q(risk_level='medium')),
            low_risk_count=Count('id', filter=Q(risk_level='low')),
            normal_count=Count('id', filter=Q(risk_level='normal')),
            active_count=Count('id', filter=Q(status='active')),
            resolved_count=Count('id', filter=Q(status='resolved')),
        )

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': stats
        })


class StudentCourseScoreListView(generics.ListAPIView):
    """学生课程综合得分列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = StudentCourseScoreSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['last_calculated', 'final_score']
    ordering = ['-last_calculated']

    def get_queryset(self):
        queryset = StudentCourseScore.objects.all()

        student_id = self.request.query_params.get('student_id')
        course_id = self.request.query_params.get('course_id')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if course_id:
            queryset = queryset.filter(course_id=course_id)

        return queryset.select_related('student', 'course')
