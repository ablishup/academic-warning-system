from rest_framework import serializers
from .models import WarningRecord, StudentCourseScore
from classes.serializers import StudentSerializer
from courses.serializers import CourseSerializer


class WarningRecordListSerializer(serializers.ModelSerializer):
    """预警列表序列化器"""
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WarningRecord
        fields = [
            'id', 'student', 'course', 'risk_level', 'risk_level_display',
            'composite_score', 'status', 'status_display',
            'calculation_time', 'created_at'
        ]


class WarningRecordDetailSerializer(serializers.ModelSerializer):
    """预警详情序列化器"""
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    ai_source_display = serializers.CharField(source='get_ai_source_display', read_only=True)

    class Meta:
        model = WarningRecord
        fields = [
            'id', 'student', 'course', 'risk_level', 'risk_level_display',
            'composite_score', 'attendance_score', 'progress_score',
            'homework_score', 'exam_score',
            'ai_analysis', 'ai_suggestions', 'ai_parent_script', 'ai_encouragement',
            'ai_source', 'ai_source_display',
            'status', 'status_display', 'resolved_at', 'resolve_note',
            'calculation_time', 'created_at', 'updated_at'
        ]


class WarningCalculateSerializer(serializers.Serializer):
    """预警计算请求序列化器"""
    student_id = serializers.IntegerField(required=False, help_text='学生ID（为空则计算全部）')
    course_id = serializers.IntegerField(required=False, help_text='课程ID（为空则计算全部）')


class WarningResolveSerializer(serializers.Serializer):
    """预警解决序列化器"""
    resolve_note = serializers.CharField(required=False, allow_blank=True, help_text='处理备注')


class StudentCourseScoreSerializer(serializers.ModelSerializer):
    """学生课程综合得分序列化器"""
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = StudentCourseScore
        fields = [
            'id', 'student', 'course',
            'attendance_rate', 'video_progress',
            'homework_avg', 'homework_submit_rate',
            'exam_avg', 'knowledge_mastery', 'final_score',
            'last_calculated'
        ]


class WarningStatsSerializer(serializers.Serializer):
    """预警统计数据序列化器"""
    total_warnings = serializers.IntegerField()
    high_risk_count = serializers.IntegerField()
    medium_risk_count = serializers.IntegerField()
    low_risk_count = serializers.IntegerField()
    normal_count = serializers.IntegerField()
    active_count = serializers.IntegerField()
    resolved_count = serializers.IntegerField()
