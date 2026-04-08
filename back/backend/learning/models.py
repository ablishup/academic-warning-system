from django.db import models


class LearningActivity(models.Model):
    """学习活动表"""
    ACTIVITY_TYPE_CHOICES = [
        ('video', '视频学习'),
        ('sign_in', '签到考勤'),
        ('discuss', '讨论'),
        ('quiz', '测验'),
        ('other', '其他'),
    ]

    id = models.AutoField(primary_key=True)
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE, db_column='student_id',
                                related_name='learning_activities')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, db_column='course_id',
                               related_name='learning_activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, verbose_name='活动类型')
    activity_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='活动名称')
    chapter = models.ForeignKey('courses.KnowledgePoint', on_delete=models.SET_NULL, db_column='chapter_id',
                                related_name='activities', null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration = models.IntegerField(null=True, blank=True, verbose_name='持续时长(秒)')
    progress = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='进度百分比')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='得分')
    raw_data = models.JSONField(null=True, blank=True, verbose_name='原始数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'learning_activities'
        managed = False
        ordering = ['-start_time']
        verbose_name = '学习活动'
        verbose_name_plural = '学习活动'

    def __str__(self):
        return f"{self.student.name} - {self.activity_name}"


class HomeworkAssignment(models.Model):
    """作业任务表"""
    id = models.AutoField(primary_key=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, db_column='course_id',
                               related_name='homework_assignments')
    title = models.CharField(max_length=200, verbose_name='作业标题')
    description = models.TextField(null=True, blank=True, verbose_name='作业描述')
    knowledge_point = models.ForeignKey('courses.KnowledgePoint', on_delete=models.SET_NULL,
                                        db_column='knowledge_point_id', null=True, blank=True)
    full_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, verbose_name='满分')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    status = models.SmallIntegerField(default=1, verbose_name='状态')
    raw_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='原始数据ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'homework_assignments'
        managed = False
        ordering = ['-deadline']
        verbose_name = '作业任务'
        verbose_name_plural = '作业任务'

    def __str__(self):
        return self.title


class HomeworkSubmission(models.Model):
    """作业提交表"""
    id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(HomeworkAssignment, on_delete=models.CASCADE, db_column='assignment_id',
                                   related_name='submissions')
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE, db_column='student_id',
                                related_name='homework_submissions')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='得分')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    is_late = models.SmallIntegerField(default=0, verbose_name='是否迟交')
    correct_count = models.IntegerField(null=True, blank=True, verbose_name='答对题数')
    total_count = models.IntegerField(null=True, blank=True, verbose_name='总题数')
    raw_data = models.JSONField(null=True, blank=True, verbose_name='原始答案数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'homework_submissions'
        managed = False
        unique_together = ['assignment', 'student']
        ordering = ['-submit_time']
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'

    def __str__(self):
        return f"{self.student.name} - {self.assignment.title}"


class ExamAssignment(models.Model):
    """考试任务表"""
    EXAM_TYPE_CHOICES = [
        ('midterm', '期中考试'),
        ('final', '期末考试'),
        ('quiz', '测验'),
        ('other', '其他'),
    ]

    id = models.AutoField(primary_key=True)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, db_column='course_id',
                               related_name='exam_assignments')
    title = models.CharField(max_length=200, verbose_name='考试标题')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES, default='quiz', verbose_name='考试类型')
    full_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, verbose_name='满分')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    duration = models.IntegerField(null=True, blank=True, verbose_name='考试时长(分钟)')
    status = models.SmallIntegerField(default=1, verbose_name='状态')
    raw_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='原始数据ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_assignments'
        managed = False
        ordering = ['-start_time']
        verbose_name = '考试任务'
        verbose_name_plural = '考试任务'

    def __str__(self):
        return self.title


class ExamResult(models.Model):
    """考试结果表"""
    id = models.AutoField(primary_key=True)
    exam = models.ForeignKey(ExamAssignment, on_delete=models.CASCADE, db_column='exam_id',
                             related_name='results')
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE, db_column='student_id',
                                related_name='exam_results')
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='得分')
    submit_time = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    is_submitted = models.SmallIntegerField(default=1, verbose_name='是否提交')
    correct_count = models.IntegerField(null=True, blank=True, verbose_name='答对题数')
    total_count = models.IntegerField(null=True, blank=True, verbose_name='总题数')
    raw_data = models.JSONField(null=True, blank=True, verbose_name='原始答案数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'exam_results'
        managed = False
        unique_together = ['exam', 'student']
        ordering = ['-submit_time']
        verbose_name = '考试结果'
        verbose_name_plural = '考试结果'

    def __str__(self):
        return f"{self.student.name} - {self.exam.title}"
