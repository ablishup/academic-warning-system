# courses/serializers.py
from rest_framework import serializers
from .models import Course, CourseEnrollment, KnowledgePoint


class CourseSerializer(serializers.ModelSerializer):
    """课程序列化器"""
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'course_no', 'name', 'description', 'credit', 'hours',
                  'teacher_id', 'semester', 'status', 'student_count', 'created_at']

    def get_student_count(self, obj):
        return CourseEnrollment.objects.filter(course_id=obj.id).count()


class KnowledgePointSerializer(serializers.ModelSerializer):
    """知识点序列化器"""
    class Meta:
        model = KnowledgePoint
        fields = ['id', 'course_id', 'name', 'chapter_no', 'description', 'weight']


class CourseListSerializer(serializers.ModelSerializer):
    """课程列表序列化器（简化版）"""
    class Meta:
        model = Course
        fields = ['id', 'name', 'course_no', 'semester']
