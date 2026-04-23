#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据架构重建脚本
- 删除teacher账号，保留teacher1/2/3
- 重建6门课程分配给3位教师
- 重建9个班级（3年级×3专业班）
- 重新分配354名学生，生成自解释学号
- 分配辅导员管理年级
- 重建选课关系
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from classes.models import Student, Class
from courses.models import Course, CourseEnrollment
from users.models import Teacher


def delete_teacher_account():
    """删除teacher测试账号"""
    print("=" * 60)
    print("步骤1: 删除teacher测试账号")
    print("=" * 60)

    try:
        teacher_user = User.objects.get(username='teacher')
        teacher_user.delete()
        print(f"[OK] 已删除用户: teacher")
    except User.DoesNotExist:
        print("[OK] teacher账号不存在，跳过")

    try:
        teacher = Teacher.objects.get(teacher_no='T2021001')
        teacher.delete()
        print(f"[OK] 已删除教师: T2021001")
    except Teacher.DoesNotExist:
        print("[OK] 教师T2021001不存在，跳过")

    print()


def rebuild_courses():
    """重建6门课程并分配给3位教师"""
    print("=" * 60)
    print("步骤2: 重建6门课程")
    print("=" * 60)

    # 获取3位教师
    teachers = Teacher.objects.filter(user__username__in=['teacher1', 'teacher2', 'teacher3']).order_by('user__username')
    if len(teachers) < 3:
        print("错误: 需要3位教师(teacher1/2/3)，当前只有", len(teachers))
        return None

    t1, t2, t3 = teachers[0], teachers[1], teachers[2]
    print(f"[OK] 获取教师: t1={t1.user.username}, t2={t2.user.username}, t3={t3.user.username}")

    # 删除现有课程
    Course.objects.all().delete()
    print("[OK] 已删除现有课程")

    # 创建6门新课程
    courses_data = [
        # (名称, 教师, 学期, 学分, 学时)
        ('数据结构', t1, '2024-2025-1', 3.0, 48),
        ('软件工程', t1, '2024-2025-1', 3.0, 48),
        ('操作系统', t2, '2024-2025-1', 3.0, 48),
        ('人工智能导论', t2, '2024-2025-1', 3.0, 48),
        ('计算机网络', t3, '2024-2025-1', 3.0, 48),
        ('数据库原理', t3, '2024-2025-1', 3.0, 48),
    ]

    courses = []
    for name, teacher, semester, credit, hours in courses_data:
        course = Course.objects.create(
            name=name,
            course_no=f"CS{len(courses)+1:03d}",
            description=f"{name}课程",
            credit=credit,
            hours=hours,
            teacher_id=teacher.id,
            semester=semester,
            status=1,
            chapters=[]
        )
        courses.append(course)
        print(f"[OK] 创建课程: {name} (教师: {teacher.user.username})")

    print(f"\n总计创建 {len(courses)} 门课程")
    return courses


def rebuild_classes():
    """重建9个班级"""
    print("=" * 60)
    print("步骤3: 重建9个班级")
    print("=" * 60)

    # 删除现有班级
    Class.objects.all().delete()
    print("[OK] 已删除现有班级")

    # 年级配置
    grades = [
        ('2019', '大四'),
        ('2020', '大三'),
        ('2021', '大二'),
    ]

    # 专业配置
    majors = [
        ('软件工程', 1),
        ('计算机科学', 2),
    ]

    classes = []
    class_id = 1

    for grade_code, grade_name in grades:
        for major_name, major_code in majors:
            # 软件工程2个班，计算机科学1个班
            num_classes = 2 if major_code == 1 else 1

            for i in range(1, num_classes + 1):
                class_name = f"{grade_code}级{major_name}{i}班"
                cls = Class.objects.create(
                    id=class_id,
                    name=class_name,
                    grade=grade_code,
                    major_id=major_code,
                    counselor_id=None,  # 稍后分配
                    student_count=0,
                    raw_id=f"CLS{class_id:04d}"
                )
                classes.append({
                    'obj': cls,
                    'grade': grade_code,
                    'major': major_code,
                    'major_name': major_name,
                    'seq': i
                })
                print(f"[OK] 创建班级: {class_name} (ID: {class_id})")
                class_id += 1

    print(f"\n总计创建 {len(classes)} 个班级")
    return classes


def assign_counselors_to_grades():
    """分配辅导员管理年级"""
    print("=" * 60)
    print("步骤4: 分配辅导员管理年级")
    print("=" * 60)

    # 辅导员-年级对应关系
    counselor_grade_map = {
        'counselor': '2019',
        'counselor2': '2020',
        'counselor3': '2021',
    }

    # 获取辅导员用户ID
    for username, grade in counselor_grade_map.items():
        try:
            user = User.objects.get(username=username)
            # 更新该年级所有班级的counselor_id
            Class.objects.filter(grade=grade).update(counselor_id=user.id)
            count = Class.objects.filter(grade=grade).count()
            print(f"[OK] {username} (ID: {user.id}) 管理 {grade}级 {count}个班级")
        except User.DoesNotExist:
            print(f"[ERROR] 辅导员 {username} 不存在")

    print()


def rebuild_students():
    """重建学生数据，分配班级，生成新学号"""
    print("=" * 60)
    print("步骤5: 重建学生数据")
    print("=" * 60)

    # 获取所有学生，排除测试账号
    students = Student.objects.exclude(
        student_no__in=['student', 'student_1', 'teststudent']
    ).order_by('id')

    total = students.count()
    print(f"[OK] 共有 {total} 名学生需要重新分配")

    # 目标分布
    # 2019级: 119人 (软件工程80人=2班，计算机科学39人=1班)
    # 2020级: 118人 (软件工程78人=2班，计算机科学40人=1班)
    # 2021级: 117人 (软件工程78人=2班，计算机科学39人=1班)

    distribution = {
        '2019': {'软件工程': [40, 40], '计算机科学': [39]},  # 合计119
        '2020': {'软件工程': [39, 39], '计算机科学': [40]},  # 合计118
        '2021': {'软件工程': [39, 39], '计算机科学': [39]},  # 合计117
    }

    # 准备班级映射
    class_map = {}
    for grade in ['2019', '2020', '2021']:
        class_map[grade] = {}
        for major in ['软件工程', '计算机科学']:
            class_map[grade][major] = list(Class.objects.filter(
                grade=grade,
                name__contains=major
            ).order_by('id'))

    # 重新分配学生
    student_iter = iter(students)
    seq_counters = {}  # 记录每个班级的序号

    for grade in ['2019', '2020', '2021']:
        for major_name, class_sizes in distribution[grade].items():
            classes = class_map[grade][major_name]
            major_code = 1 if major_name == '软件工程' else 2

            for i, class_size in enumerate(class_sizes):
                cls = classes[i]
                class_seq = i + 1

                # 分配学生到该班级
                for j in range(class_size):
                    try:
                        student = next(student_iter)
                    except StopIteration:
                        break

                    # 生成新学号: 年级4位 + 专业1位 + 班级1位 + 序号2位
                    seq_key = f"{grade}{major_code}{class_seq}"
                    if seq_key not in seq_counters:
                        seq_counters[seq_key] = 0
                    seq_counters[seq_key] += 1
                    seq_num = seq_counters[seq_key]

                    new_student_no = f"{grade}{major_code}{class_seq}{seq_num:02d}"

                    # 更新学生信息
                    student.student_no = new_student_no
                    student.class_id = cls.id
                    student.major_id = major_code
                    student.enrollment_year = int(grade)
                    student.save()

                    if seq_num <= 2 or seq_num == class_size:
                        print(f"  {student.name} -> {new_student_no} ({cls.name})")

    # 更新班级人数
    for cls in Class.objects.all():
        count = Student.objects.filter(class_id=cls.id).count()
        cls.student_count = count
        cls.save()
        print(f"[OK] {cls.name}: {count}人")

    print(f"\n[OK] 学生重新分配完成")
    print()


def rebuild_course_enrollments(courses):
    """重建选课关系"""
    print("=" * 60)
    print("步骤6: 重建选课关系")
    print("=" * 60)

    # 删除现有选课记录
    CourseEnrollment.objects.all().delete()
    print("[OK] 已删除现有选课记录")

    # 课程分配规则
    # 2021级: 数据结构 + 计算机网络
    # 2020级: 操作系统 + 数据库原理
    # 2019级: 软件工程 + 人工智能导论

    course_map = {c.name: c for c in courses}

    grade_courses = {
        '2021': [course_map['数据结构'], course_map['计算机网络']],
        '2020': [course_map['操作系统'], course_map['数据库原理']],
        '2019': [course_map['软件工程'], course_map['人工智能导论']],
    }

    total_enrollments = 0

    for grade, courses_list in grade_courses.items():
        students = Student.objects.filter(enrollment_year=int(grade))
        grade_count = 0

        for student in students:
            for course in courses_list:
                CourseEnrollment.objects.create(
                    student_id=student.id,
                    course_id=course.id,
                    status=1
                )
                grade_count += 1

        print(f"[OK] {grade}级 {students.count()}名学生 选修 {len(courses_list)}门课 = {grade_count}条记录")
        total_enrollments += grade_count

    print(f"\n总计创建 {total_enrollments} 条选课记录")
    print()


def print_summary():
    """打印数据摘要"""
    print("=" * 60)
    print("数据重建完成摘要")
    print("=" * 60)

    print("\n【教师】")
    for t in Teacher.objects.all():
        print(f"  {t.user.username}: {t.teacher_no}")

    print("\n【课程】")
    for c in Course.objects.all():
        teacher_name = Teacher.objects.get(id=c.teacher_id).user.username if c.teacher_id else '未分配'
        print(f"  {c.name} (教师: {teacher_name})")

    print("\n【辅导员-年级】")
    counselor_map = {
        'counselor': '2019',
        'counselor2': '2020',
        'counselor3': '2021',
    }
    for username, grade in counselor_map.items():
        count = Class.objects.filter(grade=grade).count()
        print(f"  {username}: {grade}级 ({count}个班级)")

    print("\n【班级分布】")
    for grade in ['2019', '2020', '2021']:
        classes = Class.objects.filter(grade=grade)
        total = sum(c.student_count for c in classes)
        print(f"  {grade}级: {classes.count()}个班, {total}人")
        for cls in classes:
            print(f"    - {cls.name}: {cls.student_count}人")

    print("\n【选课统计】")
    for grade in ['2019', '2020', '2021']:
        students = Student.objects.filter(enrollment_year=int(grade))
        enrollments = CourseEnrollment.objects.filter(student_id__in=students.values_list('id', flat=True))
        print(f"  {grade}级: {students.count()}人, {enrollments.count()}条选课记录")

    print("\n" + "=" * 60)
    print("[OK] 数据架构重建完成！")
    print("=" * 60)


def main():
    print("\n" + "=" * 60)
    print("学业预警系统 - 数据架构重建")
    print("=" * 60 + "\n")

    try:
        with transaction.atomic():
            # 步骤1: 删除teacher账号
            delete_teacher_account()

            # 步骤2: 重建课程
            courses = rebuild_courses()
            if not courses:
                raise Exception("课程重建失败")

            # 步骤3: 重建班级
            classes = rebuild_classes()
            if not classes:
                raise Exception("班级重建失败")

            # 步骤4: 分配辅导员
            assign_counselors_to_grades()

            # 步骤5: 重建学生
            rebuild_students()

            # 步骤6: 重建选课
            rebuild_course_enrollments(courses)

            # 打印摘要
            print_summary()

    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
