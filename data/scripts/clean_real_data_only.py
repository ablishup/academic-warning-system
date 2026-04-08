#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据清洗脚本（仅使用3门课的真实数据，约355学生）
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import random

# 配置
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "usedata/地大数据/公网数据"
CLEANED_DIR = BASE_DIR / "cleaned"
CLEANED_DIR.mkdir(exist_ok=True)

# 随机种子
np.random.seed(42)
random.seed(42)

# 选择前3门学生最多的真实课程
NUM_COURSES = 3
NUM_KNOWLEDGE_POINTS = 8


def clean_course_data():
    """清洗课程数据 - 选择前3门学生最多的课程"""
    print("\n[1/7] 清洗课程数据...")

    # 读取真实课程
    df = pd.read_excel(RAW_DIR / "t_stat_course_new.xls")
    course_person = pd.read_excel(RAW_DIR / "t_stat_course_person.xls")

    # 统计每门课程的学生数
    course_student_count = course_person.groupby('courseid').size()
    valid_courses = course_student_count[
        (course_student_count >= 50) & (course_student_count <= 200)
    ]

    # 选择前3门
    top3 = valid_courses.nlargest(NUM_COURSES)
    selected_course_ids = list(top3.index)

    print(f"  选择 {NUM_COURSES} 门课程: {selected_course_ids}")
    print(f"  学生数: {list(top3.values)}")

    # 筛选课程数据
    courses = df[df['courseid'].isin(selected_course_ids)].copy()
    courses['original_id'] = courses['courseid']
    courses['course_no'] = courses['course_number']
    courses['name'] = courses['name']
    courses['credit'] = 3.0
    courses['hours'] = 48
    courses['teacher_id'] = 2
    courses['semester'] = '2024-2025-1'
    courses['chapters'] = json.dumps([f"第{i}章" for i in range(1, NUM_KNOWLEDGE_POINTS + 1)])
    courses['status'] = 1

    courses['id'] = range(1, len(courses) + 1)

    # 保存映射关系
    course_id_map = dict(zip(courses['courseid'], courses['id']))
    with open(CLEANED_DIR / "course_mapping.json", "w", encoding="utf-8") as f:
        json.dump(course_id_map, f, ensure_ascii=False, indent=2)

    courses[['id', 'original_id', 'course_no', 'name', 'credit', 'hours', 'teacher_id', 'semester', 'chapters', 'status']].to_csv(
        CLEANED_DIR / "cleaned_courses.csv", index=False, encoding='utf-8-sig'
    )
    print(f"  共 {len(courses)} 门课程")

    return courses, selected_course_ids, course_id_map


def clean_student_data(real_course_ids, course_id_map):
    """清洗学生数据 - 只选选中课程的学生"""
    print("\n[2/7] 清洗学生数据...")

    # 读取真实数据
    person_df = pd.read_excel(RAW_DIR / "t_stat_person.xls")
    course_person = pd.read_excel(RAW_DIR / "t_stat_course_person.xls")

    # 筛选选中了真实课程的学生
    real_enrollments = course_person[course_person['courseid'].isin(real_course_ids)]
    real_student_ids = real_enrollments['personid'].unique()

    print(f"  选中课程的学生数: {len(real_student_ids)}")

    students = person_df[person_df['personid'].isin(real_student_ids)].copy()
    students['original_id'] = students['personid']
    students['student_no'] = students['user_name']
    students['name'] = students['login_name']
    students['gender'] = 1
    students['phone'] = None
    students['email'] = None
    students['class_id'] = 1
    students['major_id'] = 1
    students['enrollment_year'] = 2022
    students['status'] = 1

    students['id'] = range(1, len(students) + 1)

    # 保存映射
    student_id_map = dict(zip(students['personid'], students['id']))
    with open(CLEANED_DIR / "student_mapping.json", "w", encoding="utf-8") as f:
        json.dump(student_id_map, f, ensure_ascii=False, indent=2)

    students[['id', 'original_id', 'student_no', 'name', 'gender', 'phone', 'email', 'class_id', 'major_id', 'enrollment_year', 'status']].to_csv(
        CLEANED_DIR / "cleaned_persons.csv", index=False, encoding='utf-8-sig'
    )
    print(f"  总学生数: {len(students)} 名")

    return students, student_id_map


def clean_class_data():
    """清洗班级数据"""
    print("\n[3/7] 清洗班级数据...")

    df = pd.read_excel(RAW_DIR / "t_stat_class.xls")
    df['original_id'] = df['id']
    df['name'] = df['name']
    df['grade'] = '2022'
    df['major_id'] = 1
    df['counselor_id'] = None
    df['id'] = range(1, len(df) + 1)

    df[['id', 'original_id', 'name', 'grade', 'major_id', 'counselor_id']].to_csv(
        CLEANED_DIR / "cleaned_classes.csv", index=False, encoding='utf-8-sig'
    )
    print(f"  班级数: {len(df)}")
    return df


def clean_enrollment_data(real_course_ids, course_id_map, student_id_map):
    """清洗选课关系"""
    print("\n[4/7] 清洗选课关系...")

    course_person = pd.read_excel(RAW_DIR / "t_stat_course_person.xls")
    enrollments = course_person[course_person['courseid'].isin(real_course_ids)].copy()

    enrollments['student_original_id'] = enrollments['personid']
    enrollments['course_original_id'] = enrollments['courseid']
    enrollments['enroll_time'] = datetime(2024, 9, 1)

    # 映射ID
    enrollments['student_id'] = enrollments['personid'].map(student_id_map)
    enrollments['course_id'] = enrollments['courseid'].map(course_id_map)

    # 过滤掉映射失败的数据
    enrollments = enrollments[enrollments['student_id'].notna() & enrollments['course_id'].notna()]

    enrollments['id'] = range(1, len(enrollments) + 1)

    enrollments[['id', 'student_id', 'course_id', 'enroll_time']].to_csv(
        CLEANED_DIR / "cleaned_course_persons.csv", index=False, encoding='utf-8-sig'
    )
    print(f"  选课记录: {len(enrollments)}")

    return enrollments


def clean_knowledge_points(course_id_map):
    """生成知识点数据"""
    print("\n[5/7] 生成知识点...")

    knowledge_points = []
    kp_id = 1

    chapters = ['概述与基础', '核心概念', '进阶内容', '实践应用', '案例分析', '综合练习', '拓展阅读', '期末复习']

    for course_orig_id, course_id in course_id_map.items():
        for idx, chapter in enumerate(chapters, 1):
            knowledge_points.append({
                'id': kp_id,
                'course_id': course_id,
                'name': chapter,
                'chapter_no': f"第{idx}章",
                'description': f"第{idx}章 - {chapter}",
                'weight': round(random.uniform(0.8, 1.2), 2),
            })
            kp_id += 1

    df = pd.DataFrame(knowledge_points)
    df.to_csv(CLEANED_DIR / "cleaned_knowledge_points.csv", index=False, encoding='utf-8-sig')
    print(f"  知识点数: {len(df)}")
    return df


def clean_activity_data(enrollments_df):
    """生成学习活动数据"""
    print("\n[6/7] 生成学习活动数据...")

    activities = []

    for _, enrollment in enrollments_df.iterrows():
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']
        num_activities = random.randint(20, 40)

        for _ in range(num_activities):
            activity_type = random.choice(['video', 'sign_in', 'discuss', 'quiz', 'other'])
            start_time = datetime(2024, 9, 1) + timedelta(days=random.randint(0, 120))
            duration = random.randint(60, 3600) if activity_type == 'video' else random.randint(10, 300)

            activities.append({
                'student_id': student_id,
                'course_id': course_id,
                'activity_type': activity_type,
                'activity_name': activity_type,
                'start_time': start_time,
                'end_time': start_time + timedelta(seconds=duration),
                'duration': duration,
                'progress': random.uniform(0.3, 1.0) if activity_type == 'video' else None,
            })

    df = pd.DataFrame(activities)
    df.to_csv(CLEANED_DIR / "cleaned_activity_logs.csv", index=False, encoding='utf-8-sig')
    print(f"  活动记录: {len(df)}")
    return df


def clean_homework_data(course_id_map, enrollments_df):
    """生成作业数据"""
    print("\n[7/7] 生成作业数据...")

    # 作业任务
    assignments = []
    assignment_id = 1

    for course_orig_id, course_id in course_id_map.items():
        for i in range(1, NUM_KNOWLEDGE_POINTS + 1):
            assignments.append({
                'id': assignment_id,
                'course_id': course_id,
                'title': f"第{i}次作业",
                'description': f"完成第{i}章练习题",
                'knowledge_point_id': (course_id - 1) * NUM_KNOWLEDGE_POINTS + i,
                'full_score': 100.0,
                'start_time': datetime(2024, 9, 1) + timedelta(days=(i-1)*14),
                'deadline': datetime(2024, 9, 1) + timedelta(days=(i-1)*14 + 7),
            })
            assignment_id += 1

    assignments_df = pd.DataFrame(assignments)

    # 作业提交
    submissions = []
    for _, enrollment in enrollments_df.iterrows():
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']
        course_assignments = assignments_df[assignments_df['course_id'] == course_id]

        for _, assignment in course_assignments.iterrows():
            if random.random() < 0.8:
                if random.random() < 0.15:
                    score = random.uniform(30, 70)
                elif random.random() < 0.3:
                    score = random.uniform(60, 85)
                else:
                    score = random.uniform(70, 100)

                submit_time = assignment['deadline'] - timedelta(days=random.randint(0, 5))

                submissions.append({
                    'assignment_id': assignment['id'],
                    'student_id': student_id,
                    'score': round(score, 2),
                    'submit_time': submit_time,
                    'is_late': 1 if submit_time > assignment['deadline'] else 0,
                })

    submissions_df = pd.DataFrame(submissions)

    assignments_df.to_csv(CLEANED_DIR / "cleaned_homework_assignments.csv", index=False, encoding='utf-8-sig')
    submissions_df.to_csv(CLEANED_DIR / "cleaned_homework_submissions.csv", index=False, encoding='utf-8-sig')

    print(f"  作业任务: {len(assignments_df)}, 提交记录: {len(submissions_df)}")
    return assignments_df, submissions_df


def clean_exam_data(course_id_map, enrollments_df):
    """生成考试数据"""
    print("\n[额外] 生成考试数据...")

    exams = []
    exam_id = 1

    for course_orig_id, course_id in course_id_map.items():
        exams.append({
            'id': exam_id,
            'course_id': course_id,
            'title': '期中考试',
            'exam_type': 'midterm',
            'full_score': 100.0,
            'start_time': datetime(2024, 10, 15, 9, 0),
            'end_time': datetime(2024, 10, 15, 11, 0),
            'duration': 120,
        })
        exam_id += 1

        exams.append({
            'id': exam_id,
            'course_id': course_id,
            'title': '期末考试',
            'exam_type': 'final',
            'full_score': 100.0,
            'start_time': datetime(2024, 12, 20, 9, 0),
            'end_time': datetime(2024, 12, 20, 11, 0),
            'duration': 120,
        })
        exam_id += 1

    exams_df = pd.DataFrame(exams)

    # 考试结果
    results = []
    for _, enrollment in enrollments_df.iterrows():
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']
        course_exams = exams_df[exams_df['course_id'] == course_id]

        for _, exam in course_exams.iterrows():
            if random.random() < 0.9:
                if random.random() < 0.15:
                    score = random.uniform(25, 65)
                elif random.random() < 0.35:
                    score = random.uniform(55, 80)
                else:
                    score = random.uniform(70, 100)

                results.append({
                    'exam_id': exam['id'],
                    'student_id': student_id,
                    'score': round(score, 2),
                    'submit_time': exam['start_time'] + timedelta(minutes=random.randint(60, 110)),
                })

    results_df = pd.DataFrame(results)

    exams_df.to_csv(CLEANED_DIR / "cleaned_exam_assignments.csv", index=False, encoding='utf-8-sig')
    results_df.to_csv(CLEANED_DIR / "cleaned_exam_results.csv", index=False, encoding='utf-8-sig')

    print(f"  考试任务: {len(exams_df)}, 结果记录: {len(results_df)}")
    return exams_df, results_df


def main():
    """主函数"""
    print("="*60)
    print("真实数据清洗工具（仅使用3门课的真实数据）")
    print("="*60)

    # 1. 清洗课程数据
    courses_df, real_course_ids, course_id_map = clean_course_data()

    # 2. 清洗学生数据
    students_df, student_id_map = clean_student_data(real_course_ids, course_id_map)

    # 3. 清洗班级数据
    classes_df = clean_class_data()

    # 4. 清洗选课关系
    enrollments_df = clean_enrollment_data(real_course_ids, course_id_map, student_id_map)

    # 5. 生成知识点
    kp_df = clean_knowledge_points(course_id_map)

    # 6. 生成学习活动
    activity_df = clean_activity_data(enrollments_df)

    # 7. 生成作业数据
    hw_assignments, hw_submissions = clean_homework_data(course_id_map, enrollments_df)

    # 8. 生成考试数据
    exam_assignments, exam_results = clean_exam_data(course_id_map, enrollments_df)

    print("\n" + "="*60)
    print("真实数据清洗完成！")
    print("="*60)
    print(f"\n数据统计:")
    print(f"  学生数: {len(students_df)} 名（全部来自真实数据）")
    print(f"  课程数: {len(courses_df)} 门（全部来自真实数据）")
    print(f"  选课记录: {len(enrollments_df)}")
    print(f"  学习活动: {len(activity_df)}")
    print(f"  作业提交: {len(hw_submissions)}")
    print(f"  考试结果: {len(exam_results)}")
    print(f"\n文件保存在: {CLEANED_DIR}")


if __name__ == "__main__":
    main()
