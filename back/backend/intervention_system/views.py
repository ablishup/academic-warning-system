"""
干预系统API视图
"""
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from classes.models import Student
from warning_system.models import WarningRecord
from .models import InterventionRecord, InterventionFollowUp
from .serializers import (
    InterventionListSerializer,
    InterventionDetailSerializer,
    InterventionCreateSerializer,
    InterventionUpdateSerializer,
    InterventionEvaluateSerializer,
    InterventionStatsSerializer,
    InterventionFollowUpSerializer,
)


class InterventionRecordListView(generics.ListAPIView):
    """干预记录列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'student__student_no', 'content']
    ordering_fields = ['intervention_date', 'created_at', 'effectiveness']
    ordering = ['-intervention_date']

    def get_queryset(self):
        queryset = InterventionRecord.objects.all()

        # 筛选参数
        student_id = self.request.query_params.get('student_id')
        warning_id = self.request.query_params.get('warning_id')
        intervention_type = self.request.query_params.get('type')
        effectiveness = self.request.query_params.get('effectiveness')
        is_completed = self.request.query_params.get('is_completed')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if warning_id:
            queryset = queryset.filter(warning_id=warning_id)
        if intervention_type:
            queryset = queryset.filter(intervention_type=intervention_type)
        if effectiveness:
            queryset = queryset.filter(effectiveness=effectiveness)
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')

        return queryset.select_related('student', 'course', 'warning', 'counselor')


class InterventionRecordDetailView(generics.RetrieveAPIView):
    """干预记录详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionDetailSerializer
    queryset = InterventionRecord.objects.all()
    lookup_field = 'pk'


class InterventionRecordCreateView(generics.CreateAPIView):
    """创建干预记录视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionCreateSerializer
    queryset = InterventionRecord.objects.all()

    def perform_create(self, serializer):
        instance = serializer.save()
        # 如果关联了预警，可以更新预警的干预状态
        if instance.warning:
            pass  # 可以在这里添加预警状态更新逻辑


class InterventionRecordUpdateView(generics.UpdateAPIView):
    """更新干预记录视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionUpdateSerializer
    queryset = InterventionRecord.objects.all()
    lookup_field = 'pk'


class InterventionRecordDeleteView(generics.DestroyAPIView):
    """删除干预记录视图"""
    permission_classes = [IsAuthenticated]
    queryset = InterventionRecord.objects.all()
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功'
        })


class InterventionEvaluateView(APIView):
    """评估干预效果视图"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            intervention = InterventionRecord.objects.get(pk=pk)
        except InterventionRecord.DoesNotExist:
            return Response({
                'code': 404,
                'message': '干预记录不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = InterventionEvaluateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 更新干预记录
        intervention.effectiveness = serializer.validated_data['effectiveness']
        intervention.evaluation_notes = serializer.validated_data.get('evaluation_notes', '')
        intervention.evaluated_at = timezone.now()

        # 如果标记为有效或部分有效，自动标记为完成
        if intervention.effectiveness in ['effective', 'partial']:
            intervention.is_completed = True

        intervention.save()

        return Response({
            'code': 200,
            'message': '评估成功',
            'data': {
                'id': intervention.id,
                'effectiveness': intervention.effectiveness,
                'effectiveness_display': intervention.get_effectiveness_display(),
                'evaluated_at': intervention.evaluated_at
            }
        })


class InterventionStatsView(APIView):
    """干预统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 基础统计
        total = InterventionRecord.objects.count()
        completed = InterventionRecord.objects.filter(is_completed=True).count()

        # 按类型统计
        by_type = dict(InterventionRecord.objects.values('intervention_type').annotate(
            count=Count('id')
        ).values_list('intervention_type', 'count'))

        # 按效果统计
        by_effectiveness = dict(InterventionRecord.objects.values('effectiveness').annotate(
            count=Count('id')
        ).values_list('effectiveness', 'count'))

        # 本月新增
        from django.utils import timezone
        from datetime import timedelta
        this_month = InterventionRecord.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).count()

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': total,
                'completed': completed,
                'by_type': by_type,
                'by_effectiveness': by_effectiveness,
                'this_month': this_month
            }
        })


class StudentInterventionSummaryView(APIView):
    """学生干预汇总视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        try:
            student = Student.objects.get(pk=student_id)
        except Student.DoesNotExist:
            return Response({
                'code': 404,
                'message': '学生不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        interventions = InterventionRecord.objects.filter(student=student)

        total = interventions.count()
        completed = interventions.filter(is_completed=True).count()
        effective = interventions.filter(effectiveness='effective').count()

        # 最近3条干预记录
        recent_interventions = interventions.order_by('-intervention_date')[:3]

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': total,
                'completed': completed,
                'effective': effective,
                'recent_interventions': InterventionListSerializer(
                    recent_interventions, many=True
                ).data
            }
        })


class InterventionFollowUpListView(generics.ListAPIView):
    """跟进记录列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionFollowUpSerializer

    def get_queryset(self):
        queryset = InterventionFollowUp.objects.all()
        intervention_id = self.request.query_params.get('intervention_id')
        if intervention_id:
            queryset = queryset.filter(intervention_id=intervention_id)
        return queryset.select_related('created_by')


class InterventionFollowUpCreateView(generics.CreateAPIView):
    """创建跟进记录视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionFollowUpSerializer
    queryset = InterventionFollowUp.objects.all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
