from rest_framework import serializers
from .models import InterventionRecord
from classes.serializers import StudentSerializer
from courses.serializers import CourseSerializer
from users.serializers import UserSerializer


class InterventionRecordListSerializer(serializers.ModelSerializer):
    """干预记录列表序列化器"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_no = serializers.CharField(source='student.student_no', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    counselor_name = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_intervention_type_display', read_only=True)
    method_display = serializers.CharField(source='method', read_only=True)
    effectiveness_display = serializers.SerializerMethodField()

    class Meta:
        model = InterventionRecord
        fields = [
            'id', 'student', 'student_name', 'student_no',
            'course', 'course_name', 'warning',
            'intervention_type', 'type_display',
            'method', 'method_display',
            'title', 'content',
            'intervention_time', 'created_at',
            'counselor_name', 'effectiveness_display'
        ]

    def get_counselor_name(self, obj):
        return obj.intervenor.get_full_name() if obj.intervenor else ''

    def get_effectiveness_display(self, obj):
        mapping = {0: '无效', 1: '有效', 2: '待评估', None: '未评估'}
        return mapping.get(obj.is_effective, '未评估')


class InterventionRecordDetailSerializer(serializers.ModelSerializer):
    """干预记录详情序列化器"""
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    counselor = serializers.SerializerMethodField()
    intervention_type_display = serializers.CharField(source='get_intervention_type_display', read_only=True)
    is_effective_display = serializers.CharField(source='get_is_effective_display', read_only=True)
    evaluation_note = serializers.CharField(source='result', read_only=True)

    class Meta:
        model = InterventionRecord
        fields = [
            'id', 'student', 'course', 'counselor', 'warning',
            'intervention_type', 'intervention_type_display',
            'title', 'content', 'method', 'result',
            'is_effective', 'is_effective_display',
            'follow_up_needed', 'follow_up_time',
            'intervention_time', 'created_at', 'updated_at',
            'evaluation_note'
        ]

    def get_counselor(self, obj):
        if obj.intervenor:
            return {
                'id': obj.intervenor.id,
                'username': obj.intervenor.username,
                'name': obj.intervenor.get_full_name()
            }
        return None


class InterventionRecordCreateSerializer(serializers.ModelSerializer):
    """干预记录创建序列化器"""
    follow_up_plan = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = InterventionRecord
        fields = [
            'student', 'course', 'warning', 'intervention_type',
            'title', 'content', 'method', 'intervention_time',
            'follow_up_plan'
        ]

    def create(self, validated_data):
        validated_data.pop('follow_up_plan', None)  # 暂时不处理，因为模型中没有这个字段
        validated_data['intervenor'] = self.context['request'].user
        return super().create(validated_data)


class InterventionRecordUpdateSerializer(serializers.ModelSerializer):
    """干预记录更新序列化器"""
    is_effective = serializers.BooleanField(required=False)
    evaluation_note = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = InterventionRecord
        fields = [
            'title', 'content', 'method', 'result',
            'is_effective', 'evaluation_note',
            'follow_up_needed', 'follow_up_time'
        ]

    def update(self, instance, validated_data):
        # 处理 evaluation_note 映射到 result
        evaluation_note = validated_data.pop('evaluation_note', None)
        if evaluation_note is not None:
            instance.result = evaluation_note

        # 处理 is_effective (布尔值映射到整数)
        is_effective = validated_data.pop('is_effective', None)
        if is_effective is not None:
            instance.is_effective = 1 if is_effective else 0
            # 如果标记为有效，自动更新跟进状态
            if is_effective:
                instance.follow_up_needed = 0

        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class InterventionStatsSerializer(serializers.Serializer):
    """干预统计序列化器"""
    total_interventions = serializers.IntegerField()
    talk_count = serializers.IntegerField()
    academic_count = serializers.IntegerField()
    psychological_count = serializers.IntegerField()
    family_count = serializers.IntegerField()
    other_count = serializers.IntegerField()
    effective_count = serializers.IntegerField()
    ineffective_count = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    follow_up_needed_count = serializers.IntegerField()
