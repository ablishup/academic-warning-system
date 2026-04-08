# classes/serializers.py
from rest_framework import serializers
from .models import Student, Class, Major


class StudentSerializer(serializers.ModelSerializer):
    """学生序列化器"""
    gender_display = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'student_no', 'name', 'gender', 'gender_display',
                  'class_id', 'class_name', 'phone', 'email', 'enrollment_year', 'status']

    def get_gender_display(self, obj):
        gender_map = {0: '未知', 1: '男', 2: '女'}
        return gender_map.get(obj.gender, '未知')

    def get_class_name(self, obj):
        try:
            cls = Class.objects.get(id=obj.class_id)
            return cls.name
        except Class.DoesNotExist:
            return None


class ClassSerializer(serializers.ModelSerializer):
    """班级序列化器"""
    student_count_actual = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'grade', 'major_id', 'student_count', 'student_count_actual']

    def get_student_count_actual(self, obj):
        return Student.objects.filter(class_id=obj.id).count()


class StudentListSerializer(serializers.ModelSerializer):
    """学生列表序列化器（简化版）"""
    class Meta:
        model = Student
        fields = ['id', 'student_no', 'name', 'gender', 'class_id']
