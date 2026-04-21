from django.db import models
from django.contrib.auth.models import User


class InterventionRecord(models.Model):
    """干预记录表"""
    INTERVENTION_TYPE_CHOICES = [
        ('talk', '谈心谈话'),
        ('academic', '学业帮扶'),
        ('psychological', '心理疏导'),
        ('family', '家校联系'),
        ('other', '其他'),
    ]

    EFFECTIVENESS_CHOICES = [
        (0, '无效'),
        (1, '有效'),
        (2, '待评估'),
    ]

    id = models.AutoField(primary_key=True)
    warning = models.ForeignKey('warning_system.WarningRecord', on_delete=models.SET_NULL,
                                db_column='warning_id', related_name='interventions',
                                null=True, blank=True)
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE,
                                db_column='student_id', related_name='interventions')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE,
                               db_column='course_id', related_name='interventions',
                               null=True, blank=True)
    intervenor = models.ForeignKey(User, on_delete=models.CASCADE,
                                   db_column='intervenor_id', related_name='interventions')
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPE_CHOICES,
                                         verbose_name='干预类型')
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='干预标题')
    content = models.TextField(null=True, blank=True, verbose_name='干预内容详情')
    method = models.CharField(max_length=100, null=True, blank=True, verbose_name='干预方式')
    result = models.TextField(null=True, blank=True, verbose_name='干预结果')
    is_effective = models.SmallIntegerField(choices=EFFECTIVENESS_CHOICES,
                                            null=True, blank=True, verbose_name='是否有效')
    follow_up_needed = models.SmallIntegerField(default=0, verbose_name='是否需要跟进')
    follow_up_time = models.DateTimeField(null=True, blank=True, verbose_name='计划跟进时间')
    intervention_time = models.DateTimeField(verbose_name='干预时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'intervention_records'
        managed = False
        ordering = ['-intervention_time']
        verbose_name = '干预记录'
        verbose_name_plural = '干预记录'

    def __str__(self):
        return f"{self.student.name} - {self.get_intervention_type_display()} - {self.intervention_time}"


class SMSNotification(models.Model):
    """短信通知记录表"""

    STATUS_CHOICES = [
        ('pending', '待发送'),
        ('sent', '已发送'),
        ('delivered', '已送达'),
        ('failed', '失败'),
    ]

    id = models.AutoField(primary_key=True)

    # 发送信息
    sender = models.ForeignKey(User, on_delete=models.CASCADE,
                               db_column='sender_id', related_name='sent_sms',
                               verbose_name='发送者')
    student = models.ForeignKey('classes.Student', on_delete=models.CASCADE,
                                db_column='student_id', related_name='received_sms',
                                verbose_name='接收学生')
    phone = models.CharField(max_length=20, verbose_name='接收手机号')

    # 关联内容
    warning = models.ForeignKey('warning_system.WarningRecord', on_delete=models.SET_NULL,
                                db_column='warning_id', null=True, blank=True,
                                related_name='sms_notifications',
                                verbose_name='关联预警')
    content = models.TextField(verbose_name='短信内容')

    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='pending', verbose_name='状态')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')

    # 时间戳
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='发送时间')
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name='送达时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'sms_notifications'
        managed = True
        ordering = ['-created_at']
        verbose_name = '短信通知'
        verbose_name_plural = '短信通知'

    def __str__(self):
        return f"{self.student.name} - {self.get_status_display()}"
