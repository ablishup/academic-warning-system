# import_app/models.py
from django.db import models
from django.contrib.auth.models import User


class ImportLog(models.Model):
    """数据导入记录模型"""
    IMPORT_TYPE_CHOICES = [
        ('activities', '学习活动'),
        ('homework', '作业数据'),
        ('exams', '考试数据'),
        ('enrollments', '选课关系'),
    ]

    STATUS_CHOICES = [
        ('pending', '处理中'),
        ('success', '成功'),
        ('partial', '部分成功'),
        ('failed', '失败'),
    ]

    id = models.AutoField(primary_key=True)
    import_type = models.CharField(
        max_length=20,
        choices=IMPORT_TYPE_CHOICES,
        verbose_name='导入类型'
    )
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    file_size = models.IntegerField(default=0, verbose_name='文件大小(字节)')
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='上传者'
    )
    course_id = models.IntegerField(null=True, blank=True, verbose_name='关联课程ID')

    # 导入统计
    total_rows = models.IntegerField(default=0, verbose_name='总行数')
    success_rows = models.IntegerField(default=0, verbose_name='成功行数')
    failed_rows = models.IntegerField(default=0, verbose_name='失败行数')

    # 状态和信息
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    details = models.JSONField(default=dict, null=True, blank=True, verbose_name='详细信息')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'import_logs'
        managed = False
        verbose_name = '导入记录'
        verbose_name_plural = '导入记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_import_type_display()} - {self.file_name}"
