from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    """教师信息模型 - 扩展 auth_user 表的业务信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='teacher_profile',
        verbose_name='关联用户'
    )
    teacher_no = models.CharField(
        max_length=20,
        db_column='teacher_no',
        unique=True,
        verbose_name='工号'
    )
    department = models.CharField(
        max_length=100,
        db_column='department',
        blank=True,
        null=True,
        verbose_name='所属院系'
    )
    title = models.CharField(
        max_length=50,
        db_column='title',
        blank=True,
        null=True,
        verbose_name='职称',
        help_text='教授/副教授/讲师/助教等'
    )
    phone = models.CharField(
        max_length=20,
        db_column='phone',
        blank=True,
        null=True,
        verbose_name='办公电话'
    )
    office = models.CharField(
        max_length=100,
        db_column='office',
        blank=True,
        null=True,
        verbose_name='办公室位置'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'teachers'
        managed = True
        verbose_name = '教师信息'
        verbose_name_plural = '教师信息'
        ordering = ['teacher_no']

    def __str__(self):
        return f"{self.teacher_no} - {self.user.first_name or self.user.username}"


class Counselor(models.Model):
    """辅导员信息模型 - 扩展 auth_user 表的业务信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='counselor_profile',
        verbose_name='关联用户'
    )
    employee_no = models.CharField(
        max_length=20,
        db_column='employee_no',
        unique=True,
        verbose_name='工号'
    )
    department = models.CharField(
        max_length=100,
        db_column='department',
        blank=True,
        null=True,
        verbose_name='所属院系'
    )
    phone = models.CharField(
        max_length=20,
        db_column='phone',
        blank=True,
        null=True,
        verbose_name='联系电话'
    )
    office = models.CharField(
        max_length=100,
        db_column='office',
        blank=True,
        null=True,
        verbose_name='办公地点'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'counselors'
        managed = True
        verbose_name = '辅导员信息'
        verbose_name_plural = '辅导员信息'
        ordering = ['employee_no']

    def __str__(self):
        return f"{self.employee_no} - {self.user.first_name or self.user.username}"


class UserProfile(models.Model):
    """用户扩展信息 - 用于存储学生和未分类用户的额外信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='profile',
        verbose_name='关联用户'
    )
    # 对学生存储学号，对教职工存储工号
    employee_no = models.CharField(
        max_length=20,
        db_column='employee_no',
        blank=True,
        null=True,
        verbose_name='学号/工号'
    )
    department = models.CharField(
        max_length=100,
        db_column='department',
        blank=True,
        null=True,
        verbose_name='所属院系/班级'
    )
    phone = models.CharField(
        max_length=20,
        db_column='phone',
        blank=True,
        null=True,
        verbose_name='联系电话'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'user_profiles'
        managed = True
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'

    def __str__(self):
        return f"{self.user.username} 的扩展信息"
