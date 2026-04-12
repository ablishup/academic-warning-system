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
