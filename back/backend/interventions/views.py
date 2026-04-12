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
            if is_effective == 'true':
                queryset = queryset.filter(is_effective=1)
            elif is_effective == 'false':
                queryset = queryset.filter(is_effective=0)
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({
            'code': 200,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)


class InterventionRecordUpdateView(generics.UpdateAPIView):
    """干预记录更新视图"""
    permission_classes = [IsAuthenticated]
    serializer_class = InterventionRecordUpdateSerializer
    queryset = InterventionRecord.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 200,
            'message': '更新成功',
            'data': InterventionRecordDetailSerializer(instance).data
        })


class InterventionRecordDeleteView(generics.DestroyAPIView):
    """干预记录删除视图"""
    permission_classes = [IsAuthenticated]
    queryset = InterventionRecord.objects.all()

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

        effectiveness = request.data.get('effectiveness')
        evaluation_notes = request.data.get('evaluation_notes', '')

        if not effectiveness:
            return Response({
                'code': 400,
                'message': '请提供评估结果'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 映射 effectiveness 到 is_effective
        mapping = {
            'effective': 1,
            'partial': 1,
            'ineffective': 0,
            'pending': 2
        }
        intervention.is_effective = mapping.get(effectiveness, 2)
        intervention.result = evaluation_notes

        # 如果标记为有效或部分有效，自动更新跟进状态
        if effectiveness in ['effective', 'partial']:
            intervention.follow_up_needed = 0

        intervention.save()

        return Response({
            'code': 200,
            'message': '评估成功',
            'data': {
                'id': intervention.id,
                'effectiveness': effectiveness,
                'is_completed': intervention.follow_up_needed == 0
            }
        })


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
            academic_count=Count('id', filter=Q(intervention_type='academic')),
            psychological_count=Count('id', filter=Q(intervention_type='psychological')),
            family_count=Count('id', filter=Q(intervention_type='family')),
            other_count=Count('id', filter=Q(intervention_type='other')),
            effective_count=Count('id', filter=Q(is_effective=1)),
            ineffective_count=Count('id', filter=Q(is_effective=0)),
            pending_count=Count('id', filter=Q(is_effective=2)),
            follow_up_needed_count=Count('id', filter=Q(follow_up_needed=1)),
        )

        # 计算本月新增
        this_month = queryset.filter(
            created_at__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0)
        ).count()

        # 构建按类型统计
        by_type = {
            'talk': stats['talk_count'],
            'academic': stats['academic_count'],
            'psychological': stats['psychological_count'],
            'family': stats['family_count'],
            'other': stats['other_count'],
        }

        # 构建按效果统计
        by_effectiveness = {
            'effective': stats['effective_count'],
            'ineffective': stats['ineffective_count'],
            'pending': stats['pending_count'],
        }

        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': stats['total_interventions'],
                'completed': stats['total_interventions'] - stats['follow_up_needed_count'],
                'by_type': by_type,
                'by_effectiveness': by_effectiveness,
                'this_month': this_month
            }
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
