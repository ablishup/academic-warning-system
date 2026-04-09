# Django REST API 开发进度记录

**日期**: 2026-04-10  
**状态**: 学生端前端API对接完成

---

## 2026-04-10 更新 - 学生端API对接

### 已完成内容

#### 1. 前端API模块创建
- **文件**: `forward/src/api/request.js`
  - 创建axios请求实例
  - 配置请求/响应拦截器
  - 统一错误处理和token管理

- **文件**: `forward/src/api/student.js`
  - 封装学生端所有API接口
  - 包含学情分析、课程、资源、预警等接口
  - 提供学情汇总接口整合多个数据源

- **文件**: `forward/src/api/index.js`
  - API模块统一入口

#### 2. 学生端页面API对接

##### Courses.vue (课程列表页)
- 对接 `GET /api/courses/student/` 获取学生课程列表
- 对接 `GET /api/courses/resources/` 获取课程资源统计
- 实现课程搜索和筛选功能
- 动态加载课程资源数量（视频/文档/习题）

##### CourseResources.vue (课程资源页)
- 对接 `GET /api/courses/resources/` 获取课程资源列表
- 对接 `POST /api/learning/record/` 记录视频学习进度
- 实现视频播放弹窗和进度上报（每30秒记录一次）
- 实现资源下载功能
- 支持视频/文档/习题分类展示

##### Analysis.vue (学情分析页)
- 对接预警、作业、考试、学习活动等多个API
- 实现成绩趋势图（ECharts）
- 动态显示AI学业预测结果
- 展示学习行为分析（出勤率、作业成绩、提交率、学习时长）

---

## 历史记录

### 2026-04-08 基础API搭建完成

---

## 已完成内容

### 1. 安装配置DRF ✅

```bash
pip install djangorestframework django-cors-headers
```

**settings.py配置**:
- 添加 `rest_framework` 和 `corsheaders` 到 INSTALLED_APPS
- 添加 CORS中间件
- 配置REST Framework分页和认证
- 启用CORS跨域支持（开发环境）

### 2. 创建的应用和API ✅

#### users应用 - 用户认证API
| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/auth/login/` | POST | 用户登录 |
| `/api/auth/logout/` | POST | 用户登出 |
| `/api/auth/current/` | GET | 获取当前用户信息 |
| `/api/auth/list/` | GET | 获取用户列表 |

#### courses应用 - 课程API
| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/courses/` | GET | 获取课程列表 |
| `/api/courses/<id>/` | GET | 获取课程详情 |
| `/api/courses/<id>/knowledge-points/` | GET | 获取课程知识点 |
| `/api/courses/teacher/` | GET | 获取教师课程 |
| `/api/courses/student/` | GET | 获取学生课程 |

#### classes应用 - 学生和班级API
| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/classes/students/` | GET | 获取学生列表（支持搜索） |
| `/api/classes/students/search/?q=keyword` | GET | 搜索学生 |
| `/api/classes/students/<id>/` | GET | 获取学生详情 |
| `/api/classes/classes/` | GET | 获取班级列表 |
| `/api/classes/classes/<id>/students/` | GET | 获取班级学生 |

### 3. 数据模型映射 ✅

已创建与MySQL表对应的模型（managed=False）:
- `courses/models.py`: Course, CourseEnrollment, KnowledgePoint
- `classes/models.py`: Student, Class, Major

### 4. 序列化器 ✅

创建了以下序列化器:
- `UserSerializer`, `LoginSerializer`
- `CourseSerializer`, `KnowledgePointSerializer`
- `StudentSerializer`, `ClassSerializer`

---

## API响应格式

统一响应格式:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {...}
}
```

错误响应:
```json
{
  "code": 401,
  "message": "认证失败"
}
```

---

## 待办事项

### 高优先级
1. **实现预警API**
   - GET `/api/warnings/` - 获取预警列表
   - POST `/api/warnings/calculate/` - 计算预警
   - GET `/api/warnings/<id>/` - 获取预警详情

2. **实现学习数据API**
   - 学习活动记录查询
   - 作业成绩查询
   - 考试成绩查询

3. **实现干预API**
   - 创建干预记录
   - 查询干预记录

### 中优先级
4. **JWT认证**
   - 替换Session认证为JWT Token认证

5. **数据导入API**
   - 上传Excel文件导入学习数据

---

## 测试命令

```bash
# 启动服务器
cd back/backend
python manage.py runserver

# 测试API（需要登录获取session）
curl http://localhost:8000/api/courses/
curl http://localhost:8000/api/classes/students/
```

---

## 下一步计划

继续开发预警相关的API和算法。
