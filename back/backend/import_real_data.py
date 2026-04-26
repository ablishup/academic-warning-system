#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入真实学习数据到系统
- 调整选课关系以匹配原始数据
- 基于raw_id映射导入真实指标
- 重新计算StudentCourseScore和WarningRecord
"""

import os
import sys
import django
import pandas as pd

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import transaction
from classes.models import Student, Class
from courses.models import Course, CourseEnrollment
from warning_system.models import StudentCourseScore, WarningRecord
from algorithm.warning_predictor import WarningPredictor

print("=" * 70)
print("导入真实学习数据")
print("=" * 70)

# ============================================================
# 1. 读取原始数据
# ============================================================
print("\n【步骤1】读取原始数据...")

RAW_DIR = 'C:/Users/ablis/Desktop/project/data/raw'

person = pd.read_excel(f'{RAW_DIR}/t_stat_person.xls')
raw_students = person[person['role'] == 3]

cp = pd.read_excel(f'{RAW_DIR}/t_stat_course_person.xls')
activity = pd.read_excel(f'{RAW_DIR}/t_stat_activity_log.xls')
work = pd.read_excel(f'{RAW_DIR}/t_stat_work_answer.xls')
exam = pd.read_excel(f'{RAW_DIR}/t_stat_exam_answer.xls')
student_score = pd.read_excel(f'{RAW_DIR}/t_stat_student_score.xls')
job = pd.read_excel(f'{RAW_DIR}/t_stat_job_finish.xls')

print(f"  原始学生数: {len(raw_students)}")
print(f"  课程-学生关系: {len(cp)}")
print(f"  活动日志: {len(activity)}")
print(f"  作业答案: {len(work)}")
print(f"  考试答案: {len(exam)}")
print(f"  学生成绩: {len(student_score)}")
print(f"  作业完成: {len(job)}")

# ============================================================
# 2. 建立映射
# ============================================================
print("\n【步骤2】建立映射...")

# 原始courseid -> 系统course_id 映射
COURSE_MAP = {
    222807286: 4,   # 数据结构
    222820410: 9,   # 数据库原理
}

# raw_id -> student 映射
raw_to_student = {}
for s in Student.objects.exclude(raw_id__isnull=True).exclude(raw_id=''):
    try:
        raw_to_student[int(s.raw_id)] = s
    except:
        pass

print(f"  raw_id映射: {len(raw_to_student)} 名学生")

# ============================================================
# 3. 调整选课关系
# ============================================================
print("\n【步骤3】调整选课关系...")

# 清除现有选课
CourseEnrollment.objects.all().delete()
print("  已清除现有选课")

# 获取课程
courses = {c.id: c for c in Course.objects.all()}
course_map_by_name = {
    '数据结构': courses.get(4),
    '软件工程': courses.get(5),
    '操作系统': courses.get(6),
    '人工智能导论': courses.get(7),
    '计算机网络': courses.get(8),
    '数据库原理': courses.get(9),
}

# 新的选课分配（最大化真实数据覆盖）
grade_courses = {
    '2021': [course_map_by_name['数据库原理'], course_map_by_name['计算机网络']],
    '2020': [course_map_by_name['数据结构'], course_map_by_name['操作系统']],
    '2019': [course_map_by_name['软件工程'], course_map_by_name['人工智能导论']],
}

total_enrollments = 0
for grade, course_list in grade_courses.items():
    students = Student.objects.filter(enrollment_year=int(grade))
    count = 0
    for s in students:
        for c in course_list:
            if c:
                CourseEnrollment.objects.create(
                    student_id=s.id,
                    course_id=c.id,
                    status=1
                )
                count += 1
    print(f"  {grade}级: {students.count()}人 -> {[c.name for c in course_list if c]} ({count}条)")
    total_enrollments += count

print(f"  总计: {total_enrollments} 条选课记录")

# ============================================================
# 4. 计算真实指标
# ============================================================
print("\n【步骤4】计算真实指标...")

# 出勤率计算
attend = activity[activity['dtype'] == 'AttendLog']

def calc_attendance_rate(personid, courseid):
    """计算出勤率"""
    subset = attend[(attend['personid'] == personid) & (attend['courseid'] == courseid)]
    if subset.empty:
        return None

    # 该课程的总签到次数（唯一attend_id）
    course_attends = attend[attend['courseid'] == courseid]['attend_id'].nunique()
    if course_attends == 0:
        return None

    # 该学生的实际签到次数（唯一attend_id）
    student_attends = subset['attend_id'].nunique()

    rate = (student_attends / course_attends) * 100
    return min(rate, 100)

# 作业平均分
work_avg = work.groupby(['personid', 'courseid'])['score'].mean().reset_index()
work_avg_dict = {}
for _, row in work_avg.iterrows():
    work_avg_dict[(int(row['personid']), int(row['courseid']))] = row['score']

# 作业提交率
job_counts = job.groupby(['personid', 'courseid']).size().reset_index(name='count')
job_dict = {}
for _, row in job_counts.iterrows():
    job_dict[(int(row['personid']), int(row['courseid']))] = row['count']

# 考试平均分
exam_avg = exam.groupby(['personid', 'courseid'])['score'].mean().reset_index()
exam_avg_dict = {}
for _, row in exam_avg.iterrows():
    exam_avg_dict[(int(row['personid']), int(row['courseid']))] = row['score']

# 学生成绩（作为video_progress代理）
score_dict = {}
for courseid in [222807286, 222820410]:
    subset = student_score[student_score['courseid'] == courseid]
    if not subset.empty:
        max_score = subset['score'].max()
        for _, row in subset.iterrows():
            if max_score > 0:
                score_dict[(int(row['personid']), int(row['courseid']))] = (row['score'] / max_score) * 100
            else:
                score_dict[(int(row['personid']), int(row['courseid']))] = 0

print("  指标计算完成")
print(f"  出勤记录: {len(attend)} 条")
print(f"  作业平均: {len(work_avg_dict)} 条")
print(f"  考试平均: {len(exam_avg_dict)} 条")
print(f"  成绩记录: {len(score_dict)} 条")

# ============================================================
# 5. 清除旧数据，创建新的StudentCourseScore
# ============================================================
print("\n【步骤5】创建StudentCourseScore...")

StudentCourseScore.objects.all().delete()
WarningRecord.objects.all().delete()
print("  已清除旧的Score和Warning记录")

created_count = 0
real_data_count = 0

for raw_id, student in raw_to_student.items():
    for raw_courseid, course_id in COURSE_MAP.items():
        # 检查该学生是否选了这门课
        if not CourseEnrollment.objects.filter(student_id=student.id, course_id=course_id).exists():
            continue

        # 计算各项指标
        attendance = calc_attendance_rate(raw_id, raw_courseid)
        hw_avg = work_avg_dict.get((raw_id, raw_courseid))
        exam_avg_score = exam_avg_dict.get((raw_id, raw_courseid))
        video_prog = score_dict.get((raw_id, raw_courseid))

        # 判断是否有真实数据
        has_real_data = any(x is not None for x in [attendance, hw_avg, exam_avg_score, video_prog])
        if has_real_data:
            real_data_count += 1

        # 如果没有真实数据，使用合理的默认值
        if attendance is None:
            attendance = 75.0
        if hw_avg is None:
            hw_avg = 70.0
        if exam_avg_score is None:
            exam_avg_score = hw_avg
        if video_prog is None:
            video_prog = 60.0

        # 作业提交率
        total_jobs = job[job['courseid'] == raw_courseid]['job_id'].nunique()
        completed_jobs = job_dict.get((raw_id, raw_courseid), 0)
        if total_jobs > 0:
            submit_rate = (completed_jobs / total_jobs) * 100
        else:
            submit_rate = 80.0

        StudentCourseScore.objects.create(
            student_id=student.id,
            course_id=course_id,
            attendance_rate=round(attendance, 2),
            video_progress=round(video_prog, 2),
            homework_avg=round(hw_avg, 2),
            homework_submit_rate=round(submit_rate, 2),
            exam_avg=round(exam_avg_score, 2),
            knowledge_mastery=round((hw_avg + exam_avg_score) / 2, 2),
            final_score=None
        )
        created_count += 1

print(f"  创建了 {created_count} 条 StudentCourseScore 记录")
print(f"  其中含真实数据: {real_data_count} 条")

# ============================================================
# 6. 为没有真实数据的课程创建模拟数据
# ============================================================
print("\n【步骤6】为其他课程创建模拟数据...")

import random
random.seed(42)

def generate_score_for_level(expected_level):
    """根据预期风险等级生成分数"""
    if expected_level == 'high':
        return {
            'attendance_rate': random.uniform(30, 60),
            'video_progress': random.uniform(20, 50),
            'homework_avg': random.uniform(40, 58),
            'exam_avg': random.uniform(35, 55),
        }
    elif expected_level == 'medium':
        return {
            'attendance_rate': random.uniform(60, 75),
            'video_progress': random.uniform(55, 70),
            'homework_avg': random.uniform(60, 72),
            'exam_avg': random.uniform(58, 70),
        }
    elif expected_level == 'low':
        return {
            'attendance_rate': random.uniform(78, 88),
            'video_progress': random.uniform(75, 85),
            'homework_avg': random.uniform(75, 82),
            'exam_avg': random.uniform(72, 82),
        }
    else:
        return {
            'attendance_rate': random.uniform(90, 100),
            'video_progress': random.uniform(88, 100),
            'homework_avg': random.uniform(85, 95),
            'exam_avg': random.uniform(82, 95),
        }

mock_count = 0
enrollments = CourseEnrollment.objects.exclude(course_id__in=[4, 9])

for enroll in enrollments:
    rand = random.random()
    if rand < 0.15:
        level = 'high'
    elif rand < 0.35:
        level = 'medium'
    elif rand < 0.60:
        level = 'low'
    else:
        level = 'normal'

    scores = generate_score_for_level(level)

    StudentCourseScore.objects.create(
        student_id=enroll.student_id,
        course_id=enroll.course_id,
        attendance_rate=round(scores['attendance_rate'], 2),
        video_progress=round(scores['video_progress'], 2),
        homework_avg=round(scores['homework_avg'], 2),
        homework_submit_rate=round(random.uniform(60, 100), 2),
        exam_avg=round(scores['exam_avg'], 2),
        knowledge_mastery=round((scores['homework_avg'] + scores['exam_avg']) / 2, 2),
        final_score=None
    )
    mock_count += 1

print(f"  创建了 {mock_count} 条模拟 StudentCourseScore 记录")

# ============================================================
# 6.5 使用真实数据训练模型
# ============================================================
print("\n【步骤6.5】使用真实数据训练模型...")

from algorithm.features import FeatureEngineering

def build_training_data():
    """从所有StudentCourseScore构建训练数据"""
    training_data = []
    for score in StudentCourseScore.objects.all():
        features_dict = {
            'attendance_rate': float(score.attendance_rate),
            'video_progress': float(score.video_progress),
            'video_completion_rate': float(score.video_progress) * 0.9,
            'homework_avg_score': float(score.homework_avg),
            'homework_submit_rate': float(score.homework_submit_rate),
            'homework_late_rate': max(0, 100 - float(score.homework_submit_rate)) * 0.2,
            'exam_avg_score': float(score.exam_avg),
            'exam_pass_rate': 100 if float(score.exam_avg) >= 60 else float(score.exam_avg),
            'exam_attendance_rate': float(score.attendance_rate),
            'avg_daily_learning_minutes': float(score.video_progress) * 0.5,
        }

        composite = (
            features_dict['attendance_rate'] * 0.3 +
            features_dict['video_progress'] * 0.2 +
            features_dict['homework_avg_score'] * 0.3 +
            features_dict['exam_avg_score'] * 0.2
        )
        composite = round(composite, 2)

        risk_level = FeatureEngineering.determine_risk_level(composite)
        training_data.append((features_dict, composite, risk_level))

    return training_data

training_data = build_training_data()
print(f"  构建了 {len(training_data)} 条训练数据")

# 统计训练数据的等级分布
level_counts = {}
for _, _, level in training_data:
    level_counts[level] = level_counts.get(level, 0) + 1
print(f"  训练数据等级分布: {level_counts}")

predictor = WarningPredictor()
print("  训练模型...")
results = predictor.train(training_data=training_data)
print(f"  模型训练完成! 分类准确率: {results.get('classification_accuracy', 0):.2%}")

# ============================================================
# 7. 重新计算预警
# ============================================================
print("\n【步骤7】重新计算预警...")

warnings_created = 0
warnings_by_level = {'high': 0, 'medium': 0, 'low': 0, 'normal': 0}

all_scores = StudentCourseScore.objects.all()
for score in all_scores:
    # 构建完整的特征向量（必须与训练时一致）
    features_dict = {
        'attendance_rate': float(score.attendance_rate),
        'video_progress': float(score.video_progress),
        'video_completion_rate': float(score.video_progress) * 0.9,
        'homework_avg_score': float(score.homework_avg),
        'homework_submit_rate': float(score.homework_submit_rate),
        'homework_late_rate': max(0, 100 - float(score.homework_submit_rate)) * 0.2,
        'exam_avg_score': float(score.exam_avg),
        'exam_pass_rate': 100 if float(score.exam_avg) >= 60 else float(score.exam_avg),
        'exam_attendance_rate': float(score.attendance_rate),
        'avg_daily_learning_minutes': float(score.video_progress) * 0.5,
    }

    result = predictor.predict(
        student_id=score.student_id,
        course_id=score.course_id,
        features_dict=features_dict
    )

    risk_level = result['risk_level']
    warnings_by_level[risk_level] += 1

    if risk_level != 'normal':
        WarningRecord.objects.create(
            student_id=score.student_id,
            course_id=score.course_id,
            risk_level=risk_level,
            composite_score=result['predicted_score'],
            attendance_score=score.attendance_rate,
            progress_score=score.video_progress,
            homework_score=score.homework_avg,
            exam_score=score.exam_avg,
            status='active'
        )
        warnings_created += 1

print(f"  预警计算完成！")
print(f"  新增预警: {warnings_created} 条")
print(f"  高危: {warnings_by_level['high']}")
print(f"  中等: {warnings_by_level['medium']}")
print(f"  低危: {warnings_by_level['low']}")
print(f"  正常: {warnings_by_level['normal']}")

# ============================================================
# 8. 统计摘要
# ============================================================
print("\n" + "=" * 70)
print("导入完成摘要")
print("=" * 70)

print(f"\nStudentCourseScore 总计: {StudentCourseScore.objects.count()}")
print(f"WarningRecord 总计: {WarningRecord.objects.count()}")

print("\n按课程统计:")
for c in Course.objects.all().order_by('id'):
    scores = StudentCourseScore.objects.filter(course_id=c.id)
    warnings = WarningRecord.objects.filter(course_id=c.id)
    print(f"  {c.name}: {scores.count()}条分数, {warnings.count()}条预警")

print("\n按风险等级统计:")
for level in ['high', 'medium', 'low', 'normal']:
    count = WarningRecord.objects.filter(risk_level=level, status='active').count()
    print(f"  {level}: {count}")

print("\n" + "=" * 70)
print("数据导入完成！")
print("=" * 70)
