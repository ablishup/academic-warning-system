from rest_framework import serializers
from .models import InterventionRecord
from classes.serializers import StudentSerializer
from courses.serializers import CourseSerializer
from users.serializers import UserSerializer


class InterventionRecordListSerializer(serializers.ModelSerializer):
    """干预记录列表序列化器"""
    student = StudentSerializer(read_only=True)
    intervention_type_display = serializers.CharField(source='get_intervention_type_display', read_only=True)
    is_effective_display = serializers.CharField(source='get_is_effective_display', read_only=True)

    class Meta:
        model = InterventionRecord
        fields = [
            'id', 'student', 'intervention_type', 'intervention_type_display',
            'title', 'method', 'is_effective', 'is_effective_display',
            'intervention_time', 'created_at'
        ]


class InterventionRecordDetailSerializer(serializers.ModelSerializer):
    """干预记录详情序列化器"""
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    intervenor = UserSerializer(read_only=True)
    intervention_type_display = serializers.CharField(source='get_intervention_type_display', read_only=True)
    is_effective_display = serializers.CharField(source='get_is_effective_display', read_only=True)

    class Meta:
        model = InterventionRecord
        fields = [
            'id', 'student', 'course', 'intervenor', 'warning',
            'intervention_type', 'intervention_type_display',
            'title', 'content', 'method', 'result',
            'is_effective', 'is_effective_display',
            'follow_up_needed', 'follow_up_time',
            'intervention_time', 'created_at', 'updated_at'
        ]


class InterventionRecordCreateSerializer(serializers.ModelSerializer):
    """干预记录创建序列化器"""
    class Meta:
        model = InterventionRecord
        fields = [
            'student', 'course', 'warning', 'intervention_type',
            'title', 'content', 'method', 'intervention_time'
        ]

    def create(self, validated_data):
        validated_data['intervenor'] = self.context['request'].user
        return super().create(validated_data)


class InterventionRecordUpdateSerializer(serializers.ModelSerializer):
    """干预记录更新序列化器"""
    class Meta:
        model = InterventionRecord
        fields = [
            'title', 'content', 'method', 'result',
            'is_effective', 'follow_up_needed', 'follow_up_time'
        ]


class InterventionStatsSerializer(serializers.Serializer):
    """干预统计序列化器"""
    total_interventions = serializers.IntegerField()
    talk_count = serializers.IntegerField()
    parent_contact_count = serializers.IntegerField()
    study_plan_count = serializers.IntegerField()
    tutor_count = serializers.IntegerField()
    other_count = serializers.IntegerField()
    effective_count = serializers.IntegerField()
    ineffective_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    follow_up_needed_count = serializers.IntegerField()
