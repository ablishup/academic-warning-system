# courses/serializers.py
from rest_framework import serializers
from .models import Course, CourseEnrollment, KnowledgePoint, CourseResource


class CourseResourceSerializer(serializers.ModelSerializer):
    """课程资源序列化器"""
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    file_url = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    file_size_formatted = serializers.SerializerMethodField()

    class Meta:
        model = CourseResource
        fields = ['id', 'course_id', 'knowledge_point_id', 'name', 'file', 'file_url',
                  'resource_type', 'resource_type_display', 'description',
                  'file_size', 'file_size_formatted', 'download_count',
                  'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'download_count', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        """获取文件完整URL"""
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def get_created_by_name(self, obj):
        """获取上传者姓名"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None

    def get_file_size_formatted(self, obj):
        """格式化文件大小"""
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"


class CourseResourceCreateSerializer(serializers.ModelSerializer):
    """课程资源创建序列化器"""
    class Meta:
        model = CourseResource
        fields = ['course', 'knowledge_point', 'name', 'file', 'resource_type', 'description']

    def validate(self, data):
        """验证文件大小和类型"""
        file = data.get('file')
        if file:
            # 限制文件大小为 500MB
            if file.size > 500 * 1024 * 1024:
                raise serializers.ValidationError('文件大小不能超过500MB')
            data['file_size'] = file.size
        return data


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
