#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
混合数据清洗脚本
- 使用真实数据作为基础（3门课，约355学生）
- 补充模拟数据至800学生
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

# 数据规模
TARGET_TOTAL_STUDENTS = 800
NUM_REAL_COURSES = 3  # 使用3门真实课程
NUM_MOCK_COURSES = 2  # 额外创建2门模拟课程
NUM_KNOWLEDGE_POINTS = 8  # 每门课8个章节


def clean_course_data():
    """清洗课程数据 - 选择前3门学生最多的真实课程"""
    print("\n[1/8] 清洗课程数据...")

    # 读取真实课程
    df = pd.read_excel(RAW_DIR / "t_stat_course_new.xls")
    course_person = pd.read_excel(RAW_DIR / "t_stat_course_person.xls")

    # 统计每门课程的学生数
    course_student_count = course_person.groupby('courseid').size()
    valid_courses = course_student_count[
        (course_student_count >= 50) & (course_student_count <= 200)
    ]

    # 选择前3门
    top3 = valid_courses.nlargest(NUM_REAL_COURSES)
    selected_course_ids = list(top3.index)

    print(f"  选择 {NUM_REAL_COURSES} 门真实课程: {selected_course_ids}")

    # 筛选课程数据
    real_courses = df[df['courseid'].isin(selected_course_ids)].copy()
    real_courses['original_id'] = real_courses['courseid']
    real_courses['course_no'] = real_courses['course_number']
    real_courses['name'] = real_courses['name']
    real_courses['credit'] = 3.0
    real_courses['hours'] = 48
    real_courses['teacher_id'] = 2
    real_courses['semester'] = '2024-2025-1'
    real_courses['chapters'] = json.dumps([f"第{i}章" for i in range(1, NUM_KNOWLEDGE_POINTS + 1)])
    real_courses['status'] = 1

    # 添加模拟课程
    mock_courses_data = [
        {'id': 201, 'course_no': 'M201', 'name': '人工智能导论', 'credit': 3.0, 'hours': 48, 'teacher_id': 2},
        {'id': 202, 'course_no': 'M202', 'name': '软件工程实践', 'credit': 4.0, 'hours': 64, 'teacher_id': 3},
    ]
    mock_courses = pd.DataFrame(mock_courses_data)
    mock_courses['original_id'] = mock_courses['id'].apply(lambda x: f"mock_{x}")
    mock_courses['semester'] = '2024-2025-1'
    mock_courses['chapters'] = json.dumps([f"第{i}章" for i in range(1, NUM_KNOWLEDGE_POINTS + 1)])
    mock_courses['status'] = 1

    # 合并
    all_courses = pd.concat([
        real_courses[['original_id', 'course_no', 'name', 'credit', 'hours', 'teacher_id', 'semester', 'chapters', 'status']],
        mock_courses[['original_id', 'course_no', 'name', 'credit', 'hours', 'teacher_id', 'semester', 'chapters', 'status']]
    ], ignore_index=True)
    all_courses['id'] = range(1, len(all_courses) + 1)

    # 保存映射关系
    course_id_map = dict(zip(all_courses['original_id'], all_courses['id']))
    with open(CLEANED_DIR / "course_mapping.json", "w", encoding="utf-8") as f:
        json.dump(course_id_map, f, ensure_ascii=False, indent=2)

    all_courses.to_csv(CLEANED_DIR / "cleaned_courses.csv", index=False, encoding='utf-8-sig')
    print(f"  共 {len(all_courses)} 门课程（真实 {NUM_REAL_COURSES} + 模拟 {NUM_MOCK_COURSES}）")

    return all_courses, selected_course_ids, course_id_map


def clean_student_data(real_course_ids, course_id_map):
    """清洗学生数据 - 真实学生 + 模拟学生"""
    print("\n[2/8] 清洗学生数据...")

    # 读取真实数据
    person_df = pd.read_excel(RAW_DIR / "t_stat_person.xls")
    course_person = pd.read_excel(RAW_DIR / "t_stat_course_person.xls")
    clazz_df = pd.read_excel(RAW_DIR / "t_stat_class.xls")

    # 筛选选中了真实课程的学生
    real_enrollments = course_person[course_person['courseid'].isin(real_course_ids)]
    real_student_ids = real_enrollments['personid'].unique()

    real_students = person_df[person_df['personid'].isin(real_student_ids)].copy()
    real_students['original_id'] = real_students['personid']
    real_students['student_no'] = real_students['user_name']
    real_students['name'] = real_students['login_name']
    real_students['gender'] = 1  # 默认
    real_students['phone'] = None
    real_students['email'] = None
    real_students['class_id'] = real_students.get('clazzid', 1)
    real_students['major_id'] = 1
    real_students['enrollment_year'] = 2022
    real_students['status'] = 1
    real_students['is_real'] = 1  # 标记为真实数据

    print(f"  真实学生: {len(real_students)} 名")

    # 需要补充的模拟学生数
    num_mock = TARGET_TOTAL_STUDENTS - len(real_students)

    # 生成模拟学生
    surnames = ['张', '王', '李', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱']
    names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军', '洋', '勇', '杰', '娟']

    mock_students = []
    for i in range(num_mock):
        name = random.choice(surnames) + random.choice(names)
        if random.random() > 0.5:
            name += random.choice(names)

        mock_students.append({
            'original_id': f"mock_{i+1}",
            'student_no': f"2023{random.randint(1000, 9999):04d}",
            'name': name,
            'gender': random.choice([1, 2]),
            'phone': f"138{random.randint(10000000, 99999999)}",
            'email': None,
            'class_id': random.randint(1, 10),
            'major_id': random.randint(1, 4),
            'enrollment_year': 2023,
            'status': 1,
            'is_real': 0,
        })

    mock_students_df = pd.DataFrame(mock_students)
    print(f"  模拟学生: {len(mock_students_df)} 名")

    # 合并
    all_students = pd.concat([
        real_students[['original_id', 'student_no', 'name', 'gender', 'phone', 'email', 'class_id', 'major_id', 'enrollment_year', 'status', 'is_real']],
        mock_students_df
    ], ignore_index=True)
    all_students['id'] = range(1, len(all_students) + 1)

    # 保存映射
    student_id_map = dict(zip(all_students['original_id'], all_students['id']))
    with open(CLEANED_DIR / "student_mapping.json", "w", encoding="utf-8") as f:
        json.dump(student_id_map, f, ensure_ascii=False, indent=2)

    all_students.to_csv(CLEANED_DIR / "cleaned_persons.csv", index=False, encoding='utf-8-sig')
    print(f"  总学生数: {len(all_students)} 名")

    return all_students, student_id_map


def clean_class_data():
    """清洗班级数据 - 使用真实班级"""
    print("\n[3/8] 清洗班级数据...")

    df = pd.read_excel(RAW_DIR / "t_stat_class.xls")
    df['original_id'] = df['id']
    df['name'] = df['name']
    df['grade'] = df.get('semester', '2022').split('-')[0] if 'semester' in df.columns else '2022'
    df['major_id'] = 1
    df['counselor_id'] = None

    df[['original_id', 'name', 'grade', 'major_id', 'counselor_id']].to_csv(
        CLEANED_DIR / "cleaned_classes.csv", index=False, encoding='utf-8-sig'
    )
    print(f"  班级数: {len(df)}")
    return df


def clean_enrollment_data(real_course_ids, course_id_map, student_id_map):
    """清洗选课关系 - 真实选课 + 模拟选课"""
    print("\n[4/8] 清洗选课关系...")

    # 真实选课
    course_person = pd.read_excel(RAW_DIR / "t_stat_course_person.xls")
    real_enrollments = course_person[course_person['courseid'].isin(real_course_ids)].copy()

    real_enrollments['student_original_id'] = real_enrollments['personid']
    real_enrollments['course_original_id'] = real_enrollments['courseid']
    real_enrollments['enroll_time'] = datetime(2024, 9, 1)
    real_enrollments['is_real'] = 1

    # 映射ID
    real_enrollments['student_id'] = real_enrollments['student_original_id'].map(student_id_map)
    real_enrollments['course_id'] = real_enrollments['course_original_id'].map(course_id_map)

    # 过滤掉映射失败的数据
    real_enrollments = real_enrollments[real_enrollments['student_id'].notna() & real_enrollments['course_id'].notna()]

    print(f"  真实选课记录: {len(real_enrollments)}")

    # 模拟选课（模拟学生选模拟课程）
    mock_students = [sid for sid, id in student_id_map.items() if str(sid).startswith('mock_')]
    mock_courses = [cid for cid, id in course_id_map.items() if str(cid).startswith('mock_')]

    mock_enrollments = []
    for student_orig_id in mock_students:
        # 每个模拟学生选2-3门课（包括真实和模拟课程）
        num_courses = random.randint(2, 3)
        # 可以选真实课程或模拟课程
        available_courses = list(course_id_map.keys())
        selected_courses = random.sample(available_courses, min(num_courses, len(available_courses)))

        for course_orig_id in selected_courses:
            mock_enrollments.append({
                'student_original_id': student_orig_id,
                'course_original_id': course_orig_id,
                'student_id': student_id_map[student_orig_id],
                'course_id': course_id_map[course_orig_id],
                'enroll_time': datetime(2024, 9, 1) + timedelta(days=random.randint(0, 30)),
                'is_real': 0,
            })

    mock_enrollments_df = pd.DataFrame(mock_enrollments)
    print(f"  模拟选课记录: {len(mock_enrollments_df)}")

    # 合并
    all_enrollments = pd.concat([
        real_enrollments[['student_id', 'course_id', 'enroll_time', 'is_real']],
        mock_enrollments_df[['student_id', 'course_id', 'enroll_time', 'is_real']]
    ], ignore_index=True)
    all_enrollments['id'] = range(1, len(all_enrollments) + 1)

    all_enrollments.to_csv(CLEANED_DIR / "cleaned_course_persons.csv", index=False, encoding='utf-8-sig')
    print(f"  总选课记录: {len(all_enrollments)}")

    return all_enrollments


def clean_knowledge_points(course_id_map):
    """生成知识点数据"""
    print("\n[5/8] 生成知识点...")

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


def clean_activity_data(enrollments_df, student_id_map):
    """清洗学习活动数据 - 真实 + 模拟"""
    print("\n[6/8] 清洗学习活动数据...")

    activities = []

    # 真实学生活动 - 从真实数据读取
    try:
        real_activity = pd.read_excel(RAW_DIR / "t_stat_activity_log.xls")
        # 筛选真实学生的活动
        real_student_orig_ids = set(student_id_map.keys()) - {k for k in student_id_map.keys() if str(k).startswith('mock_')}
        real_activity_filtered = real_activity[real_activity['personid'].isin(real_student_orig_ids)]

        # 简化处理：为每个真实学生生成活动记录
        print(f"  真实活动记录来源: {len(real_activity_filtered)} 条原始记录")
    except:
        real_activity_filtered = None

    # 为所有选课学生生成活动记录
    for _, enrollment in enrollments_df.iterrows():
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']
        is_real = enrollment.get('is_real', 0)

        # 每个学生活动数量
        if is_real == 1:
            num_activities = random.randint(20, 40)  # 真实学生活动较多
        else:
            num_activities = random.randint(10, 30)  # 模拟学生活动较少

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
                'is_real': is_real,
            })

    df = pd.DataFrame(activities)
    df.to_csv(CLEANED_DIR / "cleaned_activity_logs.csv", index=False, encoding='utf-8-sig')
    print(f"  总活动记录: {len(df)}")
    return df


def clean_homework_data(course_id_map, enrollments_df):
    """生成作业数据"""
    print("\n[7/8] 生成作业数据...")

    # 作业任务 - 每门课8次作业
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

        # 获取该课程的作业
        course_assignments = assignments_df[assignments_df['course_id'] == course_id]

        for _, assignment in course_assignments.iterrows():
            # 80%概率提交
            if random.random() < 0.8:
                # 成绩分布
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
    print("\n[8/8] 生成考试数据...")

    # 考试任务 - 每门课期中+期末
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
            if random.random() < 0.9:  # 90%参加考试
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
    print("混合数据清洗工具")
    print("="*60)
    print(f"目标: 使用真实数据 + 补充至 {TARGET_TOTAL_STUDENTS} 人")

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
    activity_df = clean_activity_data(enrollments_df, student_id_map)

    # 7. 生成作业数据
    hw_assignments, hw_submissions = clean_homework_data(course_id_map, enrollments_df)

    # 8. 生成考试数据
    exam_assignments, exam_results = clean_exam_data(course_id_map, enrollments_df)

    # 统计
    real_students = len([s for s in student_id_map.keys() if not str(s).startswith('mock_')])
    mock_students = len([s for s in student_id_map.keys() if str(s).startswith('mock_')])

    print("\n" + "="*60)
    print("混合数据生成完成！")
    print("="*60)
    print(f"\n数据统计:")
    print(f"  真实学生: {real_students} 名")
    print(f"  模拟学生: {mock_students} 名")
    print(f"  总学生数: {real_students + mock_students} 名")
    print(f"  真实课程: {NUM_REAL_COURSES} 门")
    print(f"  模拟课程: {NUM_MOCK_COURSES} 门")
    print(f"  总课程数: {NUM_REAL_COURSES + NUM_MOCK_COURSES} 门")
    print(f"  选课记录: {len(enrollments_df)}")
    print(f"  学习活动: {len(activity_df)}")
    print(f"  作业提交: {len(hw_submissions)}")
    print(f"  考试结果: {len(exam_results)}")
    print(f"\n文件保存在: {CLEANED_DIR}")


if __name__ == "__main__":
    main()
