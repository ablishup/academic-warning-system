#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 简化版
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api(name, method, endpoint, data=None):
    """测试API"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"[SKIP] {name}: 不支持的方法")
            return

        status = response.status_code
        if status == 200:
            print(f"[OK] {name}: 成功")
        elif status == 401:
            print(f"[AUTH] {name}: 需要登录 (正常)")
        elif status == 404:
            print(f"[404] {name}: 接口不存在")
        else:
            print(f"[ERR] {name}: 状态码 {status}")
    except Exception as e:
        print(f"[ERR] {name}: {str(e)}")

def main():
    print("="*50)
    print("学生端API测试")
    print("="*50)
    print()

    # 测试课程相关
    print("[课程相关]")
    test_api("学生课程列表", "GET", "/courses/student/")
    test_api("课程资源", "GET", "/courses/resources/?course_id=1")
    print()

    # 测试学习相关
    print("[学习相关]")
    test_api("学习活动列表", "GET", "/learning/activities/")
    test_api("学习活动统计", "GET", "/learning/activities/summary/")
    test_api("作业统计", "GET", "/learning/homework/stats/")
    test_api("考试统计", "GET", "/learning/exams/stats/")
    print()

    # 测试预警相关
    print("[预警相关]")
    test_api("预警记录", "GET", "/warnings/")
    test_api("预警统计", "GET", "/warnings/stats/")
    print()

    # 测试登录
    print("[认证]")
    test_api("用户登录", "POST", "/auth/login/", {"username": "test", "password": "test"})
    print()

    print("="*50)
    print("测试完成")
    print("="*50)

if __name__ == "__main__":
    main()
