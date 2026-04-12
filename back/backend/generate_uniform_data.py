#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成均匀分布的测试数据
用于演示不同风险等级的预警效果
"""
import os
import sys
import random
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

print("=" * 70)
print("生成均匀分布的测试数据")
print("=" * 70)

from classes.models import Student
from courses.models import Course
from warning_system.models import StudentCourseScore, WarningRecord
from algorithm.warning_predictor import WarningPredictor
from algorithm.features import FeatureEngineering
from django.utils import timezone

# 清除现有数据
print("\n【步骤1】清除现有预警和得分数据")
WarningRecord.objects.all().delete()
print(f"  已删除所有预警记录")

# 获取学生和课程
students = list(Student.objects.all())
courses = list(Course.objects.all())

print(f"\n学生数: {len(students)}")
print(f"课程数: {len(courses)}")

# 为每个学生-课程组合生成均匀分布的数据
print("\n【步骤2】生成均匀分布的学习数据")

def generate_uniform_score():
    """生成均匀分布的得分数据，覆盖所有风险等级"""
    # 目标分布：高危20%，中等30%，低危30%，正常20%
    rand = random.random()

    if rand < 0.2:  # 20% 高危 (0-60分)
        # 出勤率低，各项成绩差
        return {
            'attendance_rate': random.uniform(30, 55),
            'video_progress': random.uniform(20, 50),
            'homework_avg': random.uniform(40, 58),
            'exam_avg': random.uniform(35, 55),
            'expected_level': 'high'
        }
    elif rand < 0.5:  # 30% 中等 (60-75分)
        # 部分指标偏低
        return {
            'attendance_rate': random.uniform(60, 75),
            'video_progress': random.uniform(55, 70),
            'homework_avg': random.uniform(60, 72),
            'exam_avg': random.uniform(58, 70),
            'expected_level': 'medium'
        }
    elif rand < 0.8:  # 30% 低危 (75-85分)
        # 大部分指标良好，个别稍差
        return {
            'attendance_rate': random.uniform(78, 88),
            'video_progress': random.uniform(75, 85),
            'homework_avg': random.uniform(75, 82),
            'exam_avg': random.uniform(72, 82),
            'expected_level': 'low'
        }
    else:  # 20% 正常 (85-100分)
        # 各项指标优秀
        return {
            'attendance_rate': random.uniform(90, 100),
            'video_progress': random.uniform(88, 100),
            'homework_avg': random.uniform(85, 95),
            'exam_avg': random.uniform(82, 95),
            'expected_level': 'normal'
        }

# 生成数据
score_records = []
level_counts = {'high': 0, 'medium': 0, 'low': 0, 'normal': 0}

for student in students:
    for course in courses:
        data = generate_uniform_score()

        # 保存到数据库
        score, created = StudentCourseScore.objects.update_or_create(
            student=student,
            course=course,
            defaults={
                'attendance_rate': round(data['attendance_rate'], 2),
                'video_progress': round(data['video_progress'], 2),
                'homework_avg': round(data['homework_avg'], 2),
                'exam_avg': round(data['exam_avg'], 2),
                'homework_submit_rate': random.uniform(70, 100),
            }
        )
        score_records.append((score, data['expected_level']))
        level_counts[data['expected_level']] += 1

print(f"\n生成完成！")
print(f"  高危 (high):    {level_counts['high']} 条 ({level_counts['high']/len(score_records)*100:.1f}%)")
print(f"  中等 (medium):  {level_counts['medium']} 条 ({level_counts['medium']/len(score_records)*100:.1f}%)")
print(f"  低危 (low):     {level_counts['low']} 条 ({level_counts['low']/len(score_records)*100:.1f}%)")
print(f"  正常 (normal):  {level_counts['normal']} 条 ({level_counts['normal']/len(score_records)*100:.1f}%)")

# 重新计算预警
print("\n【步骤3】使用随机森林重新计算预警")

predictor = WarningPredictor()
if not predictor.load_model():
    print("训练新模型...")
    predictor.train()

warnings_created = 0
warnings_by_level = {'high': 0, 'medium': 0, 'low': 0, 'normal': 0}

for score, expected_level in score_records:
    features_dict = {
        'attendance_rate': float(score.attendance_rate),
        'video_progress': float(score.video_progress),
        'homework_avg_score': float(score.homework_avg),
        'exam_avg_score': float(score.exam_avg),
    }

    # 预测
    result = predictor.predict(
        student_id=score.student_id,
        course_id=score.course_id,
        features_dict=features_dict
    )

    risk_level = result['risk_level']
    warnings_by_level[risk_level] += 1

    # 创建预警记录（非normal等级）
    if risk_level != 'normal':
        WarningRecord.objects.create(
            student=score.student,
            course=score.course,
            risk_level=risk_level,
            composite_score=result['predicted_score'],
            attendance_score=score.attendance_rate,
            progress_score=score.video_progress,
            homework_score=score.homework_avg,
            exam_score=score.exam_avg,
        )
        warnings_created += 1

print(f"\n预警计算完成！")
print(f"  新增预警: {warnings_created} 条")
print(f"\n预测结果分布:")
print(f"  [HIGH] 高危 (high):    {warnings_by_level['high']} 条")
print(f"  [MEDIUM] 中等 (medium):  {warnings_by_level['medium']} 条")
print(f"  [LOW] 低危 (low):     {warnings_by_level['low']} 条")
print(f"  [NORMAL] 正常 (normal):  {warnings_by_level['normal']} 条")

# 显示样本
print("\n【步骤4】各风险等级样本")
print("-" * 70)

for level in ['high', 'medium', 'low']:
    warnings = WarningRecord.objects.filter(risk_level=level).select_related('student', 'course')[:3]
    if warnings:
        print(f"\n{level.upper()} 示例:")
        for w in warnings:
            print(f"  {w.student.name} ({w.student.student_no})")
            print(f"    课程: {w.course.name if w.course else 'N/A'}")
            print(f"    综合得分: {w.composite_score}")
            print(f"    出勤: {w.attendance_score}% | 视频: {w.progress_score}% | "
                  f"作业: {w.homework_score} | 考试: {w.exam_score}")

print("\n" + "=" * 70)
print("数据生成完成！现在前端可以看到均匀分布的预警数据了。")
print("=" * 70)
