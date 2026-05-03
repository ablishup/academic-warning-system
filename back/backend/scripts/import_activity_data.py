#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习活动数据导入脚本
将 CSV 数据导入到 MySQL 的 learning_activities 表
"""

import os
import sys
import csv
from datetime import datetime

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
django.setup()

from classes.models import Student
from learning.models import LearningActivity


# CSV 文件路径
# 脚本位于 back/backend/scripts/，CSV 位于 project/data/cleaned/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
CSV_PATH = os.path.join(PROJECT_ROOT, 'data', 'cleaned', 'cleaned_activity_logs.csv')

# 年级-课程映射
GRADE_COURSE_MAP = {
    2019: [5, 7],  # 软件工程, 人工智能导论
    2020: [4, 6],  # 数据结构, 操作系统
    2021: [8, 9],  # 计算机网络, 数据库原理
}


def parse_datetime(value):
    """解析日期时间字符串"""
    if not value:
        return None
    value = value.strip()
    # 尝试多种格式
    for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
        try:
            dt = datetime.strptime(value, fmt)
            # 如果只有日期，补全时间为 00:00:00
            return dt
        except ValueError:
            continue
    return None


def main():
    print("\n" + "=" * 60)
    print("学习活动数据导入脚本")
    print("=" * 60)

    # 1. 检查 CSV 文件
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] CSV 文件不存在: {CSV_PATH}")
        return 1

    # 2. 获取学生映射（CSV ID → MySQL Student 对象）
    print("\n[INFO] 获取学生映射...")
    students = Student.objects.exclude(
        student_no__in=['student', 'student_1', 'teststudent']
    ).order_by('id')

    student_map = {}  # CSV ID → Student 对象
    for idx, student in enumerate(students, start=1):
        student_map[idx] = student

    print(f"[OK] 共映射 {len(student_map)} 名学生")
    if student_map:
        first_id = student_map[1].id
        last_id = student_map[len(student_map)].id
        print(f"    CSV ID 1 → MySQL ID {first_id}")
        print(f"    CSV ID {len(student_map)} → MySQL ID {last_id}")

    # 3. 读取 CSV 并导入
    print(f"\n[INFO] 读取 CSV 文件: {CSV_PATH}")
    activities = []
    skipped = 0
    error_rows = []

    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        row_count = 0

        for row in reader:
            row_count += 1
            csv_student_id = int(row['student_id'])
            student = student_map.get(csv_student_id)

            if not student:
                skipped += 1
                continue

            # 获取该学生年级对应的两门课程
            course_ids = GRADE_COURSE_MAP.get(student.enrollment_year, [])
            if not course_ids:
                skipped += 1
                error_rows.append(f"Row {row_count}: student {csv_student_id} has no grade mapping")
                continue

            # 解析时间
            start_time = parse_datetime(row['start_time'])
            end_time = parse_datetime(row['end_time'])

            # 解析进度（CSV 0-1 → MySQL 百分比）
            progress = None
            if row['progress'] and row['progress'].strip():
                try:
                    progress = float(row['progress']) * 100
                except ValueError:
                    pass

            # 解析时长
            duration = None
            if row['duration'] and row['duration'].strip():
                try:
                    duration = int(row['duration'])
                except ValueError:
                    pass

            # 为每门课程创建活动记录
            for course_id in course_ids:
                activity = LearningActivity(
                    student_id=student.id,
                    course_id=course_id,
                    activity_type=row['activity_type'],
                    activity_name=row['activity_name'],
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    progress=progress,
                )
                activities.append(activity)

            # 每 1000 条记录批量创建
            if len(activities) >= 2000:
                LearningActivity.objects.bulk_create(activities, batch_size=1000)
                print(f"  已导入 {len(activities)} 条记录...")
                activities = []

    # 导入剩余记录
    if activities:
        LearningActivity.objects.bulk_create(activities, batch_size=1000)

    total_created = row_count * 2 - skipped * 2  # 每条 CSV 记录生成两条 MySQL 记录

    # 4. 打印结果
    print(f"\n[OK] 导入完成")
    print(f"  CSV 记录数: {row_count}")
    print(f"  跳过记录数: {skipped}")
    print(f"  预期 MySQL 记录数: {total_created}")

    # 5. 验证导入结果
    print("\n[INFO] 验证导入结果...")
    from django.db.models import Count

    total = LearningActivity.objects.count()
    print(f"  MySQL 实际记录数: {total}")

    # 按课程统计
    course_stats = LearningActivity.objects.values('course_id').annotate(
        count=Count('id')
    ).order_by('course_id')
    print("\n  按课程统计:")
    for stat in course_stats:
        print(f"    course_id={stat['course_id']}: {stat['count']} 条")

    # 按活动类型统计
    type_stats = LearningActivity.objects.values('activity_type').annotate(
        count=Count('id')
    ).order_by('activity_type')
    print("\n  按活动类型统计:")
    for stat in type_stats:
        print(f"    {stat['activity_type']}: {stat['count']} 条")

    if error_rows:
        print(f"\n[WARN] 有 {len(error_rows)} 行数据有问题:")
        for err in error_rows[:10]:
            print(f"  {err}")
        if len(error_rows) > 10:
            print(f"  ... 还有 {len(error_rows) - 10} 行")

    print("\n" + "=" * 60)
    print("[OK] 学习活动数据导入完成！")
    print("=" * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
