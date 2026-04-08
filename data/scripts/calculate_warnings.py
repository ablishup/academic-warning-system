#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学业预警计算脚本
功能：
1. 计算学生的各项预警指标
2. 根据权重计算综合预警分数
3. 划分预警等级
4. 生成AI建议（DeepSeek API + 模板兜底）
5. 将预警记录写入数据库

使用方法：
    python calculate_warnings.py

预警算法：
    综合评分 = 出勤率*0.3 + 进度*0.2 + 作业*0.3 + 考试*0.2
    红色预警: <60, 橙色预警: 60-75, 黄色预警: 75-85, 正常: >=85
"""

import pandas as pd
import pymysql
from pathlib import Path
import json
from datetime import datetime, timedelta
import requests
import time
from typing import Dict, List, Optional

# ==================== 配置区域 ====================

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'your_password',  # 修改为你的密码
    'database': 'academic_warning_system',
    'charset': 'utf8mb4'
}

# DeepSeek API配置
DEEPSEEK_CONFIG = {
    'api_key': 'your_deepseek_api_key',  # 填入你的API Key
    'api_url': 'https://api.deepseek.com/chat/completions',
    'model': 'deepseek-chat',
    'timeout': 5,  # 5秒超时
    'max_tokens': 500,
    'temperature': 0.7
}

# 预警权重配置（应与数据库中的默认规则一致）
WEIGHTS = {
    'attendance': 0.30,   # 出勤率权重
    'progress': 0.20,     # 进度权重
    'homework': 0.30,     # 作业权重
    'exam': 0.20          # 考试权重
}

# 预警阈值
THRESHOLDS = {
    'red': 60.0,      # 红色预警阈值
    'orange': 75.0,   # 橙色预警阈值
    'yellow': 85.0    # 黄色预警阈值
}

# ==================== 数据库连接 ====================

def get_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


# ==================== 指标计算 ====================

def calculate_attendance_score(conn, student_id: int, course_id: Optional[int] = None) -> float:
    """
    计算出勤率得分（基于学习活动记录）
    简化计算：活动参与次数 / 预期活动次数 * 100
    """
    cursor = conn.cursor()

    course_filter = "AND course_id = %s" if course_id else ""
    params = [student_id]
    if course_id:
        params.append(course_id)

    # 获取学生的活动参与次数
    cursor.execute(f"""
        SELECT COUNT(*) as activity_count,
               SUM(duration) as total_duration
        FROM learning_activities
        WHERE student_id = %s {course_filter}
    """, params)

    result = cursor.fetchone()
    activity_count = result[0] if result else 0
    total_duration = result[1] if result and result[1] else 0

    # 获取课程预期活动次数（简化：按课程章节数 * 3）
    if course_id:
        cursor.execute("""
            SELECT total_chapters * 3 as expected_activities
            FROM courses WHERE id = %s
        """, (course_id,))
        expected = cursor.fetchone()
        expected_count = expected[0] if expected and expected[0] else 24
    else:
        # 跨课程计算，取平均值
        cursor.execute("""
            SELECT AVG(total_chapters * 3)
            FROM courses c
            JOIN course_enrollments ce ON c.id = ce.course_id
            WHERE ce.student_id = %s
        """, (student_id,))
        expected = cursor.fetchone()
        expected_count = expected[0] if expected and expected[0] else 24

    cursor.close()

    # 计算得分：活动参与率 + 学习时长加成
    participation_rate = min(100, (activity_count / max(expected_count, 1)) * 100)
    duration_bonus = min(10, total_duration / 3600)  # 每学习1小时加1分，最多10分

    return min(100, participation_rate + duration_bonus)


def calculate_progress_score(conn, student_id: int, course_id: Optional[int] = None) -> float:
    """
    计算学习进度得分（基于知识点掌握度）
    """
    cursor = conn.cursor()

    course_filter = "AND kp.course_id = %s" if course_id else ""
    params = [student_id]
    if course_id:
        params.append(course_id)

    cursor.execute(f"""
        SELECT AVG(km.mastery_level) as avg_mastery,
               COUNT(DISTINCT km.knowledge_point_id) as mastered_count,
               COUNT(DISTINCT kp.id) as total_kp
        FROM knowledge_points kp
        LEFT JOIN knowledge_mastery km ON kp.id = km.knowledge_point_id AND km.student_id = %s
        WHERE 1=1 {course_filter}
    """, params)

    result = cursor.fetchone()
    cursor.close()

    if not result or result[2] == 0:
        return 0.0

    avg_mastery = result[0] if result[0] else 0
    mastered_count = result[1] if result[1] else 0
    total_kp = result[2]

    # 进度 = 平均掌握度 * 0.6 + 知识点覆盖率 * 0.4
    coverage_rate = (mastered_count / total_kp) * 100
    progress = avg_mastery * 0.6 + coverage_rate * 0.4

    return min(100, progress)


def calculate_homework_score(conn, student_id: int, course_id: Optional[int] = None) -> float:
    """
    计算作业得分
    """
    cursor = conn.cursor()

    course_filter = "AND hs.course_id = %s" if course_id else ""
    params = [student_id]
    if course_id:
        params.append(course_id)

    cursor.execute(f"""
        SELECT AVG(hs.score) as avg_score,
               COUNT(DISTINCT hs.homework_id) as submitted_count,
               COUNT(DISTINCT ha.id) as total_homework
        FROM homework_assignments ha
        LEFT JOIN homework_submissions hs ON ha.id = hs.homework_id AND hs.student_id = %s
        WHERE 1=1 {course_filter}
    """, params)

    result = cursor.fetchone()
    cursor.close()

    if not result:
        return 0.0

    avg_score = result[0] if result[0] else 0
    submitted_count = result[1] if result[1] else 0
    total_homework = result[2] if result[2] else 0

    # 作业得分 = 平均分 * 0.7 + 提交率 * 0.3 * 100
    submit_rate = (submitted_count / max(total_homework, 1))
    homework_score = avg_score * 0.7 + submit_rate * 30

    return min(100, homework_score)


def calculate_exam_score(conn, student_id: int, course_id: Optional[int] = None) -> float:
    """
    计算考试得分
    """
    cursor = conn.cursor()

    course_filter = "AND er.course_id = %s" if course_id else ""
    params = [student_id]
    if course_id:
        params.append(course_id)

    cursor.execute(f"""
        SELECT AVG(er.score) as avg_score,
               COUNT(*) as exam_count
        FROM exam_results er
        WHERE er.student_id = %s {course_filter}
    """, params)

    result = cursor.fetchone()
    cursor.close()

    if not result or not result[0]:
        return 0.0

    avg_score = result[0]
    exam_count = result[1]

    # 考试次数加成：参加考试越多，得分越可信
    reliability_bonus = min(5, exam_count)

    return min(100, avg_score + reliability_bonus)


def calculate_comprehensive_score(
    attendance: float,
    progress: float,
    homework: float,
    exam: float
) -> float:
    """
    计算综合预警分数
    """
    score = (
        attendance * WEIGHTS['attendance'] +
        progress * WEIGHTS['progress'] +
        homework * WEIGHTS['homework'] +
        exam * WEIGHTS['exam']
    )
    return round(score, 2)


def determine_risk_level(score: float) -> str:
    """
    根据分数确定预警等级
    """
    if score < THRESHOLDS['red']:
        return 'red'
    elif score < THRESHOLDS['orange']:
        return 'orange'
    elif score < THRESHOLDS['yellow']:
        return 'yellow'
    else:
        return 'normal'


def analyze_risk_factors(
    attendance: float,
    progress: float,
    homework: float,
    exam: float
) -> Dict:
    """
    分析风险因素
    """
    factors = []

    if attendance < THRESHOLDS['yellow']:
        factors.append({
            'type': 'attendance',
            'score': attendance,
            'description': '出勤率偏低，学习活跃度不足'
        })

    if progress < THRESHOLDS['yellow']:
        factors.append({
            'type': 'progress',
            'score': progress,
            'description': '学习进度滞后，知识点掌握不完整'
        })

    if homework < THRESHOLDS['yellow']:
        factors.append({
            'type': 'homework',
            'score': homework,
            'description': '作业完成情况不佳'
        })

    if exam < THRESHOLDS['yellow']:
        factors.append({
            'type': 'exam',
            'score': exam,
            'description': '考试成绩不理想'
        })

    return {'factors': factors, 'count': len(factors)}


# ==================== AI建议生成 ====================

# 模板库（API失败时使用）
COUNSELOR_TEMPLATES = {
    'red': [
        "该学生当前学业状况令人担忧，建议立即安排面谈，了解具体困难并提供针对性帮助。",
        "学生已处于高危状态，建议启动学业帮扶机制，联合任课教师共同关注。",
        "学业成绩严重下滑，建议深入了解原因，必要时协助调整学习计划或课程安排。"
    ],
    'orange': [
        "该学生存在一定学业风险，建议加强课堂考勤监督，定期跟进学习进度。",
        "学生学习状态需要关注，建议提醒任课教师适当给予指导，鼓励其积极参与课堂互动。",
        "学业表现有待提升，建议与学生沟通，帮助其制定切实可行的改进计划。"
    ],
    'yellow': [
        "该学生整体表现尚可，建议继续保持关注，鼓励其向优秀方向发展。",
        "学习状态基本稳定，建议适当激励，帮助其突破瓶颈期。",
        "学业情况良好但仍有提升空间，建议关注其学习方法优化。"
    ],
    'normal': [
        "该学生学业表现良好，建议给予肯定和鼓励。",
        "学习状态优秀，可适当鼓励其帮助带动其他同学。",
        "学业情况稳定，建议保持现有学习节奏。"
    ]
}

STUDENT_TEMPLATES = {
    'red': [
        "你的学习状态需要引起重视，建议尽快与老师沟通，寻求帮助。合理安排学习时间，不要放弃！",
        "当前学业遇到困难是正常的，关键是积极面对。建议制定每日学习计划，逐步赶上进度。"
    ],
    'orange': [
        "你的学习还有提升空间，建议多参与课堂讨论，按时完成作业，相信你会取得进步！",
        "学习是一个持续的过程，建议找出薄弱环节针对性复习，保持积极心态。"
    ],
    'yellow': [
        "你的学习状态不错，继续保持！可以尝试挑战更高目标，突破自己。",
        "整体表现良好，建议优化学习方法，争取更上一层楼。"
    ],
    'normal': [
        "恭喜你保持良好的学习状态！继续保持，你一定能取得优异成绩。",
        "你的努力得到了回报，建议分享学习经验，帮助更多同学进步。"
    ]
}


def generate_ai_suggestion(
    student_name: str,
    risk_level: str,
    scores: Dict,
    risk_factors: Dict,
    for_student: bool = False
) -> str:
    """
    调用DeepSeek API生成AI建议
    """
    if not DEEPSEEK_CONFIG['api_key'] or DEEPSEEK_CONFIG['api_key'] == 'your_deepseek_api_key':
        # API未配置，使用模板
        return get_template_suggestion(risk_level, for_student)

    # 构建提示词
    level_desc = {
        'red': '高危（需立即干预）',
        'orange': '警告（需重点关注）',
        'yellow': '关注（需适当引导）',
        'normal': '正常（保持良好状态）'
    }

    factor_desc = "\n".join([
        f"- {f['type']}: {f['score']:.1f}分，{f['description']}"
        for f in risk_factors.get('factors', [])
    ]) or "各项指标均在正常范围内"

    if for_student:
        prompt = f"""作为学业助手，请为以下学生生成一段鼓励和建议（100字左右）：

学生：{student_name}
预警等级：{level_desc.get(risk_level)}
各项得分：
- 出勤率：{scores['attendance']:.1f}分
- 学习进度：{scores['progress']:.1f}分
- 作业成绩：{scores['homework']:.1f}分
- 考试成绩：{scores['exam']:.1f}分
- 综合得分：{scores['comprehensive']:.1f}分

问题分析：
{factor_desc}

请以亲切、鼓励的语气给出建议，帮助学生改进学习。"""
    else:
        prompt = f"""作为辅导员，请为以下学生生成一段干预建议（100字左右）：

学生：{student_name}
预警等级：{level_desc.get(risk_level)}
各项得分：
- 出勤率：{scores['attendance']:.1f}分
- 学习进度：{scores['progress']:.1f}分
- 作业成绩：{scores['homework']:.1f}分
- 考试成绩：{scores['exam']:.1f}分
- 综合得分：{scores['comprehensive']:.1f}分

问题分析：
{factor_desc}

请给出具体的干预措施建议。"""

    try:
        response = requests.post(
            DEEPSEEK_CONFIG['api_url'],
            headers={
                'Authorization': f"Bearer {DEEPSEEK_CONFIG['api_key']}",
                'Content-Type': 'application/json'
            },
            json={
                'model': DEEPSEEK_CONFIG['model'],
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的学业预警分析助手。'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': DEEPSEEK_CONFIG['max_tokens'],
                'temperature': DEEPSEEK_CONFIG['temperature']
            },
            timeout=DEEPSEEK_CONFIG['timeout']
        )

        if response.status_code == 200:
            result = response.json()
            suggestion = result['choices'][0]['message']['content'].strip()
            return suggestion
        else:
            print(f"  API调用失败: {response.status_code}")
            return get_template_suggestion(risk_level, for_student)

    except requests.exceptions.Timeout:
        print("  API调用超时，使用模板")
        return get_template_suggestion(risk_level, for_student)
    except Exception as e:
        print(f"  API调用异常: {e}")
        return get_template_suggestion(risk_level, for_student)


def get_template_suggestion(risk_level: str, for_student: bool = False) -> str:
    """获取模板建议"""
    import random
    templates = STUDENT_TEMPLATES if for_student else COUNSELOR_TEMPLATES
    return random.choice(templates.get(risk_level, templates['normal']))


# ==================== 预警记录生成 ====================

def generate_warning_records(conn):
    """
    为所有学生生成预警记录
    """
    print("\n生成预警记录...")

    cursor = conn.cursor()

    # 获取所有学生和课程
    cursor.execute("""
        SELECT s.id, s.name, c.id as course_id, c.name as course_name
        FROM students s
        CROSS JOIN courses c
        WHERE EXISTS (
            SELECT 1 FROM course_enrollments ce
            WHERE ce.student_id = s.id AND ce.course_id = c.id
        )
    """)

    enrollments = cursor.fetchall()
    print(f"  共 {len(enrollments)} 条学生-课程记录需要处理")

    warning_count = 0

    for student_id, student_name, course_id, course_name in enrollments:
        # 计算各项指标
        attendance = calculate_attendance_score(conn, student_id, course_id)
        progress = calculate_progress_score(conn, student_id, course_id)
        homework = calculate_homework_score(conn, student_id, course_id)
        exam = calculate_exam_score(conn, student_id, course_id)

        # 计算综合得分
        comprehensive = calculate_comprehensive_score(attendance, progress, homework, exam)

        # 确定预警等级
        risk_level = determine_risk_level(comprehensive)

        # 分析风险因素
        risk_factors = analyze_risk_factors(attendance, progress, homework, exam)

        # 生成AI建议
        scores = {
            'attendance': attendance,
            'progress': progress,
            'homework': homework,
            'exam': exam,
            'comprehensive': comprehensive
        }

        try:
            ai_suggestion = generate_ai_suggestion(
                student_name, risk_level, scores, risk_factors, for_student=False
            )
            ai_suggestion_student = generate_ai_suggestion(
                student_name, risk_level, scores, risk_factors, for_student=True
            )
        except Exception as e:
            print(f"  生成AI建议失败: {e}")
            ai_suggestion = get_template_suggestion(risk_level, False)
            ai_suggestion_student = get_template_suggestion(risk_level, True)

        # 插入预警记录
        sql = """
            INSERT INTO warning_records
            (student_id, course_id, attendance_score, progress_score, homework_score,
             exam_score, comprehensive_score, risk_level, risk_factors,
             ai_suggestion, ai_suggestion_for_student, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
                attendance_score = VALUES(attendance_score),
                progress_score = VALUES(progress_score),
                homework_score = VALUES(homework_score),
                exam_score = VALUES(exam_score),
                comprehensive_score = VALUES(comprehensive_score),
                risk_level = VALUES(risk_level),
                risk_factors = VALUES(risk_factors),
                ai_suggestion = VALUES(ai_suggestion),
                ai_suggestion_for_student = VALUES(ai_suggestion_for_student),
                updated_at = NOW()
        """

        try:
            cursor.execute(sql, (
                student_id,
                course_id,
                attendance,
                progress,
                homework,
                exam,
                comprehensive,
                risk_level,
                json.dumps(risk_factors, ensure_ascii=False),
                ai_suggestion,
                ai_suggestion_student,
                'active'
            ))
            warning_count += 1

            if warning_count % 100 == 0:
                print(f"  已处理 {warning_count} 条记录...")

        except Exception as e:
            print(f"  插入预警记录失败: {e}")

    conn.commit()
    cursor.close()

    print(f"  成功生成 {warning_count} 条预警记录")
    return warning_count


def generate_summary_report(conn):
    """
    生成预警统计摘要
    """
    print("\n预警统计摘要：")

    cursor = conn.cursor()

    # 各级别预警数量
    cursor.execute("""
        SELECT risk_level, COUNT(*) as count
        FROM warning_records
        GROUP BY risk_level
        ORDER BY FIELD(risk_level, 'red', 'orange', 'yellow', 'normal')
    """)

    results = cursor.fetchall()
    for level, count in results:
        level_name = {
            'red': '🔴 红色预警',
            'orange': '🟠 橙色预警',
            'yellow': '🟡 黄色预警',
            'normal': '🟢 正常'
        }.get(level, level)
        print(f"  {level_name}: {count} 人")

    # 高危学生TOP 10
    print("\n  综合得分最低的10名学生：")
    cursor.execute("""
        SELECT s.name, c.name as course_name, wr.comprehensive_score
        FROM warning_records wr
        JOIN students s ON wr.student_id = s.id
        JOIN courses c ON wr.course_id = c.id
        WHERE wr.risk_level IN ('red', 'orange')
        ORDER BY wr.comprehensive_score ASC
        LIMIT 10
    """)

    for name, course, score in cursor.fetchall():
        print(f"    {name} ({course}): {score:.2f}分")

    cursor.close()


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("="*60)
    print("学业预警计算工具")
    print("="*60)

    # 连接数据库
    try:
        conn = get_connection()
        print(f"\n成功连接到数据库: {DB_CONFIG['database']}")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return

    try:
        # 生成预警记录
        warning_count = generate_warning_records(conn)

        # 生成统计摘要
        generate_summary_report(conn)

        print("\n" + "="*60)
        print("预警计算完成！")
        print("="*60)

    except Exception as e:
        print(f"\n计算过程出错: {e}")
        import traceback
        traceback.print_exc()

    finally:
        conn.close()
        print("\n数据库连接已关闭")


if __name__ == "__main__":
    main()
