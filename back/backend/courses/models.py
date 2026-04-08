# courses/models.py
from django.db import models
from django.contrib.auth.models import User


class CourseResource(models.Model):
    """课程教学资料模型 - 对应数据库 course_resources 表"""
    RESOURCE_TYPE_CHOICES = [
        ('video', '视频'),
        ('document', '文档'),
        ('ppt', '课件'),
        ('exercise', '习题'),
    ]

    id = models.AutoField(primary_key=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE, db_column='course_id',
                               related_name='resources')
    knowledge_point = models.ForeignKey('KnowledgePoint', on_delete=models.SET_NULL,
                                        db_column='knowledge_point_id',
                                        null=True, blank=True,
                                        related_name='resources')
    name = models.CharField(max_length=200, db_column='name', verbose_name='资料名称')
    file = models.FileField(upload_to='resources/%Y/%m/', db_column='file_path',
                            verbose_name='文件')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES,
                                     db_column='resource_type', verbose_name='资料类型')
    description = models.TextField(blank=True, null=True, db_column='description',
                                   verbose_name='描述')
    file_size = models.IntegerField(default=0, db_column='file_size',
                                    verbose_name='文件大小(字节)')
    download_count = models.IntegerField(default=0, db_column='download_count',
                                         verbose_name='下载次数')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='created_by',
                                   null=True, blank=True, verbose_name='上传者')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'course_resources'
        managed = False
        verbose_name = '课程资源'
        verbose_name_plural = '课程资源'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Course(models.Model):
    """课程模型 - 对应数据库courses表"""
    id = models.AutoField(primary_key=True)
    course_no = models.CharField(max_length=20, blank=True, null=True, db_column='course_no')
    name = models.CharField(max_length=200, db_column='name')
    description = models.TextField(blank=True, null=True, db_column='description')
    credit = models.DecimalField(max_digits=3, decimal_places=1, default=2.0, db_column='credit')
    hours = models.IntegerField(blank=True, null=True, db_column='hours')
    teacher_id = models.IntegerField(blank=True, null=True, db_column='teacher_id')
    semester = models.CharField(max_length=20, blank=True, null=True, db_column='semester')
    chapters = models.JSONField(blank=True, null=True, db_column='chapters')
    status = models.SmallIntegerField(default=1, db_column='status')
    raw_id = models.CharField(max_length=50, blank=True, null=True, db_column='raw_id')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'courses'
        managed = False

    def __str__(self):
        return self.name


class CourseEnrollment(models.Model):
    """选课关系模型 - 对应数据库course_enrollments表"""
    id = models.AutoField(primary_key=True)
    student_id = models.IntegerField(db_column='student_id')
    course_id = models.IntegerField(db_column='course_id')
    enroll_time = models.DateTimeField(blank=True, null=True, db_column='enroll_time')
    status = models.SmallIntegerField(default=1, db_column='status')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'course_enrollments'
        managed = False
        unique_together = [['student_id', 'course_id']]


class KnowledgePoint(models.Model):
    """知识点模型 - 对应数据库knowledge_points表"""
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='course_id')
    name = models.CharField(max_length=200, db_column='name')
    chapter_no = models.CharField(max_length=20, blank=True, null=True, db_column='chapter_no')
    parent_id = models.IntegerField(blank=True, null=True, db_column='parent_id')
    description = models.TextField(blank=True, null=True, db_column='description')
    weight = models.DecimalField(max_digits=4, decimal_places=2, default=1.00, db_column='weight')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'knowledge_points'
        managed = False

    def __str__(self):
        return self.name
