import os
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["POST"])
def generate_comment(request):
    """
    基于学生学习数据，使用DeepSeek API生成AI评语
    """
    try:
        data = json.loads(request.body)

        # 获取学生学习数据
        student_name = data.get('student_name', '同学')
        learning_stats = data.get('learning', {})
        homework_stats = data.get('homework', {})
        exam_stats = data.get('exam', {})
        warnings = data.get('warnings', [])

        # 提取关键指标
        progress = learning_stats.get('avg_progress', 0)
        total_duration = learning_stats.get('total_duration', 0)
        homework_avg = homework_stats.get('avg_score', 0)
        homework_completion = homework_stats.get('completion_rate', 0)
        exam_avg = exam_stats.get('avg_score', 0)

        # 构建提示词
        prompt = f"""你是一位专业的教育顾问，请基于以下学生的学习数据，生成一段个性化的学习评语和学习建议。

学生信息：{student_name}

学习数据：
- 视频学习进度：{progress:.1f}%
- 总学习时长：{total_duration/3600:.1f}小时
- 作业平均分：{homework_avg:.1f}分
- 作业完成率：{homework_completion:.1f}%
- 考试平均分：{exam_avg:.1f}分
- 预警状态：{'有预警' if warnings else '无预警'}

请按以下格式输出（JSON格式）：
{{
    "comment": "一段鼓励性的评语，指出学生的优点和需要改进的地方，200字左右",
    "suggestions": ["具体建议1", "具体建议2", "具体建议3"],
    "prediction": {{
        "score": 预测期末分数（整数）,
        "assessment": "对预测结果的简要说明"
    }}
}}

注意：
1. 评语要客观、鼓励性，符合学生实际表现
2. 建议要具体可行
3. 预测分数要基于现有数据合理推断"""

        # 调用DeepSeek API
        api_key = os.environ.get('DEEPSEEK_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
        api_url = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')

        if not api_key or api_key == '你的API_KEY':
            # 如果没有配置API Key，返回模拟数据
            return JsonResponse({
                'code': 200,
                'data': generate_mock_comment(student_name, progress, homework_avg, exam_avg, total_duration),
                'message': '使用模拟数据（API Key未配置）'
            })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': '你是一位专业的教育顾问，善于分析学生的学习数据并给出个性化的建议。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 1000
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        result = response.json()
        ai_content = result['choices'][0]['message']['content']

        # 解析AI返回的JSON
        try:
            # 尝试提取JSON部分
            json_start = ai_content.find('{')
            json_end = ai_content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                ai_data = json.loads(ai_content[json_start:json_end])
            else:
                ai_data = json.loads(ai_content)

            return JsonResponse({
                'code': 200,
                'data': {
                    'comment': ai_data.get('comment', ''),
                    'suggestions': ai_data.get('suggestions', []),
                    'prediction': ai_data.get('prediction', {}),
                    'generateTime': get_current_time()
                }
            })

        except json.JSONDecodeError:
            # 如果不是JSON格式，直接返回文本
            return JsonResponse({
                'code': 200,
                'data': {
                    'comment': ai_content,
                    'suggestions': ['请认真学习，提高课堂参与度', '按时完成作业，巩固所学知识', '积极参与讨论，提高理解能力'],
                    'prediction': {'score': int((progress + homework_avg + exam_avg) / 3), 'assessment': '基于当前表现的预测'},
                    'generateTime': get_current_time()
                }
            })

    except requests.exceptions.RequestException as e:
        print(f"DeepSeek API调用失败: {e}")
        # API调用失败时返回模拟数据
        return JsonResponse({
            'code': 200,
            'data': generate_mock_comment(
                data.get('student_name', '同学'),
                data.get('learning', {}).get('avg_progress', 0),
                data.get('homework', {}).get('avg_score', 0),
                data.get('exam', {}).get('avg_score', 0),
                data.get('learning', {}).get('total_duration', 0)
            ),
            'message': '使用本地模拟数据'
        })

    except Exception as e:
        print(f"生成评语失败: {e}")
        return JsonResponse({
            'code': 500,
            'message': f'生成评语失败: {str(e)}'
        }, status=500)


def generate_mock_comment(student_name, progress, homework_avg, exam_avg, total_duration):
    """生成模拟评语（当API不可用时使用）"""
    hours = total_duration / 3600

    if progress >= 80 and homework_avg >= 80 and exam_avg >= 80:
        comment = f"{student_name}，你的学习表现非常优秀！视频学习进度达到{progress:.1f}%，作业和考试成绩都保持在较高水平。你展现出了良好的学习态度和自律能力，继续保持！"
        suggestions = [
            "可以尝试学习一些拓展内容，挑战更高难度的题目",
            "帮助其他同学解答问题，巩固自己的知识",
            "关注学科前沿动态，拓宽知识面"
        ]
        prediction = {"score": 88, "assessment": "预计期末成绩优秀"}
    elif progress >= 60 and homework_avg >= 60 and exam_avg >= 60:
        comment = f"{student_name}，你的学习状态总体良好。视频学习进度为{progress:.1f}%，基本跟上课程节奏。但还有一些提升空间，建议在学习方法上做些调整。"
        suggestions = [
            "增加课后复习时间，及时巩固所学知识",
            "对于作业中的错题要认真分析原因",
            "多与老师和同学交流，解决疑惑"
        ]
        prediction = {"score": 75, "assessment": "预计期末成绩中等"}
    else:
        comment = f"{student_name}，目前你的学习进度有些滞后（{progress:.1f}%），作业或考试成绩也不太理想。需要引起重视，及时调整学习状态。"
        suggestions = [
            "制定详细的学习计划，每天保证固定的学习时间",
            "优先补上落下的视频课程内容",
            "寻求老师或同学的帮助，解决学习困难",
            "调整作息时间，保持良好的学习状态"
        ]
        prediction = {"score": 58, "assessment": "预计有挂科风险，需努力"}

    if hours < 10:
        suggestions.append("建议增加学习时间，每天至少学习1-2小时")

    return {
        'comment': comment,
        'suggestions': suggestions,
        'prediction': prediction,
        'generateTime': get_current_time()
    }


def get_current_time():
    """获取当前时间字符串"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def counselor_comment_data(warning):
    """
    解析counselor_suggestions字段，返回完整的辅导员评语数据
    支持新格式（包含analysis等）和旧格式（纯数组）
    """
    suggestions_data = warning.counselor_suggestions or []
    if isinstance(suggestions_data, dict):
        # 新格式，包含完整的AI评语数据
        return {
            'summary': warning.counselor_comment or '',
            'analysis': suggestions_data.get('analysis', ''),
            'suggestions': suggestions_data.get('suggestions', []),
            'action_plan': suggestions_data.get('action_plan', ''),
            'talking_points': warning.counselor_talk_script or '',
        }
    else:
        # 旧格式，suggestions_data是纯数组
        return {
            'summary': warning.counselor_comment or '',
            'analysis': '',
            'suggestions': suggestions_data if isinstance(suggestions_data, list) else [],
            'action_plan': '',
            'talking_points': warning.counselor_talk_script or '',
        }


# =============================================================================
# 辅导员端AI评语接口（新增）
# =============================================================================

from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from warning_system.models import WarningRecord
from classes.models import Student


def get_student_detail_data(student_id):
    """获取学生详细数据用于AI评语生成"""
    try:
        student = Student.objects.get(id=student_id)

        # 从StudentCourseScore获取综合得分数据
        from warning_system.models import StudentCourseScore
        score = StudentCourseScore.objects.filter(student_id=student_id).first()

        data = {
            'id': student.id,
            'name': student.name,
            'student_no': student.student_no,
            'class_name': getattr(student, 'class_name', ''),
            'phone': getattr(student, 'phone', ''),
        }

        if score:
            data.update({
                'attendance_rate': float(score.attendance_rate or 0),
                'video_progress': float(score.video_progress or 0),
                'homework_avg': float(score.homework_avg or 0),
                'homework_submit_rate': float(score.homework_submit_rate or 0),
                'exam_avg': float(score.exam_avg or 0),
            })

        return data
    except Student.DoesNotExist:
        raise Exception(f'学生不存在: {student_id}')


@csrf_exempt
@require_http_methods(["POST"])
def generate_counselor_comment(request):
    """
    辅导员生成干预建议评语
    POST /ai/counselor-comment/
    {
        "student_id": 1,
        "warning_id": 1
    }
    """
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        warning_id = data.get('warning_id')

        if not student_id or not warning_id:
            return JsonResponse({
                'code': 400,
                'message': '缺少student_id或warning_id参数'
            }, status=400)

        # 获取学生和预警数据
        student_data = get_student_detail_data(student_id)
        warning = WarningRecord.objects.get(id=warning_id)

        # 构建辅导员专用Prompt
        prompt = f"""你是一位资深的高校辅导员，拥有10年学生工作经验，擅长学业指导和心理健康辅导。

请根据以下学生的学习数据，生成专业的辅导员干预建议。

【学生信息】
姓名: {student_data['name']}
学号: {student_data['student_no']}
班级: {student_data.get('class_name', '未知')}

【预警信息】
风险等级: {warning.risk_level}
综合得分: {warning.composite_score}
出勤率得分: {warning.attendance_score}
学习进度得分: {warning.progress_score}
作业成绩得分: {warning.homework_score}
考试成绩得分: {warning.exam_score}

【学习数据】
出勤率: {student_data.get('attendance_rate', 'N/A')}%
视频学习进度: {student_data.get('video_progress', 'N/A')}%
作业平均分: {student_data.get('homework_avg', 'N/A')}
作业提交率: {student_data.get('homework_submit_rate', 'N/A')}%
考试平均分: {student_data.get('exam_avg', 'N/A')}

请输出JSON格式：
{{
    "summary": "总体评价（50-100字）",
    "analysis": "问题分析（100-200字）",
    "suggestions": ["具体建议1", "具体建议2", "具体建议3"],
    "action_plan": "行动计划（100-150字）",
    "talking_points": "与学生沟通的话术建议（100-150字）"
}}

要求：
1. 分析客观准确，指出具体问题
2. 建议具体可行，有可操作性
3. 沟通话术要温暖亲切，避免说教
4. 重点关注学生的心理感受"""

        # 调用DeepSeek API
        api_key = os.environ.get('DEEPSEEK_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
        api_url = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')

        if not api_key or api_key == '你的API_KEY':
            # 使用模拟数据
            mock_data = generate_counselor_mock_comment(
                student_data['name'],
                warning.risk_level,
                student_data.get('homework_avg', 0)
            )

            # 保存到数据库
            warning.counselor_comment = mock_data['summary']
            warning.counselor_talk_script = mock_data.get('talking_points', '')
            # 将完整的AI评语数据保存在JSON字段中
            warning.counselor_suggestions = {
                'suggestions': mock_data['suggestions'],
                'analysis': mock_data.get('analysis', ''),
                'action_plan': mock_data.get('action_plan', '')
            }
            warning.ai_generated_at = timezone.now()
            warning.save()

            return JsonResponse({
                'code': 200,
                'data': mock_data,
                'message': '使用模拟数据（API Key未配置）'
            })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': '你是一位资深的高校辅导员，擅长生成专业的学生干预建议。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 2000,
            'response_format': {'type': 'json_object'}
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()

        result = response.json()
        ai_content = result['choices'][0]['message']['content']

        # 解析JSON
        try:
            json_start = ai_content.find('{')
            json_end = ai_content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                ai_data = json.loads(ai_content[json_start:json_end])
            else:
                ai_data = json.loads(ai_content)
        except json.JSONDecodeError:
            ai_data = {
                'summary': '该学生当前学习状态需要关注',
                'analysis': '根据学习数据分析，学生在某些方面存在改进空间。',
                'suggestions': ['制定学习计划', '寻求帮助', '保持积极心态'],
                'action_plan': '建议近期制定详细的学习计划',
                'talking_points': '同学你好，老师想和你聊聊学习情况'
            }

        # 保存到数据库 - 保存完整的辅导员评语数据
        warning.counselor_comment = ai_data.get('summary', '')
        warning.counselor_talk_script = ai_data.get('talking_points', '')
        # 将完整的AI评语数据保存在JSON字段中
        warning.counselor_suggestions = {
            'suggestions': ai_data.get('suggestions', []),
            'analysis': ai_data.get('analysis', ''),
            'action_plan': ai_data.get('action_plan', '')
        }
        warning.ai_generated_at = timezone.now()

        # 获取正确的用户ID（解决users表和auth_user表的外键问题）
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE username = %s', [request.user.username])
            result = cursor.fetchone()
            user_id_in_users = result[0] if result else None
        warning.ai_generated_by_id = user_id_in_users

        warning.save()

        return JsonResponse({
            'code': 200,
            'data': ai_data
        })

    except WarningRecord.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'message': '预警记录不存在'
        }, status=404)
    except Exception as e:
        print(f"生成辅导员评语失败: {e}")
        return JsonResponse({
            'code': 500,
            'message': f'生成评语失败: {str(e)}'
        }, status=500)


def generate_counselor_mock_comment(student_name, risk_level, homework_avg):
    """生成辅导员模拟评语"""
    if risk_level == 'high':
        summary = f"{student_name}同学当前学习状态令人担忧，需要重点关注和干预。"
        analysis = "该生近期学习数据表现不佳，可能存在学习动力不足或学习方法不当的问题。建议辅导员主动约谈，了解具体情况。"
        suggestions = [
            "安排一对一谈心谈话，了解学生思想动态",
            "帮助制定切实可行的学习计划",
            "联系家长，寻求家校配合",
            "推荐学习帮扶资源或学业导师"
        ]
        action_plan = "本周内安排约谈，两周内跟进学习改善情况。"
        talking_points = f"{student_name}同学，老师注意到你最近的学习情况有些下滑，想和你聊聊。不用担心，我们一起来想办法解决，好吗？"
    elif risk_level == 'medium':
        summary = f"{student_name}同学学习状态有下滑趋势，需要适当关注和引导。"
        analysis = "该生部分学习指标出现下滑迹象，但总体还有改进空间。建议辅导员适时提醒和鼓励。"
        suggestions = [
            "与学生进行非正式交流，了解近况",
            "提醒学生注意时间管理和学习方法",
            "鼓励参加学习小组或辅导活动"
        ]
        action_plan = "两周内安排一次交流，关注学习状态变化。"
        talking_points = f"{student_name}同学，最近感觉怎么样？学习上有没有遇到什么困难？"
    else:
        summary = f"{student_name}同学学习状态良好，继续保持。"
        analysis = "该生学习数据表现正常，建议给予鼓励和肯定，帮助保持学习积极性。"
        suggestions = [
            "给予正面鼓励和肯定",
            "鼓励帮助其他同学",
            "关注长远发展建议"
        ]
        action_plan = "定期关注即可。"
        talking_points = f"{student_name}同学，你的学习状态不错，继续保持！有什么需要帮助的吗？"

    return {
        'summary': summary,
        'analysis': analysis,
        'suggestions': suggestions,
        'action_plan': action_plan,
        'talking_points': talking_points
    }


@csrf_exempt
@require_http_methods(["GET"])
def get_stored_comment(request, warning_id):
    """
    获取已存储的AI评语
    GET /ai/stored-comment/{warning_id}/
    """
    try:
        warning = WarningRecord.objects.select_related('student').get(id=warning_id)

        return JsonResponse({
            'code': 200,
            'data': {
                'student_id': warning.student_id,
                'student_name': warning.student.name,
                'student_no': warning.student.student_no,
                'risk_level': warning.risk_level,
                'student_comment': {
                    'comment': warning.ai_analysis or '',
                    'suggestions': warning.ai_suggestions or [],
                },
                'counselor_comment': counselor_comment_data(warning),
                'generated_at': warning.ai_generated_at.strftime('%Y-%m-%d %H:%M:%S') if warning.ai_generated_at else None,
                'sms_sent': warning.sms_sent,
                'sms_sent_at': warning.sms_sent_at.strftime('%Y-%m-%d %H:%M:%S') if warning.sms_sent_at else None
            }
        })
    except WarningRecord.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'message': '预警记录不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'获取评语失败: {str(e)}'
        }, status=500)


# 导入短信服务
from .sms_service import sms_service


@csrf_exempt
@require_http_methods(["POST"])
def send_sms_notification(request):
    """
    发送短信通知学生
    POST /ai/send-sms/
    {
        "warning_id": 1,
        "phone": "13800138000",  // 可选，默认使用学生注册手机号
        "message": "自定义消息内容"  // 可选，默认使用模板
    }
    """
    try:
        data = json.loads(request.body)
        warning_id = data.get('warning_id')
        custom_phone = data.get('phone')
        custom_message = data.get('message')

        if not warning_id:
            return JsonResponse({
                'code': 400,
                'message': '缺少warning_id参数'
            }, status=400)

        warning = WarningRecord.objects.select_related('student').get(id=warning_id)
        student = warning.student

        # 确定接收手机号
        phone = custom_phone or student.phone
        if not phone:
            return JsonResponse({
                'code': 400,
                'message': '学生未设置手机号，请手动输入'
            }, status=400)

        # 验证手机号格式
        import re
        if not re.match(r'^1[3-9]\d{9}$', phone):
            return JsonResponse({
                'code': 400,
                'message': '手机号格式不正确'
            }, status=400)

        # 构建短信内容
        if custom_message:
            message = custom_message
        else:
            summary = warning.counselor_comment or '辅导员查看了你的学习情况'
            if len(summary) > 40:
                summary = summary[:37] + '...'
            message = f"【学业预警】{student.name}同学您好，{summary}。请登录系统查看详情。"

        # 发送短信
        result = sms_service.send_sms(phone, message)

        # 获取正确的用户ID
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT id FROM users WHERE username = %s', [request.user.username])
            result_db = cursor.fetchone()
            user_id_in_users = result_db[0] if result_db else None

        # 记录到数据库
        from interventions.models import SMSNotification
        SMSNotification.objects.create(
            sender_id=user_id_in_users,
            student=student,
            phone=phone,
            warning=warning,
            content=message,
            status='sent' if result.get('success') else 'failed',
            error_message=result.get('error_message'),
            sent_at=timezone.now()
        )

        # 更新预警记录
        if result.get('success'):
            warning.sms_sent = True
            warning.sms_sent_at = timezone.now()
            warning.save()

        return JsonResponse({
            'code': 200,
            'message': '发送成功' if result.get('success') else '发送失败',
            'data': {
                'success': result.get('success'),
                'provider': result.get('provider', 'mock'),
                'message': result.get('message', '')
            }
        })

    except WarningRecord.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'message': '预警记录不存在'
        }, status=404)
    except Exception as e:
        print(f"发送短信失败: {e}")
        return JsonResponse({
            'code': 500,
            'message': f'发送失败: {str(e)}'
        }, status=500)
