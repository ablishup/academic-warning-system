#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预测功能测试脚本
"""
import os
import sys
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

print("=" * 70)
print("预测功能实际效果测试")
print("=" * 70)

# 1. 检查当前数据状态
print("\n【步骤1】检查当前数据状态")
print("-" * 70)

from classes.models import Student
from courses.models import Course, CourseEnrollment
from learning.models import LearningActivity, HomeworkSubmission, ExamResult
from warning_system.models import StudentCourseScore, WarningRecord

print(f"学生总数: {Student.objects.count()}")
print(f"课程总数: {Course.objects.count()}")
print(f"选课记录: {CourseEnrollment.objects.count()}")
print(f"\n原始学习数据:")
print(f"  - 考勤记录: {LearningActivity.objects.filter(activity_type='sign_in').count()}")
print(f"  - 视频记录: {LearningActivity.objects.filter(activity_type='video').count()}")
print(f"  - 作业提交: {HomeworkSubmission.objects.count()}")
print(f"  - 考试记录: {ExamResult.objects.count()}")
print(f"\n当前得分/预警:")
print(f"  - 学生课程得分: {StudentCourseScore.objects.count()}")
print(f"  - 预警记录: {WarningRecord.objects.count()}")

# 2. 同步数据
print("\n【步骤2】同步学生课程得分数据")
print("-" * 70)

from warning_system.data_sync import DataSynchronizer

stats_before = DataSynchronizer.get_sync_statistics()
print(f"同步前覆盖率: {stats_before['coverage_percent']}%")

if stats_before['synced_scores'] == 0:
    print("\n开始同步数据...")
    results = DataSynchronizer.sync_all_students_scores()
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"同步完成: 成功 {success_count} 条")
else:
    print("数据已同步，跳过")

stats_after = DataSynchronizer.get_sync_statistics()
print(f"同步后覆盖率: {stats_after['coverage_percent']}%")

# 3. 查看同步后的得分数据
print("\n【步骤3】查看学生课程得分样本")
print("-" * 70)

scores = StudentCourseScore.objects.select_related('student', 'course')[:5]
for score in scores:
    print(f"\n学生: {score.student.name} ({score.student.student_no})")
    print(f"课程: {score.course.name if score.course else 'N/A'}")
    print(f"  出勤率: {score.attendance_rate:.1f}%")
    print(f"  视频进度: {score.video_progress:.1f}%")
    print(f"  作业平均分: {score.homework_avg:.1f}")
    print(f"  考试平均分: {score.exam_avg:.1f}")

# 4. 训练随机森林模型
print("\n【步骤4】训练随机森林模型")
print("-" * 70)

from algorithm.warning_predictor import WarningPredictor

predictor = WarningPredictor()

# 检查是否已有模型
if predictor.load_model():
    print("已加载已有模型")
else:
    print("训练新模型...")
    train_results = predictor.train()
    print(f"模型训练完成!")
    print(f"  分类准确率: {train_results['classification_accuracy']:.2%}")
    print(f"  回归RMSE: {train_results['regression_rmse']}")
    print(f"\n特征重要性:")
    for feature, importance in sorted(
        train_results['feature_importance'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]:
        print(f"  - {feature}: {importance:.3f}")

# 5. 预测单个学生
print("\n【步骤5】预测单个学生风险")
print("-" * 70)

test_score = StudentCourseScore.objects.select_related('student', 'course').first()
if test_score:
    print(f"\n测试学生: {test_score.student.name}")
    print(f"课程: {test_score.course.name if test_score.course else 'N/A'}")
    print(f"\n输入特征:")
    print(f"  出勤率: {test_score.attendance_rate:.1f}%")
    print(f"  视频进度: {test_score.video_progress:.1f}%")
    print(f"  作业平均分: {test_score.homework_avg:.1f}")
    print(f"  考试平均分: {test_score.exam_avg:.1f}")

    # 执行预测
    result = predictor.predict(
        student_id=test_score.student_id,
        course_id=test_score.course_id
    )

    print(f"\n预测结果:")
    print(f"  风险等级: {result['risk_level'].upper()}")
    print(f"  预测得分: {result['predicted_score']:.2f}")
    print(f"  使用模型: {result['model_type']}")

    print(f"\n各风险等级概率:")
    for level, prob in result['risk_probability'].items():
        print(f"  - {level}: {prob}%")

    if result['feature_importance']:
        print(f"\n特征重要性排名:")
        for i, (feature, importance) in enumerate(
            sorted(result['feature_importance'].items(), key=lambda x: x[1], reverse=True)[:5],
            1
        ):
            print(f"  {i}. {feature}: {importance:.3f}")

# 6. 批量预测生成预警
print("\n【步骤6】批量生成预警记录")
print("-" * 70)

from django.utils import timezone
from algorithm.features import FeatureEngineering

warnings_created = 0
warnings_updated = 0

all_scores = StudentCourseScore.objects.select_related('student', 'course')
print(f"需要处理的学生-课程组合: {all_scores.count()}")

for score in all_scores[:20]:  # 先测试前20条
    features_dict = {
        'attendance_rate': float(score.attendance_rate or 0),
        'video_progress': float(score.video_progress or 0),
        'homework_avg_score': float(score.homework_avg or 0),
        'exam_avg_score': float(score.exam_avg or 0),
    }

    # 预测
    result = predictor.predict(
        student_id=score.student_id,
        course_id=score.course_id,
        features_dict=features_dict
    )

    # 检查是否已有预警
    existing = WarningRecord.objects.filter(
        student=score.student,
        course=score.course,
        status='active'
    ).first()

    if existing:
        # 更新
        existing.composite_score = result['predicted_score']
        existing.risk_level = result['risk_level']
        existing.attendance_score = score.attendance_rate
        existing.progress_score = score.video_progress
        existing.homework_score = score.homework_avg
        existing.exam_score = score.exam_avg
        existing.calculation_time = timezone.now()
        existing.save()
        warnings_updated += 1
    elif result['risk_level'] != 'normal':
        # 创建新预警
        WarningRecord.objects.create(
            student=score.student,
            course=score.course,
            risk_level=result['risk_level'],
            composite_score=result['predicted_score'],
            attendance_score=score.attendance_rate,
            progress_score=score.video_progress,
            homework_score=score.homework_avg,
            exam_score=score.exam_avg,
        )
        warnings_created += 1

print(f"\n预警生成完成:")
print(f"  - 新增预警: {warnings_created} 条")
print(f"  - 更新预警: {warnings_updated} 条")

# 7. 查看预警统计
print("\n【步骤7】预警统计")
print("-" * 70)

from django.db.models import Count, Q

stats = WarningRecord.objects.aggregate(
    total=Count('id'),
    high=Count('id', filter=Q(risk_level='high')),
    medium=Count('id', filter=Q(risk_level='medium')),
    low=Count('id', filter=Q(risk_level='low')),
    normal=Count('id', filter=Q(risk_level='normal')),
)

print(f"预警统计:")
print(f"  - 高危 (high): {stats['high']} 条")
print(f"  - 中等 (medium): {stats['medium']} 条")
print(f"  - 低危 (low): {stats['low']} 条")
print(f"  - 正常 (normal): {stats['normal']} 条")
print(f"  - 总计: {stats['total']} 条")

# 8. 查看预警详情
print("\n【步骤8】预警记录示例")
print("-" * 70)

warnings = WarningRecord.objects.select_related('student', 'course')[:5]
for w in warnings:
    risk_label = {
        'high': '[HIGH]',
        'medium': '[MEDIUM]',
        'low': '[LOW]',
        'normal': '[NORMAL]'
    }.get(w.risk_level, '[UNKNOWN]')

    print(f"\n{risk_label} {w.student.name} ({w.student.student_no})")
    print(f"   课程: {w.course.name if w.course else 'N/A'}")
    print(f"   风险: {w.risk_level} | 得分: {w.composite_score}")
    print(f"   出勤: {w.attendance_score}% | 视频: {w.progress_score}% | "
          f"作业: {w.homework_score} | 考试: {w.exam_score}")

print("\n" + "=" * 70)
print("测试完成！")
print("=" * 70)
