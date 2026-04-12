"""
干预系统模型
记录辅导员对学生的干预措施
"""
from django.db import models
from django.contrib.auth.models import User

from classes.models import Student
from courses.models import Course
from warning_system.models import WarningRecord


class InterventionRecord(models.Model):
    """干预记录"""
    INTERVENTION_TYPES = [
        ('talk', '谈心谈话'),
        ('study_plan', '学习计划制定'),
        ('tutoring', '学业辅导'),
        ('parent_contact', '家长联系'),
        ('course_adjust', '课程调整'),
        ('other', '其他'),
    ]

    INTERVENTION_METHODS = [
        ('face_to_face', '面对面'),
        ('phone', '电话'),
        ('online', '线上'),
        ('group', '班会/群体'),
    ]

    EFFECTIVENESS_CHOICES = [
        ('effective', '有效'),
        ('partial', '部分有效'),
        ('ineffective', '无效'),
        ('pending', '待评估'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='interventions',
        verbose_name='学生'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='interventions',
        verbose_name='关联课程',
        null=True,
        blank=True
    )
    warning = models.ForeignKey(
        WarningRecord,
        on_delete=models.SET_NULL,
        related_name='interventions',
        verbose_name='关联预警',
        null=True,
        blank=True
    )
    counselor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='interventions',
        verbose_name='辅导员'
    )

    # 干预内容
    intervention_type = models.CharField(
        max_length=20,
        choices=INTERVENTION_TYPES,
        verbose_name='干预类型'
    )
    method = models.CharField(
        max_length=20,
        choices=INTERVENTION_METHODS,
        verbose_name='干预方式'
    )
    content = models.TextField(verbose_name='干预内容')
    follow_up_plan = models.TextField(
        verbose_name='后续跟进计划',
        null=True,
        blank=True
    )

    # 时间记录
    intervention_date = models.DateTimeField(verbose_name='干预时间')
    duration_minutes = models.PositiveIntegerField(
        verbose_name='持续时间(分钟)',
        default=30
    )

    # 效果评估
    effectiveness = models.CharField(
        max_length=20,
        choices=EFFECTIVENESS_CHOICES,
        default='pending',
        verbose_name='干预效果'
    )
    evaluation_notes = models.TextField(
        verbose_name='评估说明',
        null=True,
        blank=True
    )
    evaluated_at = models.DateTimeField(
        verbose_name='评估时间',
        null=True,
        blank=True
    )

    # 状态
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'interventions_record'
        verbose_name = '干预记录'
        verbose_name_plural = '干预记录'
        ordering = ['-intervention_date', '-created_at']

    def __str__(self):
        return f"{self.student.name} - {self.get_intervention_type_display()} ({self.intervention_date.strftime('%Y-%m-%d')})"


class InterventionFollowUp(models.Model):
    """干预后续跟进记录"""
    intervention = models.ForeignKey(
        InterventionRecord,
        on_delete=models.CASCADE,
        related_name='follow_ups',
        verbose_name='干预记录'
    )
    follow_up_date = models.DateTimeField(verbose_name='跟进时间')
    content = models.TextField(verbose_name='跟进内容')
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='记录人'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'interventions_followup'
        verbose_name = '跟进记录'
        verbose_name_plural = '跟进记录'
        ordering = ['-follow_up_date']
