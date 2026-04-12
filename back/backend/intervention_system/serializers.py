"""
干预系统序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User

from classes.models import Student
from courses.models import Course
from warning_system.models import WarningRecord
from .models import InterventionRecord, InterventionFollowUp


class StudentBriefSerializer(serializers.ModelSerializer):
    """学生简要信息"""
    class Meta:
        model = Student
        fields = ['id', 'name', 'student_no', 'class_name']


class CourseBriefSerializer(serializers.ModelSerializer):
    """课程简要信息"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'course_code']


class WarningBriefSerializer(serializers.ModelSerializer):
    """预警简要信息"""
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = WarningRecord
        fields = ['id', 'risk_level', 'composite_score', 'student_name']


class InterventionListSerializer(serializers.ModelSerializer):
    """干预记录列表序列化器"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_no = serializers.CharField(source='student.student_no', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    warning_level = serializers.CharField(source='warning.risk_level', read_only=True)
    counselor_name = serializers.CharField(source='counselor.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_intervention_type_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    effectiveness_display = serializers.CharField(source='get_effectiveness_display', read_only=True)

    class Meta:
        model = InterventionRecord
        fields = [
            'id', 'student', 'student_name', 'student_no',
            'course', 'course_name', 'warning', 'warning_level',
            'counselor', 'counselor_name',
            'intervention_type', 'type_display',
            'method', 'method_display',
            'content', 'follow_up_plan',
            'intervention_date', 'duration_minutes',
            'effectiveness', 'effectiveness_display',
            'is_completed', 'created_at'
        ]


class InterventionDetailSerializer(serializers.ModelSerializer):
    """干预记录详情序列化器"""
    student = StudentBriefSerializer(read_only=True)
    course = CourseBriefSerializer(read_only=True)
    warning = WarningBriefSerializer(read_only=True)
    counselor_name = serializers.CharField(source='counselor.get_full_name', read_only=True)
    type_display = serializers.CharField(source='get_intervention_type_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    effectiveness_display = serializers.CharField(source='get_effectiveness_display', read_only=True)

    class Meta:
        model = InterventionRecord
        fields = '__all__'


class InterventionCreateSerializer(serializers.ModelSerializer):
    """干预记录创建序列化器"""
    class Meta:
        model = InterventionRecord
        fields = [
            'student', 'course', 'warning',
            'intervention_type', 'method', 'content',
            'follow_up_plan', 'intervention_date', 'duration_minutes'
        ]

    def create(self, validated_data):
        validated_data['counselor'] = self.context['request'].user
        return super().create(validated_data)


class InterventionUpdateSerializer(serializers.ModelSerializer):
    """干预记录更新序列化器"""
    class Meta:
        model = InterventionRecord
        fields = [
            'intervention_type', 'method', 'content',
            'follow_up_plan', 'intervention_date', 'duration_minutes',
            'effectiveness', 'evaluation_notes', 'is_completed'
        ]

    def update(self, instance, validated_data):
        if 'effectiveness' in validated_data and validated_data['effectiveness'] != instance.effectiveness:
            from django.utils import timezone
            validated_data['evaluated_at'] = timezone.now()

            # 如果标记为有效或部分有效，自动完成
            if validated_data['effectiveness'] in ['effective', 'partial']:
                validated_data['is_completed'] = True

        return super().update(instance, validated_data)


class InterventionEvaluateSerializer(serializers.Serializer):
    """干预效果评估序列化器"""
    effectiveness = serializers.ChoiceField(
        choices=InterventionRecord.EFFECTIVENESS_CHOICES,
        required=True
    )
    evaluation_notes = serializers.CharField(
        required=False,
        allow_blank=True
    )


class InterventionStatsSerializer(serializers.Serializer):
    """干预统计序列化器"""
    total = serializers.IntegerField()
    by_type = serializers.DictField()
    by_effectiveness = serializers.DictField()
    this_month = serializers.IntegerField()
    completed = serializers.IntegerField()


class InterventionFollowUpSerializer(serializers.ModelSerializer):
    """跟进记录序列化器"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = InterventionFollowUp
        fields = ['id', 'intervention', 'follow_up_date', 'content', 'created_by', 'created_by_name', 'created_at']
