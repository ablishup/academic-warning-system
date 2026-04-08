#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟数据导入MySQL脚本
将生成的mock数据导入数据库
"""

import pandas as pd
import pymysql
from pathlib import Path
import json
from datetime import datetime
import numpy as np

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',  # 修改为你的密码
    'database': 'academic_warning_system',
    'charset': 'utf8mb4'
}

MOCK_DIR = Path(__file__).parent.parent / "mock"


def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def import_table(conn, table_name, csv_file, columns_mapping=None):
    """通用导入函数"""
    file_path = MOCK_DIR / csv_file
    if not file_path.exists():
        print(f"  文件不存在: {file_path}")
        return 0

    df = pd.read_csv(file_path, encoding='utf-8-sig')
    if len(df) == 0:
        return 0

    cursor = conn.cursor()
    count = 0

    # 获取表的所有列
    cursor.execute(f"SHOW COLUMNS FROM {table_name}")
    table_columns = [col[0] for col in cursor.fetchall()]

    # 过滤df中存在的列
    df_columns = df.columns.tolist()
    common_columns = [c for c in table_columns if c in df_columns and c != 'id']

    for _, row in df.iterrows():
        # 构建INSERT语句
        cols = []
        vals = []

        for col in common_columns:
            val = row.get(col)
            if pd.isna(val):
                vals.append(None)
            elif isinstance(val, (np.integer, np.floating)):
                vals.append(float(val) if isinstance(val, np.floating) else int(val))
            else:
                vals.append(str(val))
            cols.append(col)

        if not cols:
            continue

        placeholders = ', '.join(['%s'] * len(cols))
        sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({placeholders})"

        try:
            cursor.execute(sql, vals)
            count += 1
        except Exception as e:
            # 忽略重复错误
            if 'Duplicate' not in str(e):
                print(f"  导入错误: {e}")

    conn.commit()
    cursor.close()
    return count


def main():
    """主函数"""
    print("=" * 60)
    print("模拟数据导入MySQL工具")
    print("=" * 60)

    # 检查mock数据是否存在
    if not MOCK_DIR.exists():
        print(f"错误：mock数据目录不存在: {MOCK_DIR}")
        print("请先运行 generate_mock_data.py 生成数据")
        return

    # 连接数据库
    try:
        conn = get_connection()
        print(f"\n成功连接到数据库: {DB_CONFIG['database']}")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("请修改脚本中的 DB_CONFIG 配置")
        return

    # 定义导入顺序（考虑外键依赖）
    import_order = [
        ('majors', 'majors.csv'),
        ('classes', 'classes.csv'),
        ('students', 'students.csv'),
        ('users', 'users.csv'),
        ('courses', 'courses.csv'),
        ('knowledge_points', 'knowledge_points.csv'),
        ('course_enrollments', 'course_enrollments.csv'),
        ('learning_activities', 'learning_activities.csv'),
        ('homework_assignments', 'homework_assignments.csv'),
        ('homework_submissions', 'homework_submissions.csv'),
        ('exam_assignments', 'exam_assignments.csv'),
        ('exam_results', 'exam_results.csv'),
        ('warning_records', 'warning_records.csv'),
    ]

    print("\n开始导入数据...")
    total_count = 0

    for table, csv_file in import_order:
        print(f"\n导入 {table}...")
        count = import_table(conn, table, csv_file)
        print(f"  成功导入 {count} 条记录")
        total_count += count

    print("\n" + "=" * 60)
    print(f"数据导入完成！共导入 {total_count} 条记录")
    print("=" * 60)

    # 显示统计
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM students) as students,
            (SELECT COUNT(*) FROM courses) as courses,
            (SELECT COUNT(*) FROM warning_records WHERE status='active') as warnings
    """)
    stats = cursor.fetchone()
    print(f"\n数据库统计:")
    print(f"  学生数: {stats[0]}")
    print(f"  课程数: {stats[1]}")
    print(f"  活跃预警: {stats[2]}")

    cursor.close()
    conn.close()
    print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()
