from django.db import models
from django.contrib.auth.models import User


class WarningRecord(models.Model):
    """预警记录表"""
    RISK_LEVEL_CHOICES = [
        ('high', '红色预警'),
        ('medium', '橙色预警'),
        ('low', '黄色预警'),
        ('normal', '正常'),
    ]
    STATUS_CHOICES = [
        ('active', '生效中'),
        ('resolved', '已解决'),
        ('ignored', '已忽略'),
    ]
    AI_SOURCE_CHOICES = [
        ('ai', 'AI生成'),
        ('template', '模板'),
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE, db_column='student_id',
                                related_name='warnings')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, db_column='course_id',
                               related_name='warnings', null=True, blank=True)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES, verbose_name='风险等级')
    composite_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          verbose_name='综合得分')

    # 各维度得分
    attendance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                           verbose_name='出勤率得分')
    progress_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         verbose_name='学习进度得分')
    homework_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         verbose_name='作业成绩得分')
    exam_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     verbose_name='考试成绩得分')

    # AI建议
    ai_analysis = models.TextField(null=True, blank=True, verbose_name='AI问题分析')
    ai_suggestions = models.JSONField(null=True, blank=True, verbose_name='AI建议列表')
    ai_parent_script = models.TextField(null=True, blank=True, verbose_name='AI家长沟通文案')
    ai_encouragement = models.TextField(null=True, blank=True, verbose_name='AI激励信')
    ai_source = models.CharField(max_length=10, choices=AI_SOURCE_CHOICES, default='template',
                                 verbose_name='建议来源')

    # 状态
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='预警状态')
    resolved_at = models.DateTimeField(null=True, blank=True, verbose_name='解决时间')
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='resolved_by',
                                    related_name='resolved_warnings', null=True, blank=True)
    resolve_note = models.TextField(null=True, blank=True, verbose_name='处理备注')
    calculation_time = models.DateTimeField(auto_now_add=True, verbose_name='计算时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'warning_records'
        managed = False
        ordering = ['-calculation_time']
        verbose_name = '预警记录'
        verbose_name_plural = '预警记录'

    def __str__(self):
        course_name = self.course.name if self.course else '综合'
        return f"{self.student.name} - {course_name} - {self.get_risk_level_display()}"


class StudentCourseScore(models.Model):
    """学生课程综合得分表"""
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE, db_column='student_id',
                                related_name='course_scores')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, db_column='course_id',
                               related_name='student_scores')
    attendance_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                          verbose_name='出勤率')
    video_progress = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         verbose_name='视频进度')
    homework_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                       verbose_name='作业平均分')
    homework_submit_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                               verbose_name='作业提交率')
    exam_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   verbose_name='考试平均分')
    knowledge_mastery = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                            verbose_name='知识点掌握度')
    final_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                      verbose_name='期末成绩')
    last_calculated = models.DateTimeField(auto_now=True, verbose_name='最后计算时间')

    class Meta:
        db_table = 'student_course_scores'
        managed = False
        unique_together = ['student', 'course']
        verbose_name = '学生课程综合得分'
        verbose_name_plural = '学生课程综合得分'

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"
