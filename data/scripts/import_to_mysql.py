#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清洗后的数据导入MySQL脚本
功能：
1. 连接MySQL数据库
2. 将清洗后的CSV数据导入对应表
3. 建立知识点关联（简化方案）
4. 计算并填充知识点掌握度

使用方法：
    1. 先在MySQL中执行 chaoxing_schema.sql 创建表
    2. 修改本脚本中的数据库连接配置
    3. python import_to_mysql.py
"""

import pandas as pd
import pymysql
from pathlib import Path
import json
from datetime import datetime
import numpy as np

# ==================== 配置区域 ====================

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'YYXyyx204821',
    'database': 'academic_warning_system',
    'charset': 'utf8mb4'
}

CLEANED_DIR = Path(__file__).parent.parent / "cleaned"

# ID映射缓存（原始ID -> 新ID）
id_mappings = {
    'students': {},      # raw_id -> new_id
    'courses': {},       # raw_id -> new_id
    'classes': {},       # raw_id -> new_id
    'knowledge_points': {},  # 需要动态生成
}

# ==================== 数据库连接 ====================

def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


# ==================== 导入基础表 ====================

def import_majors(conn):
    """导入专业数据（使用默认值）"""
    print("专业数据使用SQL初始化中的默认值")
    return True


def import_classes(conn):
    """导入班级数据"""
    print("\n导入班级数据...")

    df = pd.read_csv(CLEANED_DIR / "cleaned_classes.csv", encoding='utf-8-sig')
    if len(df) == 0:
        print("  无班级数据")
        return False

    cursor = conn.cursor()

    for _, row in df.iterrows():
        sql = """
            INSERT INTO classes (raw_id, name, grade, major_id)
            VALUES (%s, %s, %s, %s)
        """
        # 随机分配专业（实际项目中应该有专业信息）
        major_id = int(row.get('major_id', 0)) % 4 + 1 if pd.notna(row.get('major_id')) else 1

        cursor.execute(sql, (
            str(row.get('original_id', '')),
            str(row.get('name', '')),
            str(row.get('grade', '')),
            major_id
        ))

        # 保存ID映射
        new_id = cursor.lastrowid
        raw_id = str(row.get('original_id', ''))
        if raw_id:
            id_mappings['classes'][raw_id] = new_id

    conn.commit()
    cursor.close()
    print(f"  成功导入 {len(df)} 个班级")
    return True


def import_students(conn):
    """导入学生数据"""
    print("\n导入学生数据...")

    df = pd.read_csv(CLEANED_DIR / "cleaned_persons.csv", encoding='utf-8-sig')
    if len(df) == 0:
        print("  无学生数据")
        return False

    cursor = conn.cursor()

    success_count = 0
    for _, row in df.iterrows():
        # 性别转换
        gender = '未知'
        sex_val = str(row.get('gender', '')).lower()
        if sex_val in ['1', '男', 'male', 'm']:
            gender = '男'
        elif sex_val in ['0', '2', '女', 'female', 'f']:
            gender = '女'

        # 查找班级ID
        class_raw_id = str(row.get('class_id', ''))
        class_id = id_mappings['classes'].get(class_raw_id)

        sql = """
            INSERT INTO students (raw_id, student_no, name, class_id, gender, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                class_id = VALUES(class_id),
                gender = VALUES(gender)
        """

        try:
            cursor.execute(sql, (
                str(row.get('original_id', '')),
                str(row.get('student_no', '')) if pd.notna(row.get('student_no')) else None,
                str(row.get('name', '')),
                class_id,
                1 if gender == '男' else 2 if gender == '女' else 0,
                str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                str(row.get('email', '')) if pd.notna(row.get('email')) else None
            ))

            new_id = cursor.lastrowid
            raw_id = str(row.get('original_id', ''))
            if raw_id:
                id_mappings['students'][raw_id] = new_id
            success_count += 1
        except Exception as e:
            print(f"  导入学生失败 {row.get('student_no')}: {e}")

    conn.commit()
    cursor.close()
    print(f"  成功导入 {success_count} 名学生")
    return True


def import_courses(conn):
    """导入课程数据"""
    print("\n导入课程数据...")

    df = pd.read_csv(CLEANED_DIR / "cleaned_courses.csv", encoding='utf-8-sig')
    if len(df) == 0:
        print("  无课程数据")
        return False

    cursor = conn.cursor()

    for _, row in df.iterrows():
        sql = """
            INSERT INTO courses (raw_id, course_no, name, description, credit, hours, teacher_id, semester)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            str(row.get('original_id', '')),
            str(row.get('course_no', '')) if pd.notna(row.get('course_no')) else None,
            str(row.get('name', '')),
            str(row.get('description', ''))[:500] if pd.notna(row.get('description')) else None,
            float(row.get('credit', 3.0)) if pd.notna(row.get('credit')) else 3.0,
            int(row.get('hours', 48)) if pd.notna(row.get('hours')) else 48,
            int(row.get('teacher_id', 2)) if pd.notna(row.get('teacher_id')) else 2,
            str(row.get('semester', '2024-2025-1'))
        ))

        new_id = cursor.lastrowid
        raw_id = str(row.get('original_id', ''))
        if raw_id:
            id_mappings['courses'][raw_id] = new_id

    conn.commit()
    cursor.close()
    print(f"  成功导入 {len(df)} 门课程")
    return True


def import_course_enrollments(conn):
    """导入选课关系"""
    print("\n导入选课关系...")

    df = pd.read_csv(CLEANED_DIR / "cleaned_course_persons.csv", encoding='utf-8-sig')
    if len(df) == 0:
        print("  无选课数据")
        return False

    cursor = conn.cursor()

    success_count = 0
    for _, row in df.iterrows():
        # CSV中已经是新ID，直接使用
        course_id = int(row.get('course_id', 0))
        student_id = int(row.get('student_id', 0))

        if not course_id or not student_id:
            continue

        sql = """
            INSERT INTO course_enrollments (student_id, course_id, enroll_time)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE enroll_time = VALUES(enroll_time)
        """

        try:
            # 处理enroll_time格式
            enroll_time = row.get('enroll_time')
            if pd.isna(enroll_time) or enroll_time == '':
                enroll_time = datetime.now()
            else:
                # 如果是字符串，转换为datetime
                if isinstance(enroll_time, str):
                    try:
                        enroll_time = datetime.strptime(enroll_time, '%Y-%m-%d')
                    except:
                        enroll_time = datetime.now()

            cursor.execute(sql, (
                student_id,
                course_id,
                enroll_time
            ))
            success_count += 1
        except Exception as e:
            if 'Duplicate' not in str(e):
                print(f"  导入选课失败: {e}")
            pass  # 忽略重复错误

    conn.commit()
    cursor.close()
    print(f"  成功导入 {success_count} 条选课记录")
    return True


# ==================== 导入知识点（简化方案） ====================

def import_knowledge_points(conn):
    """
    导入知识点（简化方案：课程章节作为知识点）
    """
    print("\n导入知识点（基于章节）...")

    df = pd.read_csv(CLEANED_DIR / "cleaned_knowledge_points.csv", encoding='utf-8-sig')
    if len(df) == 0:
        print("  无知识点数据")
        return False

    cursor = conn.cursor()

    for _, row in df.iterrows():
        course_id = int(row.get('course_id', 0))

        if not course_id:
            continue

        sql = """
            INSERT INTO knowledge_points (course_id, name, description, chapter_no)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, (
            course_id,
            str(row.get('name', '')),
            str(row.get('description', ''))[:500] if pd.notna(row.get('description')) else None,
            str(row.get('chapter_no', '第1章'))
        ))

        new_id = cursor.lastrowid
        kp_id = str(row.get('id', ''))
        if kp_id:
            id_mappings['knowledge_points'][kp_id] = new_id

    conn.commit()
    cursor.close()
    print(f"  成功导入 {len(df)} 个知识点")
    return True


# ==================== 导入学习活动 ====================

def import_learning_activities(conn):
    """导入学习活动记录"""
    print("\n导入学习活动记录...")

    file_path = CLEANED_DIR / "cleaned_activity_logs.csv"
    if not file_path.exists():
        print("  无活动日志文件")
        return False

    # 分批读取
    chunk_size = 5000
    total_count = 0

    for chunk in pd.read_csv(file_path, encoding='utf-8-sig', chunksize=chunk_size):
        cursor = conn.cursor()

        for _, row in chunk.iterrows():
            student_id = int(row.get('student_id', 0))
            course_id = int(row.get('course_id', 0))

            if not student_id or not course_id:
                continue

            sql = """
                INSERT INTO learning_activities
                (student_id, course_id, activity_type, activity_name, duration, start_time, end_time, progress)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            try:
                start_time = row.get('start_time', datetime.now())
                duration = int(row.get('duration', 0)) if pd.notna(row.get('duration')) else 0
                progress = float(row.get('progress', 0)) if pd.notna(row.get('progress')) else None

                cursor.execute(sql, (
                    student_id,
                    course_id,
                    str(row.get('activity_type', 'other')),
                    str(row.get('activity_name', ''))[:200] if pd.notna(row.get('activity_name')) else None,
                    duration,
                    start_time,
                    row.get('end_time', start_time) if pd.notna(row.get('end_time')) else start_time,
                    progress
                ))
                total_count += 1
            except Exception as e:
                pass

        conn.commit()
        cursor.close()

    print(f"  成功导入 {total_count} 条活动记录")
    return True


# ==================== 导入作业数据 ====================

def import_homework_data(conn):
    """导入作业任务和提交记录"""
    print("\n导入作业数据...")

    cursor = conn.cursor()
    homework_mapping = {}  # assignment_id -> new_id

    # 1. 导入作业任务
    hw_assignments_file = CLEANED_DIR / "cleaned_homework_assignments.csv"
    if hw_assignments_file.exists():
        df = pd.read_csv(hw_assignments_file, encoding='utf-8-sig')
        for _, row in df.iterrows():
            course_id = int(row.get('course_id', 0))
            if not course_id:
                continue

            sql = """
                INSERT INTO homework_assignments
                (course_id, knowledge_point_id, title, description, full_score, start_time, deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            try:
                cursor.execute(sql, (
                    course_id,
                    int(row.get('knowledge_point_id')) if pd.notna(row.get('knowledge_point_id')) else None,
                    str(row.get('title', '')),
                    str(row.get('description', ''))[:500] if pd.notna(row.get('description')) else None,
                    float(row.get('full_score', 100.0)),
                    row.get('start_time'),
                    row.get('deadline')
                ))

                new_id = cursor.lastrowid
                orig_id = str(row.get('id', ''))
                if orig_id:
                    homework_mapping[orig_id] = new_id
            except Exception as e:
                pass

        conn.commit()
        print(f"  成功导入 {len(homework_mapping)} 个作业任务")

    # 2. 导入作业提交记录
    sub_file = CLEANED_DIR / "cleaned_homework_submissions.csv"
    if sub_file.exists():
        total_sub = 0
        for chunk in pd.read_csv(sub_file, encoding='utf-8-sig', chunksize=5000):
            for _, row in chunk.iterrows():
                student_id = int(row.get('student_id', 0))
                assignment_id = str(row.get('assignment_id', ''))
                homework_id = homework_mapping.get(assignment_id)

                if not student_id or not homework_id:
                    continue

                score_val = row.get('score', 0)
                try:
                    score = float(score_val) if pd.notna(score_val) else 0
                except:
                    score = 0

                sql = """
                    INSERT INTO homework_submissions
                    (assignment_id, student_id, score, submit_time, is_late)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE score = VALUES(score)
                """

                try:
                    cursor.execute(sql, (
                        homework_id,
                        student_id,
                        score,
                        row.get('submit_time'),
                        int(row.get('is_late', 0)) if pd.notna(row.get('is_late')) else 0
                    ))
                    total_sub += 1
                except:
                    pass

        conn.commit()
        print(f"  成功导入 {total_sub} 条作业提交记录")

    cursor.close()
    return True


# ==================== 导入考试数据 ====================

def import_exam_data(conn):
    """导入考试任务和结果"""
    print("\n导入考试数据...")

    cursor = conn.cursor()
    exam_mapping = {}

    # 1. 导入考试任务
    exam_file = CLEANED_DIR / "cleaned_exam_assignments.csv"
    if exam_file.exists():
        df = pd.read_csv(exam_file, encoding='utf-8-sig')
        for _, row in df.iterrows():
            course_id = int(row.get('course_id', 0))
            if not course_id:
                continue

            exam_type = str(row.get('exam_type', 'quiz'))
            # 映射考试类型
            if exam_type == 'midterm':
                exam_type_db = 'midterm'
            elif exam_type == 'final':
                exam_type_db = 'final'
            else:
                exam_type_db = 'quiz'

            sql = """
                INSERT INTO exam_assignments
                (course_id, title, exam_type, full_score, start_time, end_time, duration)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            try:
                cursor.execute(sql, (
                    course_id,
                    str(row.get('title', '')),
                    exam_type_db,
                    float(row.get('full_score', 100.0)),
                    row.get('start_time'),
                    row.get('end_time'),
                    int(row.get('duration', 120)) if pd.notna(row.get('duration')) else 120
                ))

                new_id = cursor.lastrowid
                orig_id = str(row.get('id', ''))
                if orig_id:
                    exam_mapping[orig_id] = new_id
            except Exception as e:
                pass

        conn.commit()
        print(f"  成功导入 {len(exam_mapping)} 个考试任务")

    # 2. 导入考试结果
    result_file = CLEANED_DIR / "cleaned_exam_results.csv"
    if result_file.exists():
        total_results = 0
        df = pd.read_csv(result_file, encoding='utf-8-sig')

        for _, row in df.iterrows():
            student_id = int(row.get('student_id', 0))
            exam_id = str(row.get('exam_id', ''))
            exam_db_id = exam_mapping.get(exam_id)

            if not student_id or not exam_db_id:
                continue

            score_val = row.get('score', 0)
            try:
                score = float(score_val) if pd.notna(score_val) else 0
            except:
                score = 0

            sql = """
                INSERT INTO exam_results
                (exam_id, student_id, score, submit_time)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE score = VALUES(score)
            """

            try:
                cursor.execute(sql, (
                    exam_db_id,
                    student_id,
                    score,
                    row.get('submit_time')
                ))
                total_results += 1
            except:
                pass

        conn.commit()
        print(f"  成功导入 {total_results} 条考试结果")

    cursor.close()
    return True


# ==================== 计算知识点掌握度 ====================

def calculate_knowledge_mastery(conn):
    """
    基于作业和考试成绩计算知识点掌握度（创建视图表用于查询）
    """
    print("\n知识点掌握度计算...")
    print("  知识点掌握度将通过API动态计算")
    return True


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("="*60)
    print("数据导入MySQL工具")
    print("="*60)

    # 检查清洗数据是否存在
    if not CLEANED_DIR.exists():
        print(f"错误：清洗数据目录不存在: {CLEANED_DIR}")
        print("请先运行 clean_data.py 清洗数据")
        return

    # 连接数据库
    try:
        conn = get_connection()
        print(f"\n成功连接到数据库: {DB_CONFIG['database']}")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("请检查 DB_CONFIG 配置")
        return

    try:
        # 1. 导入基础表
        import_majors(conn)
        import_classes(conn)
        import_students(conn)
        import_courses(conn)
        import_course_enrollments(conn)

        # 2. 导入知识点（简化方案）
        import_knowledge_points(conn)

        # 3. 导入学习活动
        import_learning_activities(conn)

        # 4. 导入作业和考试
        import_homework_data(conn)
        import_exam_data(conn)

        # 5. 计算知识点掌握度
        calculate_knowledge_mastery(conn)

        print("\n" + "="*60)
        print("数据导入完成！")
        print("="*60)

    except Exception as e:
        print(f"\n导入过程出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()
        print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()
