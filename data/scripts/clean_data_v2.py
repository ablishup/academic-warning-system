#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超星公网数据清洗脚本 V2
适配实际数据结构
"""

import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
import json

# 配置路径
BASE_DIR = Path(__file__).parent.parent
RAW_DATA_DIR = BASE_DIR / "raw"
CLEANED_DIR = BASE_DIR / "cleaned"
CLEANED_DIR.mkdir(exist_ok=True)

# 筛选配置
MIN_STUDENTS_PER_COURSE = 50
MAX_STUDENTS_PER_COURSE = 200
TARGET_COURSES = 3


def is_test_account(username):
    """判断是否为测试账号"""
    if pd.isna(username):
        return True
    test_patterns = [r'test', r'admin', r'测试', r'教师', r'teacher']
    check_str = str(username).lower()
    for pattern in test_patterns:
        if re.search(pattern, check_str):
            return True
    return False


def read_excel_safe(filename, **kwargs):
    """安全读取Excel文件"""
    filepath = RAW_DATA_DIR / filename
    try:
        # 尝试用xlrd读取
        return pd.read_excel(filepath, engine='xlrd', **kwargs)
    except Exception as e1:
        try:
            # 尝试用openpyxl读取
            return pd.read_excel(filepath, engine='openpyxl', **kwargs)
        except Exception as e2:
            print(f"警告: 无法读取 {filename}: {e1}, {e2}")
            return None


def clean_person_data():
    """清洗学生信息表"""
    print("正在清洗学生信息表...")

    df = read_excel_safe("t_stat_person.xls")
    if df is None:
        print("无法读取学生信息，跳过")
        return pd.DataFrame()

    print(f"原始记录数: {len(df)}")
    print(f"列名: {list(df.columns)}")

    # 去除测试账号
    df = df[~df['user_name'].apply(is_test_account)]

    # 去除重复
    df = df.drop_duplicates(subset=['user_name'], keep='first')

    # 去除关键字段为空的记录
    df = df.dropna(subset=['user_name'])

    # 字段重命名
    # 注意：user_name是姓名，login_name是学号
    column_mapping = {
        'id': 'original_id',
        'personid': 'personid',
        'user_name': 'name',        # 姓名
        'login_name': 'student_no', # 学号
        'role': 'role',
        'fid': 'fid',
    }
    df = df.rename(columns=column_mapping)

    # 选择需要的字段
    needed_columns = ['original_id', 'personid', 'student_no', 'name', 'role', 'fid']
    existing_columns = [c for c in needed_columns if c in df.columns]
    df = df[existing_columns]

    # 保存
    output_path = CLEANED_DIR / "cleaned_persons.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_course_data():
    """清洗课程信息表"""
    print("\n正在清洗课程信息表...")

    df = read_excel_safe("t_stat_course.xls")
    if df is None:
        print("无法读取课程信息，跳过")
        return pd.DataFrame(), []

    print(f"原始课程数: {len(df)}")
    print(f"列名: {list(df.columns)}")

    # 读取选课关系
    course_person = read_excel_safe("t_stat_course_person.xls")
    if course_person is None:
        print("无法读取选课关系，使用所有课程")
        selected_courses = df['id'].tolist() if 'id' in df.columns else df.iloc[:TARGET_COURSES, 0].tolist()
    else:
        # 统计每门课程的学生数
        course_id_col = 'course_id' if 'course_id' in course_person.columns else course_person.columns[0]
        course_student_count = course_person.groupby(course_id_col).size()

        # 筛选符合人数要求的课程
        valid_courses = course_student_count[
            (course_student_count >= MIN_STUDENTS_PER_COURSE) &
            (course_student_count <= MAX_STUDENTS_PER_COURSE)
        ].index.tolist()

        print(f"符合人数要求的课程数: {len(valid_courses)}")

        # 选择学生数最多的前几门课程
        if len(valid_courses) > 0:
            selected_courses = course_student_count[valid_courses].nlargest(min(TARGET_COURSES, len(valid_courses))).index.tolist()
        else:
            selected_courses = course_student_count.nlargest(TARGET_COURSES).index.tolist()

    print(f"已选择 {len(selected_courses)} 门课程: {selected_courses}")

    # 保存课程选择结果
    with open(CLEANED_DIR / "selected_courses.json", "w", encoding="utf-8") as f:
        json.dump({
            "course_ids": selected_courses,
            "course_count": len(selected_courses)
        }, f, ensure_ascii=False, indent=2)

    # 课程ID列名
    course_id_col = 'id' if 'id' in df.columns else df.columns[0]

    # 筛选课程数据
    df = df[df[course_id_col].isin(selected_courses)]

    # 字段重命名
    column_mapping = {
        'id': 'original_id',
        'course_id': 'original_id',
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

    df = read_excel_safe("t_stat_clazz.xls")
    if df is None:
        print("无法读取班级信息，创建空文件")
        df = pd.DataFrame(columns=['original_id', 'name'])
    else:
        print(f"原始班级数: {len(df)}")
        print(f"列名: {list(df.columns)}")

        # 字段重命名
        clazz_id_col = 'id' if 'id' in df.columns else 'clazz_id' if 'clazz_id' in df.columns else df.columns[0]
        clazz_name_col = 'clazz_name' if 'clazz_name' in df.columns else 'name' if 'name' in df.columns else df.columns[1]

        df = df.rename(columns={
            clazz_id_col: 'original_id',
            clazz_name_col: 'name'
        })

    # 保存
    output_path = CLEANED_DIR / "cleaned_classes.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后班级数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_course_person_data(selected_course_ids):
    """清洗选课关系表"""
    print("\n正在清洗选课关系表...")

    df = read_excel_safe("t_stat_course_person.xls")
    if df is None:
        print("无法读取选课关系，创建空文件")
        df = pd.DataFrame()
    else:
        print(f"原始选课记录数: {len(df)}")
        print(f"列名: {list(df.columns)}")

        # 列名
        course_id_col = 'course_id' if 'course_id' in df.columns else df.columns[0]

        # 筛选已选课程
        df = df[df[course_id_col].isin(selected_course_ids)]

        # 去除重复
        user_id_col = 'user_id' if 'user_id' in df.columns else df.columns[1] if len(df.columns) > 1 else None
        if user_id_col:
            df = df.drop_duplicates(subset=[course_id_col, user_id_col], keep='first')

    # 保存
    output_path = CLEANED_DIR / "cleaned_course_persons.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后选课记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_activity_log_data(selected_course_ids):
    """清洗活动日志表"""
    print("\n正在清洗活动日志表...")

    df = read_excel_safe("t_stat_activity_log.xls")
    if df is None:
        print("无法读取活动日志，创建空文件")
        df = pd.DataFrame()
    else:
        print(f"原始活动记录数: {len(df)}")

        # 筛选已选课程
        course_id_col = 'course_id' if 'course_id' in df.columns else df.columns[0]
        df = df[df[course_id_col].isin(selected_course_ids)]

    # 保存
    output_path = CLEANED_DIR / "cleaned_activity_logs.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后活动记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_work_answer_data(selected_course_ids):
    """清洗作业答案表"""
    print("\n正在清洗作业答案表...")

    df = read_excel_safe("t_stat_work_answer.xls")
    if df is None:
        print("无法读取作业答案，创建空文件")
        df = pd.DataFrame()
    else:
        print(f"原始作业答案记录数: {len(df)}")

        # 筛选已选课程
        course_id_col = 'course_id' if 'course_id' in df.columns else df.columns[0]
        df = df[df[course_id_col].isin(selected_course_ids)]

    # 保存
    output_path = CLEANED_DIR / "cleaned_work_answers.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后作业答案记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_exam_answer_data(selected_course_ids):
    """清洗考试答案表"""
    print("\n正在清洗考试答案表...")

    df = read_excel_safe("t_stat_exam_answer.xls")
    if df is None:
        print("无法读取考试答案，创建空文件")
        df = pd.DataFrame()
    else:
        print(f"原始考试答案记录数: {len(df)}")

        # 筛选已选课程
        course_id_col = 'course_id' if 'course_id' in df.columns else df.columns[0]
        df = df[df[course_id_col].isin(selected_course_ids)]

    # 保存
    output_path = CLEANED_DIR / "cleaned_exam_answers.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后考试答案记录数: {len(df)}, 已保存到 {output_path}")

    return df


def clean_student_score_data(selected_course_ids):
    """清洗学生成绩表"""
    print("\n正在清洗学生成绩表...")

    df = read_excel_safe("t_stat_student_score.xls")
    if df is None:
        print("无法读取成绩数据，创建空文件")
        df = pd.DataFrame()
    else:
        print(f"原始成绩记录数: {len(df)}")

        # 筛选已选课程
        course_id_col = 'course_id' if 'course_id' in df.columns else df.columns[0]
        df = df[df[course_id_col].isin(selected_course_ids)]

    # 保存
    output_path = CLEANED_DIR / "cleaned_student_scores.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"清洗后成绩记录数: {len(df)}, 已保存到 {output_path}")

    return df


def extract_knowledge_points():
    """提取知识点（简化方案：创建默认章节）"""
    print("\n正在提取知识点（创建默认章节）...")

    courses = read_excel_safe("t_stat_course.xls")
    if courses is None:
        print("无法读取课程信息，创建空知识点文件")
        return pd.DataFrame()

    knowledge_points = []
    kp_id = 1

    course_id_col = 'id' if 'id' in courses.columns else courses.columns[0]
    course_name_col = 'course_name' if 'course_name' in courses.columns else 'name' if 'name' in courses.columns else None

    for _, course in courses.iterrows():
        course_id = course[course_id_col]
        course_name = course.get(course_name_col, f"课程{course_id}") if course_name_col else f"课程{course_id}"

        # 创建默认8个章节
        for idx in range(1, 9):
            knowledge_points.append({
                'original_id': kp_id,
                'course_original_id': course_id,
                'name': f"第{idx}章",
                'description': f"{course_name} - 第{idx}章",
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
    print("超星公网数据清洗工具 V2")
    print("="*60)

    # 1. 清洗学生信息
    persons = clean_person_data()

    # 2. 清洗课程信息
    courses, selected_course_ids = clean_course_data()

    # 3. 清洗班级信息
    classes = clean_clazz_data()

    # 4. 清洗选课关系
    course_persons = clean_course_person_data(selected_course_ids)

    # 5. 清洗活动日志
    activity_logs = clean_activity_log_data(selected_course_ids)

    # 6. 清洗作业答案
    work_answers = clean_work_answer_data(selected_course_ids)

    # 7. 清洗考试答案
    exam_answers = clean_exam_answer_data(selected_course_ids)

    # 8. 清洗成绩数据
    scores = clean_student_score_data(selected_course_ids)

    # 9. 提取知识点
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
        "选中课程": selected_course_ids,
    }

    with open(CLEANED_DIR / "cleaning_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n数据统计:")
    for key, value in report.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
