from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InterventionRecord
from .serializers import (
    InterventionRecordListSerializer,
    InterventionRecordDetailSerializer,
    InterventionRecordCreateSerializer,
    InterventionRecordUpdateSerializer,
    InterventionStatsSerializer,
)


class InterventionRecordListView(generics.ListAPIView):
    """干预记录列表视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionRecordListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__name', 'student__student_no', 'title', 'content']
    ordering_fields = ['intervention_time', 'created_at']
    ordering = ['-intervention_time']

    def get_queryset(self):
        queryset = InterventionRecord.objects.all()

        # 筛选参数
        student_id = self.request.query_params.get('student_id')
        warning_id = self.request.query_params.get('warning_id')
        intervention_type = self.request.query_params.get('type')
        is_effective = self.request.query_params.get('is_effective')
        follow_up_needed = self.request.query_params.get('follow_up_needed')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if warning_id:
            queryset = queryset.filter(warning_id=warning_id)
        if intervention_type:
            queryset = queryset.filter(intervention_type=intervention_type)
        if is_effective is not None:
            queryset = queryset.filter(is_effective=is_effective)
        if follow_up_needed is not None:
            queryset = queryset.filter(follow_up_needed=follow_up_needed)

        return queryset.select_related('student', 'course', 'intervenor')


class InterventionRecordDetailView(generics.RetrieveAPIView):
    """干预记录详情视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionRecordDetailSerializer
    queryset = InterventionRecord.objects.all()

    def get_queryset(self):
        return InterventionRecord.objects.select_related(
            'student', 'course', 'intervenor', 'warning'
        )


class InterventionRecordCreateView(generics.CreateAPIView):
    """干预记录创建视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionRecordCreateSerializer
    queryset = InterventionRecord.objects.all()

    def perform_create(self, serializer):
        serializer.save(intervenor=self.request.user)


class InterventionRecordUpdateView(generics.UpdateAPIView):
    """干预记录更新视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionRecordUpdateSerializer
    queryset = InterventionRecord.objects.all()


class InterventionRecordDeleteView(generics.DestroyAPIView):
    """干预记录删除视图"""
    permission_classes = [IsAuthenticated]
    queryset = InterventionRecord.objects.all()


class InterventionStatsView(APIView):
    """干预统计视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student_id = request.query_params.get('student_id')

        queryset = InterventionRecord.objects.all()
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        stats = queryset.aggregate(
            total_interventions=Count('id'),
            talk_count=Count('id', filter=Q(intervention_type='talk')),
            parent_contact_count=Count('id', filter=Q(intervention_type='parent_contact')),
            study_plan_count=Count('id', filter=Q(intervention_type='study_plan')),
            tutor_count=Count('id', filter=Q(intervention_type='tutor')),
            other_count=Count('id', filter=Q(intervention_type='other')),
            effective_count=Count('id', filter=Q(is_effective=1)),
            ineffective_count=Count('id', filter=Q(is_effective=0)),
            pending_count=Count('id', filter=Q(is_effective=2)),
            follow_up_needed_count=Count('id', filter=Q(follow_up_needed=1)),
        )

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': stats
        })


class StudentInterventionSummaryView(APIView):
    """学生干预汇总视图"""
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        interventions = InterventionRecord.objects.filter(student_id=student_id)

        # 最新干预
        latest_intervention = interventions.order_by('-intervention_time').first()

        # 统计
        stats = interventions.aggregate(
            total=Count('id'),
            effective=Count('id', filter=Q(is_effective=1)),
            recent_30_days=Count('id', filter=Q(intervention_time__gte=timezone.now() - timezone.timedelta(days=30)))
        )

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'student_id': student_id,
                'total_interventions': stats['total'],
                'effective_count': stats['effective'],
                'recent_30_days': stats['recent_30_days'],
                'latest_intervention': InterventionRecordListSerializer(latest_intervention).data if latest_intervention else None
            }
        })
