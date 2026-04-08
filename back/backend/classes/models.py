# classes/models.py
from django.db import models


class Major(models.Model):
    """专业模型"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_column='name')
    code = models.CharField(max_length=20, blank=True, null=True, unique=True, db_column='code')
    department = models.CharField(max_length=100, blank=True, null=True, db_column='department')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'majors'
        managed = False

    def __str__(self):
        return self.name


class Class(models.Model):
    """班级模型"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, db_column='name')
    grade = models.CharField(max_length=10, blank=True, null=True, db_column='grade')
    major_id = models.IntegerField(blank=True, null=True, db_column='major_id')
    counselor_id = models.IntegerField(blank=True, null=True, db_column='counselor_id')
    student_count = models.IntegerField(default=0, db_column='student_count')
    raw_id = models.CharField(max_length=50, blank=True, null=True, db_column='raw_id')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'classes'
        managed = False

    def __str__(self):
        return self.name


class Student(models.Model):
    """学生模型"""
    id = models.AutoField(primary_key=True)
    raw_id = models.CharField(max_length=50, blank=True, null=True, db_column='raw_id')
    student_no = models.CharField(max_length=20, unique=True, db_column='student_no')
    name = models.CharField(max_length=50, db_column='name')
    class_id = models.IntegerField(blank=True, null=True, db_column='class_id')
    gender = models.SmallIntegerField(default=0, db_column='gender')  # 0未知, 1男, 2女
    phone = models.CharField(max_length=20, blank=True, null=True, db_column='phone')
    email = models.CharField(max_length=100, blank=True, null=True, db_column='email')
    major_id = models.IntegerField(blank=True, null=True, db_column='major_id')
    enrollment_year = models.IntegerField(blank=True, null=True, db_column='enrollment_year')
    status = models.SmallIntegerField(default=1, db_column='status')  # 0离校, 1在读
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at')

    class Meta:
        db_table = 'students'
        managed = False

    def __str__(self):
        return self.name
