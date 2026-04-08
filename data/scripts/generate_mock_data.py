#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟数据生成脚本
生成500-1000学生的学业预警演示数据
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import random

# 配置
BASE_DIR = Path(__file__).parent.parent
MOCK_DIR = BASE_DIR / "mock"
MOCK_DIR.mkdir(exist_ok=True)

# 随机种子（保证可重复）
np.random.seed(42)
random.seed(42)

# 数据规模配置
NUM_STUDENTS = 800          # 学生数量
NUM_COURSES = 4             # 课程数量
NUM_CLASSES = 10            # 班级数量
NUM_KNOWLEDGE_POINTS = 8    # 每门课程知识点数量


def generate_majors():
    """生成专业数据"""
    majors = [
        {'id': 1, 'name': '计算机科学与技术', 'code': 'CS001', 'department': '计算机学院'},
        {'id': 2, 'name': '软件工程', 'code': 'SE001', 'department': '软件学院'},
        {'id': 3, 'name': '数据科学与大数据技术', 'code': 'DS001', 'department': '数据学院'},
        {'id': 4, 'name': '人工智能', 'code': 'AI001', 'department': '人工智能学院'},
    ]
    return pd.DataFrame(majors)


def generate_classes(majors_df):
    """生成班级数据"""
    classes = []
    grades = ['2021', '2022', '2023']

    for i in range(1, NUM_CLASSES + 1):
        major_id = random.choice(majors_df['id'].tolist())
        grade = random.choice(grades)
        classes.append({
            'id': i,
            'name': f"{grade}级{i}班",
            'grade': grade,
            'major_id': major_id,
            'counselor_id': None,  # 稍后填充
            'student_count': 0,
        })

    return pd.DataFrame(classes)


def generate_students(classes_df):
    """生成学生数据"""
    students = []
    surnames = ['张', '王', '李', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
    names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
             '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞']

    for i in range(1, NUM_STUDENTS + 1):
        class_id = random.choice(classes_df['id'].tolist())
        class_info = classes_df[classes_df['id'] == class_id].iloc[0]

        # 生成姓名
        name = random.choice(surnames) + random.choice(names)
        if random.random() > 0.5:
            name += random.choice(names)

        # 生成学号
        grade = class_info['grade']
        student_no = f"{grade}{class_id:02d}{i:04d}"

        students.append({
            'id': i,
            'student_no': student_no,
            'name': name,
            'gender': random.choice([1, 2]),
            'phone': f"138{random.randint(10000000, 99999999)}",
            'email': f"{student_no}@example.edu.cn",
            'class_id': class_id,
            'major_id': class_info['major_id'],
            'enrollment_year': int(grade),
            'status': 1,
            'original_id': f"mock_{i}",
        })

    return pd.DataFrame(students)


def generate_courses():
    """生成课程数据"""
    courses = [
        {
            'id': 1,
            'course_no': 'CS101',
            'name': '数据结构与算法',
            'description': '计算机专业核心课程，学习常用数据结构和算法设计',
            'credit': 4.0,
            'hours': 64,
            'teacher_id': 2,  # 教师ID
            'semester': '2024-2025-1',
            'chapters': json.dumps(['线性表', '栈与队列', '树与二叉树', '图', '查找', '排序', '算法设计', '综合应用']),
        },
        {
            'id': 2,
            'course_no': 'CS102',
            'name': '操作系统原理',
            'description': '计算机专业核心课程，学习操作系统基本概念和原理',
            'credit': 3.5,
            'hours': 56,
            'teacher_id': 2,
            'semester': '2024-2025-1',
            'chapters': json.dumps(['进程管理', '内存管理', '文件系统', 'I/O系统', '死锁', '虚拟化', '安全', '分布式']),
        },
        {
            'id': 3,
            'course_no': 'CS103',
            'name': '计算机网络',
            'description': '计算机专业核心课程，学习计算机网络体系结构和协议',
            'credit': 3.0,
            'hours': 48,
            'teacher_id': 3,
            'semester': '2024-2025-1',
            'chapters': json.dumps(['物理层', '数据链路层', '网络层', '传输层', '应用层', '网络安全', '无线网络', '网络管理']),
        },
        {
            'id': 4,
            'course_no': 'CS104',
            'name': '数据库原理',
            'description': '计算机专业核心课程，学习数据库设计和SQL语言',
            'credit': 3.5,
            'hours': 56,
            'teacher_id': 3,
            'semester': '2024-2025-1',
            'chapters': json.dumps(['关系模型', 'SQL语言', '数据库设计', '规范化', '事务管理', '并发控制', '恢复技术', '数据库安全']),
        },
    ]
    return pd.DataFrame(courses)


def generate_knowledge_points(courses_df):
    """生成知识点数据"""
    knowledge_points = []
    kp_id = 1

    for _, course in courses_df.iterrows():
        chapters = json.loads(course['chapters'])
        for idx, chapter in enumerate(chapters, 1):
            knowledge_points.append({
                'id': kp_id,
                'course_id': course['id'],
                'name': chapter,
                'chapter_no': f"第{idx}章",
                'description': f"{course['name']} - {chapter}",
                'weight': round(random.uniform(0.8, 1.2), 2),
            })
            kp_id += 1

    return pd.DataFrame(knowledge_points)


def generate_course_enrollments(students_df, courses_df):
    """生成选课关系数据"""
    enrollments = []

    # 每名学生随机选2-4门课程
    for _, student in students_df.iterrows():
        num_courses = random.randint(2, 4)
        selected_courses = random.sample(courses_df['id'].tolist(), num_courses)

        for course_id in selected_courses:
            enrollments.append({
                'id': len(enrollments) + 1,
                'student_id': student['id'],
                'course_id': course_id,
                'enroll_time': datetime(2024, 9, 1) + timedelta(days=random.randint(0, 30)),
                'status': 1,
            })

    return pd.DataFrame(enrollments)


def generate_users():
    """生成用户数据（教师、辅导员、管理员）"""
    users = [
        {
            'id': 1,
            'username': 'admin',
            'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  # password
            'name': '系统管理员',
            'role': 'admin',
            'email': 'admin@example.edu.cn',
            'phone': '13800138000',
            'is_active': 1,
        },
        {
            'id': 2,
            'username': 'teacher1',
            'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
            'name': '王老师',
            'role': 'teacher',
            'email': 'teacher1@example.edu.cn',
            'phone': '13800138001',
            'is_active': 1,
        },
        {
            'id': 3,
            'username': 'teacher2',
            'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
            'name': '李老师',
            'role': 'teacher',
            'email': 'teacher2@example.edu.cn',
            'phone': '13800138002',
            'is_active': 1,
        },
        {
            'id': 4,
            'username': 'counselor1',
            'password': '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
            'name': '张辅导员',
            'role': 'counselor',
            'email': 'counselor1@example.edu.cn',
            'phone': '13800138003',
            'is_active': 1,
        },
    ]
    return pd.DataFrame(users)


def generate_learning_activities(students_df, courses_df, enrollments_df):
    """生成学习活动数据（视频观看、签到等）"""
    activities = []

    for _, enrollment in enrollments_df.iterrows():
        student_id = enrollment['student_id']
        course_id = enrollment['course_id']

        # 每个选课学生生成20-40次活动记录
        num_activities = random.randint(20, 40)

        for _ in range(num_activities):
            activity_type = random.choice(['video', 'sign_in', 'discuss', 'quiz', 'other'])
            activity_name = {
                'video': random.choice(['课程视频', '课件视频', '录播回放']),
                'sign_in': random.choice(['课堂签到', '在线签到', '位置签到']),
                'discuss': random.choice(['讨论区发帖', '回复讨论', '点赞评论']),
                'quiz': random.choice(['随堂测试', '章节测试', '练习题']),
                'other': random.choice(['查看资料', '浏览公告', '访问作业']),
            }[activity_type]

            # 生成活动时间（学期内）
            start_time = datetime(2024, 9, 1) + timedelta(days=random.randint(0, 120))
            duration = random.randint(60, 3600) if activity_type == 'video' else random.randint(10, 300)
            progress = random.uniform(0.3, 1.0) if activity_type == 'video' else None

            activities.append({
                'id': len(activities) + 1,
                'student_id': student_id,
                'course_id': course_id,
                'activity_type': activity_type,
                'activity_name': activity_name,
                'chapter_id': random.randint(1, NUM_KNOWLEDGE_POINTS * NUM_COURSES),
                'start_time': start_time,
                'end_time': start_time + timedelta(seconds=duration),
                'duration': duration,
                'progress': progress,
                'score': None,
            })

    return pd.DataFrame(activities)


def generate_homework_assignments(courses_df):
    """生成作业任务数据"""
    assignments = []
    assignment_id = 1

    for _, course in courses_df.iterrows():
        # 每门课程8次作业
        for i in range(1, 9):
            assignments.append({
                'id': assignment_id,
                'course_id': course['id'],
                'title': f"第{i}次作业 - {course['name']}",
                'description': f"完成第{i}章相关练习题",
                'knowledge_point_id': (course['id'] - 1) * 8 + i,
                'full_score': 100.0,
                'start_time': datetime(2024, 9, 1) + timedelta(days=(i-1)*14),
                'deadline': datetime(2024, 9, 1) + timedelta(days=(i-1)*14 + 7),
            })
            assignment_id += 1

    return pd.DataFrame(assignments)


def generate_homework_submissions(students_df, assignments_df, enrollments_df):
    """生成作业提交数据"""
    submissions = []

    # 构建学生-课程映射
    student_courses = {}
    for _, enrollment in enrollments_df.iterrows():
        if enrollment['student_id'] not in student_courses:
            student_courses[enrollment['student_id']] = []
        student_courses[enrollment['student_id']].append(enrollment['course_id'])

    for _, assignment in assignments_df.iterrows():
        course_id = assignment['course_id']

        # 找到选这门课的所有学生
        for student_id, courses in student_courses.items():
            if course_id not in courses:
                continue

            # 80%概率提交作业
            if random.random() < 0.8:
                # 成绩分布：部分学生成绩低（用于预警）
                if random.random() < 0.15:  # 15%学生成绩较差
                    score = random.uniform(30, 70)
                elif random.random() < 0.3:  # 30%学生成绩中等
                    score = random.uniform(60, 85)
                else:  # 55%学生成绩良好
                    score = random.uniform(70, 100)

                submit_time = assignment['deadline'] - timedelta(days=random.randint(0, 5))
                is_late = submit_time > assignment['deadline']

                submissions.append({
                    'id': len(submissions) + 1,
                    'assignment_id': assignment['id'],
                    'student_id': student_id,
                    'score': round(score, 2),
                    'submit_time': submit_time,
                    'is_late': 1 if is_late else 0,
                    'correct_count': int(score / 100 * 10),
                    'total_count': 10,
                })

    return pd.DataFrame(submissions)


def generate_exam_assignments(courses_df):
    """生成考试任务数据"""
    exams = []

    for _, course in courses_df.iterrows():
        # 期中考试
        exams.append({
            'id': len(exams) + 1,
            'course_id': course['id'],
            'title': f"{course['name']} - 期中考试",
            'exam_type': 'midterm',
            'full_score': 100.0,
            'start_time': datetime(2024, 10, 15, 9, 0),
            'end_time': datetime(2024, 10, 15, 11, 0),
            'duration': 120,
        })
        # 期末考试
        exams.append({
            'id': len(exams) + 1,
            'course_id': course['id'],
            'title': f"{course['name']} - 期末考试",
            'exam_type': 'final',
            'full_score': 100.0,
            'start_time': datetime(2024, 12, 20, 9, 0),
            'end_time': datetime(2024, 12, 20, 11, 0),
            'duration': 120,
        })

    return pd.DataFrame(exams)


def generate_exam_results(students_df, exams_df, enrollments_df):
    """生成考试结果数据"""
    results = []

    # 构建学生-课程映射
    student_courses = {}
    for _, enrollment in enrollments_df.iterrows():
        if enrollment['student_id'] not in student_courses:
            student_courses[enrollment['student_id']] = []
        student_courses[enrollment['student_id']].append(enrollment['course_id'])

    for _, exam in exams_df.iterrows():
        course_id = exam['course_id']

        for student_id, courses in student_courses.items():
            if course_id not in courses:
                continue

            # 90%概率参加考试
            if random.random() < 0.9:
                # 成绩与作业类似，但有相关性
                if random.random() < 0.15:
                    score = random.uniform(25, 65)
                elif random.random() < 0.35:
                    score = random.uniform(55, 80)
                else:
                    score = random.uniform(70, 100)

                results.append({
                    'id': len(results) + 1,
                    'exam_id': exam['id'],
                    'student_id': student_id,
                    'score': round(score, 2),
                    'submit_time': exam['start_time'] + timedelta(minutes=random.randint(60, 110)),
                    'is_submitted': 1,
                    'correct_count': int(score / 100 * 20),
                    'total_count': 20,
                })

    return pd.DataFrame(results)


def generate_warning_records(students_df, courses_df):
    """生成预警记录数据（示例）"""
    warnings = []

    # 为部分学生生成预警记录
    for _, student in students_df.iterrows():
        # 20%学生有预警记录
        if random.random() < 0.2:
            course_id = random.choice(courses_df['id'].tolist())

            # 随机风险等级
            risk_level = random.choices(
                ['high', 'medium', 'low', 'normal'],
                weights=[0.2, 0.3, 0.3, 0.2]
            )[0]

            composite_score = {
                'high': random.uniform(30, 59),
                'medium': random.uniform(60, 74),
                'low': random.uniform(75, 84),
                'normal': random.uniform(85, 95),
            }[risk_level]

            warnings.append({
                'id': len(warnings) + 1,
                'student_id': student['id'],
                'course_id': course_id,
                'risk_level': risk_level,
                'composite_score': round(composite_score, 2),
                'attendance_score': round(random.uniform(20, 100), 2),
                'progress_score': round(random.uniform(20, 100), 2),
                'homework_score': round(random.uniform(20, 100), 2),
                'exam_score': round(random.uniform(20, 100), 2),
                'ai_analysis': f"{student['name']}同学学习状态需要关注。",
                'ai_suggestions': json.dumps(['建议约谈学生', '安排学习帮扶', '定期跟进']),
                'ai_source': 'template',
                'status': 'active',
            })

    return pd.DataFrame(warnings)


def main():
    """主函数"""
    print("="*60)
    print("模拟数据生成工具")
    print("="*60)

    # 1. 生成基础数据
    print("\n生成基础数据...")
    majors = generate_majors()
    classes = generate_classes(majors)
    students = generate_students(classes)
    courses = generate_courses()
    users = generate_users()
    knowledge_points = generate_knowledge_points(courses)

    # 2. 生成关系数据
    print("生成选课关系...")
    enrollments = generate_course_enrollments(students, courses)

    # 3. 生成学习数据
    print("生成学习活动数据...")
    activities = generate_learning_activities(students, courses, enrollments)

    print("生成作业数据...")
    assignments = generate_homework_assignments(courses)
    submissions = generate_homework_submissions(students, assignments, enrollments)

    print("生成考试数据...")
    exams = generate_exam_assignments(courses)
    results = generate_exam_results(students, exams, enrollments)

    # 4. 生成预警数据
    print("生成预警记录...")
    warnings = generate_warning_records(students, courses)

    # 5. 保存所有数据
    print("\n保存数据文件...")

    data_dict = {
        'majors': majors,
        'classes': classes,
        'students': students,
        'users': users,
        'courses': courses,
        'knowledge_points': knowledge_points,
        'course_enrollments': enrollments,
        'learning_activities': activities,
        'homework_assignments': assignments,
        'homework_submissions': submissions,
        'exam_assignments': exams,
        'exam_results': results,
        'warning_records': warnings,
    }

    for name, df in data_dict.items():
        output_path = MOCK_DIR / f"{name}.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"  {name}: {len(df)}条记录 -> {output_path}")

    # 6. 生成统计报告
    report = {
        "生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "专业数量": len(majors),
        "班级数量": len(classes),
        "学生数量": len(students),
        "教师/辅导员数量": len(users) - 1,  # 除去管理员
        "课程数量": len(courses),
        "知识点数量": len(knowledge_points),
        "选课记录": len(enrollments),
        "学习活动": len(activities),
        "作业任务": len(assignments),
        "作业提交": len(submissions),
        "考试任务": len(exams),
        "考试结果": len(results),
        "预警记录": len(warnings),
    }

    with open(MOCK_DIR / "mock_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "="*60)
    print("模拟数据生成完成！")
    print(f"数据保存在: {MOCK_DIR}")
    print("="*60)

    print("\n数据统计:")
    for key, value in report.items():
        if key != "生成时间":
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
