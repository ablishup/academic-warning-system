#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超星公网数据清洗脚本
功能：
1. 读取原始xls/xlsx文件
2. 筛选2-3门完整课程
3. 去除测试账号和重复数据
4. 字段映射和类型转换
5. 保存清洗后的数据到cleaned目录

使用方法：
    python clean_data.py
"""

import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
import json

# 配置路径
BASE_DIR = Path(__file__).parent.parent  # data目录
RAW_DATA_DIR = BASE_DIR / "raw"  # 原始数据目录
CLEANED_DIR = BASE_DIR / "cleaned"  # 清洗后数据目录
CLEANED_DIR.mkdir(exist_ok=True)
CLEANED_DIR.mkdir(exist_ok=True)

# 筛选配置
MIN_STUDENTS_PER_COURSE = 50   # 每门课程最少学生数
MAX_STUDENTS_PER_COURSE = 200  # 每门课程最多学生数
TARGET_COURSES = 3             # 目标课程数量


def is_test_account(username, name):
    """判断是否为测试账号"""
    if pd.isna(username) and pd.isna(name):
        return True

    test_patterns = [
        r'test', r'admin', r'测试', r'教师', r'teacher',
        r'^[0-9]{4}$',  # 纯4位数字（可能是测试编号）
    ]

    check_str = f"{username} {name}".lower()
    for pattern in test_patterns:
        if re.search(pattern, check_str):
            return True
    return False


def clean_person_data():
    """清洗学生信息表"""
    print("正在清洗学生信息表...")

    df = pd.read_excel(RAW_DATA_DIR / "t_stat_person.xls")
    print(f"原始记录数: {len(df)}")

    # 去除测试账号
    df = df[~df.apply(lambda x: is_test_account(x.get('user_name'), x.get('name')), axis=1)]

    # 去除重复（根据学号）
    df = df.drop_duplicates(subset=['user_name'], keep='first')

    # 去除关键字段为空的记录
    df = df.dropna(subset=['user_name', 'name'])

    # 字段重命名（映射到项目字段）
    column_mapping = {
        'user_id': 'original_id',
        'user_name': 'student_id',  # 学号
        'name': 'name',
        'clazz_id': 'class_id',
        'school_id': 'school_id',
        'major_id': 'major_id',
        'sex': 'gender',
        'phone': 'phone',
        'email': 'email',
    }
    df = df.rename(columns=column_mapping)

    # 选择需要的字段
    needed_columns = ['original_id', 'student_id', 'name', 'class_id', 'gender', 'phone', 'email']
    existing_columns = [c for c in needed_columns if c in df.columns]
    df = df[existing_columns]

    # 保存
    output_path = CLEANED_DIR / "cleaned_persons.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_course_data():
    """清洗课程信息表，筛选目标课程"""
    print("\n正在清洗课程信息表...")

    df = pd.read_excel(RAW_DATA_DIR / "t_stat_course.xls")
    print(f"原始课程数: {len(df)}")

    # 读取选课关系，统计每门课程的学生数
    course_person = pd.read_excel(RAW_DATA_DIR / "t_stat_course_person.xls")
    course_student_count = course_person.groupby('course_id').size()

    # 筛选符合人数要求的课程
    valid_courses = course_student_count[
        (course_student_count >= MIN_STUDENTS_PER_COURSE) &
        (course_student_count <= MAX_STUDENTS_PER_COURSE)
    ].index.tolist()

    print(f"符合人数要求的课程数: {len(valid_courses)}")

    # 选择学生数最多的前几门课程
    selected_courses = course_student_count[valid_courses].nlargest(TARGET_COURSES).index.tolist()
    print(f"已选择 {len(selected_courses)} 门课程: {selected_courses}")

    # 保存课程选择结果
    with open(CLEANED_DIR / "selected_courses.json", "w", encoding="utf-8") as f:
        json.dump({
            "course_ids": selected_courses,
            "student_counts": course_student_count[selected_courses].to_dict()
        }, f, ensure_ascii=False, indent=2)

    # 筛选课程数据
    df = df[df['course_id'].isin(selected_courses)]

    # 字段重命名
    column_mapping = {
        'course_id': 'original_id',
        'course_name': 'name',
        'teacher_name': 'teacher_name',
        'create_time': 'created_at',
        'course_desc': 'description',
        'chapters': 'chapters',  # 章节信息，用于知识点
    }
    df = df.rename(columns=column_mapping)

    # 保存
    output_path = CLEANED_DIR / "cleaned_courses.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后课程数: {len(df)}, 已保存到 {output_path}")

    return df, selected_courses


def clean_clazz_data():
    """清洗班级信息表"""
    print("\n正在清洗班级信息表...")

    df = pd.read_excel(RAW_DATA_DIR / "t_stat_clazz.xls")
    print(f"原始班级数: {len(df)}")

    # 读取学生数据，获取相关班级ID
    persons = pd.read_csv(CLEANED_DIR / "cleaned_persons.csv", encoding='utf-8-sig')
    related_class_ids = persons['class_id'].dropna().unique()

    # 筛选相关班级
    df = df[df['clazz_id'].isin(related_class_ids)]

    # 字段重命名
    column_mapping = {
        'clazz_id': 'original_id',
        'clazz_name': 'name',
        'grade': 'grade',
        'major_id': 'major_id',
        'school_id': 'school_id',
    }
    df = df.rename(columns=column_mapping)

    # 保存
    output_path = CLEANED_DIR / "cleaned_classes.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后班级数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_course_person_data(selected_course_ids):
    """清洗选课关系表"""
    print("\n正在清洗选课关系表...")

    df = pd.read_excel(RAW_DATA_DIR / "t_stat_course_person.xls")
    print(f"原始选课记录数: {len(df)}")

    # 读取已清洗的学生数据
    persons = pd.read_csv(CLEANED_DIR / "cleaned_persons.csv", encoding='utf-8-sig')
    valid_student_ids = persons['original_id'].unique()

    # 筛选：只保留已选课程和已清洗学生
    df = df[
        (df['course_id'].isin(selected_course_ids)) &
        (df['user_id'].isin(valid_student_ids))
    ]

    # 去除重复
    df = df.drop_duplicates(subset=['course_id', 'user_id'], keep='first')

    # 保存
    output_path = CLEANED_DIR / "cleaned_course_persons.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后选课记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_activity_log_data(selected_course_ids):
    """清洗活动日志表（用于出勤率计算）"""
    print("\n正在清洗活动日志表...")

    # 分批读取大文件
    chunks = []
    chunk_size = 50000

    for chunk in pd.read_excel(RAW_DATA_DIR / "t_stat_activity_log.xls", chunksize=chunk_size):
        # 筛选已选课程
        filtered = chunk[chunk['course_id'].isin(selected_course_ids)]
        if len(filtered) > 0:
            chunks.append(filtered)

    if chunks:
        df = pd.concat(chunks, ignore_index=True)
    else:
        df = pd.DataFrame()

    print(f"清洗后活动记录数: {len(df)}")

    # 字段重命名
    column_mapping = {
        'log_id': 'original_id',
        'user_id': 'student_original_id',
        'course_id': 'course_original_id',
        'activity_type': 'activity_type',
        'create_time': 'created_at',
        'duration': 'duration',
    }
    df = df.rename(columns=column_mapping)

    # 保存
    output_path = CLEANED_DIR / "cleaned_activity_logs.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"已保存到 {output_path}")

    return df


def clean_work_answer_data(selected_course_ids):
    """清洗作业答案表"""
    print("\n正在清洗作业答案表...")

    # 分批读取
    chunks = []
    chunk_size = 50000

    for chunk in pd.read_excel(RAW_DATA_DIR / "t_stat_work_answer.xls", chunksize=chunk_size):
        filtered = chunk[chunk['course_id'].isin(selected_course_ids)]
        if len(filtered) > 0:
            chunks.append(filtered)

    if chunks:
        df = pd.concat(chunks, ignore_index=True)
    else:
        df = pd.DataFrame()

    print(f"清洗后作业答案记录数: {len(df)}")

    # 保存
    output_path = CLEANED_DIR / "cleaned_work_answers.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"已保存到 {output_path}")

    return df


def clean_exam_answer_data(selected_course_ids):
    """清洗考试答案表"""
    print("\n正在清洗考试答案表...")

    df = pd.read_excel(RAW_DATA_DIR / "t_stat_exam_answer.xls")
    print(f"原始考试答案记录数: {len(df)}")

    # 筛选已选课程
    df = df[df['course_id'].isin(selected_course_ids)]

    print(f"清洗后考试答案记录数: {len(df)}")

    # 保存
    output_path = CLEANED_DIR / "cleaned_exam_answers.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"已保存到 {output_path}")

    return df


def clean_student_score_data(selected_course_ids):
    """清洗学生成绩表"""
    print("\n正在清洗学生成绩表...")

    df = pd.read_excel(RAW_DATA_DIR / "t_stat_student_score.xls")
    print(f"原始成绩记录数: {len(df)}")

    # 筛选已选课程
    df = df[df['course_id'].isin(selected_course_ids)]

    print(f"清洗后成绩记录数: {len(df)}")

    # 保存
    output_path = CLEANED_DIR / "cleaned_student_scores.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"已保存到 {output_path}")

    return df


def extract_knowledge_points():
    """
    从课程信息中提取知识点（简化方案：以章节作为知识点）
    """
    print("\n正在提取知识点（基于课程章节）...")

    courses = pd.read_csv(CLEANED_DIR / "cleaned_courses.csv", encoding='utf-8-sig')

    knowledge_points = []
    kp_id = 1

    for _, course in courses.iterrows():
        course_id = course['original_id']
        course_name = course.get('name', '')

        # 从chapters字段解析章节（如果存在）
        chapters_str = course.get('chapters', '')
        if pd.notna(chapters_str) and chapters_str:
            # 假设章节以某种分隔符分隔
            chapters = str(chapters_str).split(',') if ',' in str(chapters_str) else [str(chapters_str)]
        else:
            # 如果没有章节信息，创建默认章节
            chapters = [f"第{i}章" for i in range(1, 9)]  # 默认8章

        for idx, chapter in enumerate(chapters, 1):
            knowledge_points.append({
                'original_id': kp_id,
                'course_original_id': course_id,
                'name': chapter.strip() if isinstance(chapter, str) else f"第{idx}章",
                'description': f"{course_name} - {chapter}" if isinstance(chapter, str) else f"{course_name} 第{idx}章",
                'chapter_order': idx,
            })
            kp_id += 1

    df = pd.DataFrame(knowledge_points)
    output_path = CLEANED_DIR / "cleaned_knowledge_points.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"提取知识点数量: {len(df)}, 已保存到 {output_path}")

    return df


def main():
    """主函数"""
    print("="*60)
    print("超星公网数据清洗工具")
    print("="*60)

    # 1. 清洗学生信息
    persons = clean_person_data()

    # 2. 清洗课程信息（并获取选中的课程ID）
    courses, selected_course_ids = clean_course_data()

    # 3. 清洗班级信息
    classes = clean_clazz_data()

    # 4. 清洗选课关系
    course_persons = clean_course_person_data(selected_course_ids)

    # 5. 清洗活动日志（出勤数据）
    activity_logs = clean_activity_log_data(selected_course_ids)

    # 6. 清洗作业答案
    work_answers = clean_work_answer_data(selected_course_ids)

    # 7. 清洗考试答案
    exam_answers = clean_exam_answer_data(selected_course_ids)

    # 8. 清洗成绩数据
    scores = clean_student_score_data(selected_course_ids)

    # 9. 提取知识点（简化方案）
    knowledge_points = extract_knowledge_points()

    print("\n" + "="*60)
    print("数据清洗完成！")
    print(f"清洗后文件保存在: {CLEANED_DIR}")
    print("="*60)

    # 生成统计报告
    report = {
        "学生数量": len(persons),
        "课程数量": len(courses),
        "班级数量": len(classes),
        "选课记录": len(course_persons),
        "活动记录": len(activity_logs),
        "作业答案": len(work_answers),
        "考试答案": len(exam_answers),
        "成绩记录": len(scores),
        "知识点数量": len(knowledge_points),
    }

    with open(CLEANED_DIR / "cleaning_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n数据统计:")
    for key, value in report.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
