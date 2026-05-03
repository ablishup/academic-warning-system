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
    suggestion = serializers.SerializerMethodField()

    class Meta:
        model = WarningRecord
        fields = [
            'id', 'student', 'course', 'risk_level', 'risk_level_display',
            'composite_score', 'attendance_score', 'progress_score',
            'homework_score', 'exam_score',
            'suggestion', 'status', 'status_display',
            'calculation_time', 'created_at'
        ]

    def get_suggestion(self, obj):
        """根据风险等级和各维度分数生成知识点建议"""
        if obj.risk_level == 'normal':
            return '当前学习状态良好，请继续保持。'

        # 找出最薄弱的维度
        scores = {
            '出勤': float(obj.attendance_score or 0),
            '视频学习进度': float(obj.progress_score or 0),
            '作业成绩': float(obj.homework_score or 0),
            '考试成绩': float(obj.exam_score or 0),
        }
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        weakest = sorted_scores[0]
        second_weakest = sorted_scores[1]

        if obj.risk_level == 'high':
            return f'学习状态严重预警，建议立即强化以下薄弱环节：{weakest[0]}（{weakest[1]:.0f}分）、{second_weakest[0]}（{second_weakest[1]:.0f}分）。请及时联系辅导员寻求帮助。'
        elif obj.risk_level == 'medium':
            return f'学习状态存在风险，建议重点关注：{weakest[0]}（{weakest[1]:.0f}分）、{second_weakest[0]}（{second_weakest[1]:.0f}分）。请合理安排时间加强学习。'
        else:  # low
            return f'学习状态基本正常，建议适当关注：{weakest[0]}（{weakest[1]:.0f}分）。继续保持当前学习节奏。'


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
