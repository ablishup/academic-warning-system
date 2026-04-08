# courses/models.py
from django.db import models


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
