from rest_framework import serializers
from .models import (
    LearningActivity, HomeworkAssignment, HomeworkSubmission,
    ExamAssignment, ExamResult
)
from classes.serializers import StudentSerializer
from courses.serializers import CourseSerializer, KnowledgePointSerializer


class LearningActivityCreateSerializer(serializers.Serializer):
    """学习活动创建序列化器"""
    student_id = serializers.IntegerField(required=True, help_text='学生ID')
    course_id = serializers.IntegerField(required=True, help_text='课程ID')
    activity_type = serializers.ChoiceField(
        choices=LearningActivity.ACTIVITY_TYPE_CHOICES,
        required=True,
        help_text='活动类型'
    )
    activity_name = serializers.CharField(required=True, max_length=200, help_text='活动名称')
    chapter = serializers.IntegerField(required=False, allow_null=True, help_text='知识点ID')
    start_time = serializers.DateTimeField(required=False, help_text='开始时间')
    duration = serializers.IntegerField(required=False, default=0, help_text='持续时长(秒)')
    progress = serializers.DecimalField(required=False, max_digits=5, decimal_places=2, default=0, help_text='进度百分比')
    score = serializers.DecimalField(required=False, max_digits=5, decimal_places=2, allow_null=True, help_text='得分')
    raw_data = serializers.JSONField(required=False, default=dict, help_text='原始数据(观看片段等)')


class LearningActivitySerializer(serializers.ModelSerializer):
    """学习活动序列化器"""
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = LearningActivity
        fields = [
            'id', 'student', 'course', 'activity_type', 'activity_type_display',
            'activity_name', 'start_time', 'end_time', 'duration',
            'progress', 'score', 'created_at'
        ]


class LearningActivitySummarySerializer(serializers.Serializer):
    """学习活动统计序列化器"""
    total_activities = serializers.IntegerField()
    video_count = serializers.IntegerField()
    sign_in_count = serializers.IntegerField()
    total_duration = serializers.IntegerField()
    avg_progress = serializers.FloatField()


class HomeworkAssignmentSerializer(serializers.ModelSerializer):
    """作业任务序列化器"""
    course = CourseSerializer(read_only=True)
    knowledge_point = KnowledgePointSerializer(read_only=True)

    class Meta:
        model = HomeworkAssignment
        fields = [
            'id', 'course', 'title', 'description',
            'knowledge_point', 'full_score', 'start_time', 'deadline', 'status'
        ]


class HomeworkSubmissionSerializer(serializers.ModelSerializer):
    """作业提交序列化器"""
    student = StudentSerializer(read_only=True)
    assignment = HomeworkAssignmentSerializer(read_only=True)
    submission_rate = serializers.SerializerMethodField()

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id', 'student', 'assignment', 'score',
            'submit_time', 'is_late', 'correct_count', 'total_count',
            'submission_rate', 'created_at'
        ]

    def get_submission_rate(self, obj):
        if obj.total_count and obj.total_count > 0:
            return round((obj.correct_count or 0) / obj.total_count * 100, 2)
        return None


class HomeworkSubmissionListSerializer(serializers.ModelSerializer):
    """作业提交列表序列化器（简化版）"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_no = serializers.CharField(source='student.student_no', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    submission_rate = serializers.SerializerMethodField()

    class Meta:
        model = HomeworkSubmission
        fields = [
            'id', 'student_name', 'student_no', 'assignment_title',
            'score', 'submit_time', 'is_late', 'submission_rate'
        ]

    def get_submission_rate(self, obj):
        if obj.total_count and obj.total_count > 0:
            return round((obj.correct_count or 0) / obj.total_count * 100, 2)
        return None


class StudentHomeworkStatsSerializer(serializers.Serializer):
    """学生作业统计序列化器"""
    total_assignments = serializers.IntegerField()
    submitted_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    on_time_rate = serializers.FloatField()


class ExamAssignmentSerializer(serializers.ModelSerializer):
    """考试任务序列化器"""
    course = CourseSerializer(read_only=True)
    exam_type_display = serializers.CharField(source='get_exam_type_display', read_only=True)

    class Meta:
        model = ExamAssignment
        fields = [
            'id', 'course', 'title', 'exam_type', 'exam_type_display',
            'full_score', 'start_time', 'end_time', 'duration', 'status'
        ]


class ExamResultSerializer(serializers.ModelSerializer):
    """考试结果序列化器"""
    student = StudentSerializer(read_only=True)
    exam = ExamAssignmentSerializer(read_only=True)
    accuracy_rate = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = [
            'id', 'student', 'exam', 'score',
            'submit_time', 'is_submitted', 'correct_count', 'total_count',
            'accuracy_rate', 'created_at'
        ]

    def get_accuracy_rate(self, obj):
        if obj.total_count and obj.total_count > 0:
            return round((obj.correct_count or 0) / obj.total_count * 100, 2)
        return None


class ExamResultListSerializer(serializers.ModelSerializer):
    """考试结果列表序列化器（简化版）"""
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_no = serializers.CharField(source='student.student_no', read_only=True)
    exam_title = serializers.CharField(source='exam.title', read_only=True)
    exam_type = serializers.CharField(source='exam.exam_type', read_only=True)
    accuracy_rate = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = [
            'id', 'student_name', 'student_no', 'exam_title', 'exam_type',
            'score', 'submit_time', 'accuracy_rate'
        ]

    def get_accuracy_rate(self, obj):
        if obj.total_count and obj.total_count > 0:
            return round((obj.correct_count or 0) / obj.total_count * 100, 2)
        return None


class StudentExamStatsSerializer(serializers.Serializer):
    """学生考试统计序列化器"""
    total_exams = serializers.IntegerField()
    taken_count = serializers.IntegerField()
    avg_score = serializers.FloatField()
    highest_score = serializers.FloatField()
    lowest_score = serializers.FloatField()


class CourseLearningStatsSerializer(serializers.Serializer):
    """课程学习统计序列化器"""
    course_id = serializers.IntegerField()
    course_name = serializers.CharField()
    student_count = serializers.IntegerField()
    avg_video_progress = serializers.FloatField()
    avg_homework_score = serializers.FloatField()
    avg_exam_score = serializers.FloatField()
