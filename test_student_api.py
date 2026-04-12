#!/usr/bin/env python3
"""
学生端API测试脚本
测试学生端相关接口是否正常工作
"""

import requests
import json

# 配置
BASE_URL = "http://localhost:8000/api"

def test_api(name, method, endpoint, data=None, token=None):
    """测试单个API"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=10)
        else:
            print(f"❌ {name}: 不支持的HTTP方法 {method}")
            return None

        if response.status_code == 200:
            print(f"✅ {name}: 成功")
            return response.json()
        elif response.status_code == 401:
            print(f"⚠️  {name}: 需要登录 (401)")
        elif response.status_code == 404:
            print(f"⚠️  {name}: 接口不存在 (404)")
        else:
            print(f"❌ {name}: 失败 ({response.status_code}) - {response.text[:100]}")
        return None
    except Exception as e:
        print(f"❌ {name}: 异常 - {str(e)}")
        return None

def main():
    print("="*60)
    print("学生端API测试")
    print("="*60)
    print()

    # 测试登录接口（不需要token）
    print("【1. 认证相关】")
    login_result = test_api(
        "用户登录",
        "POST",
        "/auth/login/",
        {"username": "student1", "password": "123456"}
    )

    token = None
    if login_result and login_result.get("code") == 200:
        token = login_result.get("data", {}).get("token")
        print(f"   获取到Token: {token[:20]}..." if token else "   未获取到Token")
    print()

    # 测试课程相关接口
    print("【2. 课程相关】")
    test_api("学生课程列表", "GET", "/courses/student/", token=token)
    test_api("课程详情", "GET", "/courses/1/", token=token)
    test_api("课程知识点", "GET", "/courses/1/knowledge-points/", token=token)
    print()

    # 测试资源相关接口
    print("【3. 资源相关】")
    test_api("课程资源列表", "GET", "/courses/resources/?course_id=1", token=token)
    print()

    # 测试学习相关接口
    print("【4. 学习相关】")
    test_api("学习活动列表", "GET", "/learning/activities/", token=token)
    test_api("学习活动统计", "GET", "/learning/activities/summary/", token=token)
    test_api("作业统计", "GET", "/learning/homework/stats/", token=token)
    test_api("作业提交记录", "GET", "/learning/homework/submissions/", token=token)
    test_api("考试统计", "GET", "/learning/exams/stats/", token=token)
    test_api("考试结果", "GET", "/learning/exams/results/", token=token)
    test_api("课程学习统计", "GET", "/learning/course-stats/?course_id=1", token=token)
    print()

    # 测试预警相关接口
    print("【5. 预警相关】")
    test_api("预警记录列表", "GET", "/warnings/", token=token)
    test_api("预警统计", "GET", "/warnings/stats/", token=token)
    test_api("学生课程得分", "GET", "/warnings/scores/", token=token)
    print()

    # 测试记录学习活动
    print("【6. 记录学习活动】")
    test_api(
        "记录视频学习",
        "POST",
        "/learning/record/",
        {
            "course_id": 1,
            "activity_type": "video",
            "activity_name": "测试视频",
            "duration": 60,
            "progress": 50.0
        },
        token=token
    )
    print()

    print("="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
