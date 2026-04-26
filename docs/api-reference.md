# 学业预警系统 - 后端API接口文档

## 接口基础信息

| 项目 | 说明 |
|------|------|
| Base URL | `http://localhost:8000/api` |
| 认证方式 | JWT Bearer Token + Django Session (CSRF) |
| 请求格式 | JSON / FormData (文件上传) |
| 响应格式 | `{code: 200, data: ..., message: ...}` 或 DRF分页格式 |

---

## 一、认证接口

### 1.1 用户登录

| 属性 | 值 |
|------|-----|
| URL | `/auth/login/` |
| Method | POST |
| 权限 | 公开 |

**请求参数**：
```json
{
  "username": "teacher1",
  "password": "123456"
}
```

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "teacher1",
      "role": "teacher",
      "name": "张老师"
    }
  },
  "message": "登录成功"
}
```

### 1.2 用户登出

| 属性 | 值 |
|------|-----|
| URL | `/auth/logout/` |
| Method | POST |
| 权限 | 需登录 |

### 1.3 获取当前用户信息

| 属性 | 值 |
|------|-----|
| URL | `/auth/profile/` |
| Method | GET |
| 权限 | 需登录 |

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "teacher1",
    "role": "teacher",
    "teacher_no": "T2021001",
    "department": "计算机学院",
    "title": "副教授"
  }
}
```

---

## 二、教师端接口

### 2.1 获取教师课程列表

| 属性 | 值 |
|------|-----|
| URL | `/teacher/courses/` |
| Method | GET |
| 权限 | 教师 |

**响应示例**：
```json
{
  "code": 200,
  "data": [
    {
      "id": 4,
      "name": "数据结构",
      "course_no": "CS004",
      "student_count": 118,
      "warning_count": 65
    }
  ]
}
```

**说明**：返回当前登录教师负责的所有课程，附带学生数和预警数统计。

---

### 2.2 获取课程学生列表

| 属性 | 值 |
|------|-----|
| URL | `/teacher/courses/{course_id}/students/` |
| Method | GET |
| 权限 | 教师 |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| class_id | int | 否 | 按班级筛选 |
| search | string | 否 | 按姓名/学号搜索 |

**响应示例**：
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "张三",
      "student_no": "20191101",
      "class_name": "2019级软件工程1班",
      "attendance_rate": 85.5,
      "homework_avg": 78.0,
      "exam_avg": 82.5,
      "composite_score": 81.2,
      "risk_level": "low"
    }
  ]
}
```

---

### 2.3 获取课程统计信息

| 属性 | 值 |
|------|-----|
| URL | `/teacher/courses/{course_id}/stats/` |
| Method | GET |
| 权限 | 教师 |

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "student_count": 118,
    "avg_attendance": 82.3,
    "avg_homework": 75.6,
    "avg_exam": 79.2,
    "warning_distribution": {
      "high": 15,
      "medium": 35,
      "low": 40,
      "normal": 28
    }
  }
}
```

---

### 2.4 获取学生学情摘要

| 属性 | 值 |
|------|-----|
| URL | `/teacher/students/{student_id}/summary/` |
| Method | GET |
| 权限 | 教师 |

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "student": {
      "id": 1,
      "name": "张三",
      "student_no": "20191101",
      "class_name": "2019级软件工程1班"
    },
    "learning_activities": [...],
    "homework_records": [...],
    "exam_records": [...],
    "warning_info": {
      "risk_level": "medium",
      "composite_score": 68.5
    }
  }
}
```

---

### 2.5 教学资源管理

#### 2.5.1 获取课程资源列表

| 属性 | 值 |
|------|-----|
| URL | `/courses/resources/` |
| Method | GET |
| 权限 | 教师 |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course_id | int | 否 | 按课程筛选 |
| resource_type | string | 否 | 按类型筛选（video/document/ppt/exercise） |

#### 2.5.2 上传资源

| 属性 | 值 |
|------|-----|
| URL | `/courses/resources/` |
| Method | POST |
| 权限 | 教师 |
| Content-Type | multipart/form-data |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 上传的文件 |
| course | int | 是 | 课程ID |
| resource_type | string | 是 | 资源类型 |
| description | string | 否 | 资源描述 |

#### 2.5.3 删除资源

| 属性 | 值 |
|------|-----|
| URL | `/courses/resources/{id}/` |
| Method | DELETE |
| 权限 | 教师 |

#### 2.5.4 下载资源

| 属性 | 值 |
|------|-----|
| URL | `/courses/resources/{id}/download/` |
| Method | GET |
| 权限 | 需登录 |

---

### 2.6 数据导入

#### 2.6.1 导入学习活动数据

| 属性 | 值 |
|------|-----|
| URL | `/import/activities/` |
| Method | POST |
| 权限 | 教师 |
| Content-Type | multipart/form-data |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | Excel文件 |
| course_id | int | 是 | 课程ID |

#### 2.6.2 导入作业数据

| 属性 | 值 |
|------|-----|
| URL | `/import/homework/` |
| Method | POST |
| 权限 | 教师 |

#### 2.6.3 导入考试数据

| 属性 | 值 |
|------|-----|
| URL | `/import/exams/` |
| Method | POST |
| 权限 | 教师 |

#### 2.6.4 获取导入模板

| 属性 | 值 |
|------|-----|
| URL | `/import/template/` |
| Method | GET |
| 权限 | 教师 |

---

## 三、辅导员端接口

### 3.1 获取预警列表（按学生汇总）

| 属性 | 值 |
|------|-----|
| URL | `/warnings/by-student/` |
| Method | GET |
| 权限 | 辅导员 |

**说明**：返回辅导员管理的所有学生，按风险等级排序。每个学生包含其所有课程的预警信息。

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "students": [
      {
        "student": {
          "id": 1,
          "name": "张三",
          "student_no": "20191101",
          "class_name": "2019级软件工程1班"
        },
        "warnings": [
          {
            "course_name": "数据结构",
            "risk_level": "high",
            "composite_score": 45.2
          }
        ],
        "highest_risk": "high",
        "risk_count": {"high": 1, "medium": 0, "low": 0},
        "avg_score": 45.2
      }
    ],
    "risk_summary": {
      "high": 5,
      "medium": 12,
      "low": 20,
      "normal": 63
    }
  }
}
```

---

### 3.2 获取预警记录列表

| 属性 | 值 |
|------|-----|
| URL | `/warnings/` |
| Method | GET |
| 权限 | 辅导员 |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| risk_level | string | 否 | 风险等级筛选（high/medium/low/normal） |
| status | string | 否 | 状态筛选（active/resolved/ignored） |
| student_id | int | 否 | 按学生筛选 |

---

### 3.3 获取预警详情

| 属性 | 值 |
|------|-----|
| URL | `/warnings/{id}/` |
| Method | GET |
| 权限 | 辅导员 |

---

### 3.4 处理预警

| 属性 | 值 |
|------|-----|
| URL | `/warnings/{id}/resolve/` |
| Method | POST |
| 权限 | 辅导员 |

**请求参数**：
```json
{
  "resolution_note": "已联系学生，安排了补习"
}
```

---

### 3.5 获取预警统计

| 属性 | 值 |
|------|-----|
| URL | `/warnings/stats/` |
| Method | GET |
| 权限 | 辅导员 |

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "total_warnings": 100,
    "high_risk_count": 15,
    "medium_risk_count": 35,
    "low_risk_count": 30,
    "normal_count": 20,
    "resolved_count": 25,
    "pending_count": 75
  }
}
```

---

### 3.6 触发预警计算

| 属性 | 值 |
|------|-----|
| URL | `/warnings/calculate/` |
| Method | POST |
| 权限 | 辅导员/管理员 |

**说明**：调用随机森林模型重新计算所有学生的风险等级并生成预警记录。

---

### 3.7 获取干预记录列表

| 属性 | 值 |
|------|-----|
| URL | `/interventions/` |
| Method | GET |
| 权限 | 辅导员 |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 干预类型筛选 |
| is_effective | bool | 否 | 效果筛选（true/false/null） |
| search | string | 否 | 搜索关键词 |

---

### 3.8 创建干预记录

| 属性 | 值 |
|------|-----|
| URL | `/interventions/create/` |
| Method | POST |
| 权限 | 辅导员 |

**请求参数**：
```json
{
  "student_id": 1,
  "warning_id": 5,
  "intervention_type": "talk",
  "intervention_time": "2025-04-10T14:30:00",
  "content": "与学生进行了面谈，了解了学习困难",
  "follow_up_plan": "安排每周一次的辅导"
}
```

---

### 3.9 更新干预记录

| 属性 | 值 |
|------|-----|
| URL | `/interventions/{id}/update/` |
| Method | PUT |
| 权限 | 辅导员 |

---

### 3.10 评估干预效果

| 属性 | 值 |
|------|-----|
| URL | `/interventions/{id}/evaluate/` |
| Method | POST |
| 权限 | 辅导员 |

**请求参数**：
```json
{
  "effectiveness": true,
  "evaluation_notes": "学生成绩有明显提升"
}
```

---

### 3.11 获取辅导员Dashboard统计

| 属性 | 值 |
|------|-----|
| URL | `/auth/counselor/dashboard-stats/` |
| Method | GET |
| 权限 | 辅导员 |

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "total_students": 119,
    "class_list": ["2019级软件工程1班", "2019级软件工程2班", "2019级计算机科学1班"],
    "high_risk_count": 15,
    "medium_risk_count": 35,
    "intervention_count": 25
  }
}
```

---

### 3.12 搜索学生

| 属性 | 值 |
|------|-----|
| URL | `/auth/search/` |
| Method | GET |
| 权限 | 辅导员 |

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| q | string | 是 | 搜索关键词（至少2个字符） |
| role | string | 否 | 角色筛选（默认student） |

---

## 四、公共接口

### 4.1 获取班级列表

| 属性 | 值 |
|------|-----|
| URL | `/classes/classes/` |
| Method | GET |
| 权限 | 需登录 |

### 4.2 获取班级学生列表

| 属性 | 值 |
|------|-----|
| URL | `/classes/classes/{id}/students/` |
| Method | GET |
| 权限 | 需登录 |

### 4.3 获取学生详情

| 属性 | 值 |
|------|-----|
| URL | `/classes/students/{id}/` |
| Method | GET |
| 权限 | 需登录 |

---

## 五、管理员接口

### 5.1 辅导员管理

#### 5.1.1 获取辅导员列表

| 属性 | 值 |
|------|-----|
| URL | `/auth/counselors/` |
| Method | GET |
| 权限 | 管理员 |

#### 5.1.2 获取辅导员管理班级

| 属性 | 值 |
|------|-----|
| URL | `/auth/counselors/{id}/classes/` |
| Method | GET |
| 权限 | 管理员 |

#### 5.1.3 分配班级给辅导员

| 属性 | 值 |
|------|-----|
| URL | `/auth/counselors/{id}/assign-classes/` |
| Method | POST |
| 权限 | 管理员 |

**请求参数**：
```json
{
  "class_ids": [1, 2, 3]
}
```

#### 5.1.4 移除辅导员的班级

| 属性 | 值 |
|------|-----|
| URL | `/auth/counselors/{id}/remove-class/` |
| Method | POST |
| 权限 | 管理员 |

**请求参数**：
```json
{
  "class_id": 1
}
```

#### 5.1.5 获取未分配班级

| 属性 | 值 |
|------|-----|
| URL | `/auth/available-classes/` |
| Method | GET |
| 权限 | 管理员 |

---

## 六、接口权限总结

| 接口 | 学生 | 教师 | 辅导员 | 管理员 |
|------|------|------|--------|--------|
| `/auth/*` | ✓ | ✓ | ✓ | ✓ |
| `/teacher/*` | ✗ | ✓ | ✗ | ✗ |
| `/courses/resources/*` | ✓(下载) | ✓(完整) | ✗ | ✓ |
| `/import/*` | ✗ | ✓ | ✗ | ✓ |
| `/warnings/*` | ✗ | ✗ | ✓ | ✓ |
| `/interventions/*` | ✗ | ✗ | ✓ | ✗ |
| `/classes/*` | ✓(只读) | ✓(只读) | ✓(只读) | ✓(完整) |
| `/admin/*` | ✗ | ✗ | ✗ | ✓ |
