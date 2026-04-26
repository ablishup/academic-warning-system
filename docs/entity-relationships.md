# 学业预警系统 - 实体关系说明

## 一、核心实体概览

本系统包含以下核心实体：

| 实体 | 说明 | 对应数据库表 |
|------|------|-------------|
| User | Django内置认证用户 | auth_user |
| Teacher | 教师信息 | teachers |
| Counselor | 辅导员信息 | counselors |
| Student | 学生信息 | students |
| Class | 班级信息 | classes |
| Major | 专业信息 | majors |
| Course | 课程信息 | courses |
| CourseEnrollment | 选课关系 | course_enrollments |
| StudentCourseScore | 学生课程得分 | student_course_scores |
| WarningRecord | 预警记录 | warning_records |
| InterventionRecord | 干预记录 | intervention_records |

---

## 二、用户体系关系

### 2.1 User - Teacher - Counselor 关系

```
Django auth_user
    ├── Teacher (1:1)  via user.teacher_profile
    │   └── teacher_no, department, title, phone, office
    ├── Counselor (1:1) via user.counselor_profile
    │   └── employee_no, department, phone, office
    └── UserProfile (1:1) via user.profile
        └── employee_no, department, phone
```

**关键说明**：
- `Teacher` 和 `Counselor` 通过 `OneToOneField` 扩展 `auth_user` 表
- 前端登录后，`userInfo` 存储在 localStorage，包含 `role` 字段（student/teacher/counselor/admin）
- 辅导员管理班级的依据是 `Class.counselor_id = User.id`（注意：是 User 的主键，不是 Counselor 表的主键）

### 2.2 账号与角色的对应关系

| 角色 | 前端路由 | 布局组件 | 后端标识 |
|------|---------|---------|---------|
| 学生 | /student/* | Layout.vue | role = "student" |
| 教师 | /teacher/* | TeacherLayout.vue | role = "teacher" |
| 辅导员 | /counselor/* | CounselorLayout.vue | role = "counselor" |
| 管理员 | /admin/* | AdminLayout.vue | role = "admin" |

---

## 三、学生-班级-年级关系

### 3.1 数据模型

```
Major（专业）
    └── Class（班级）
        ├── name: 班级名称（如 "2019级软件工程1班"）
        ├── grade: 年级代码（如 "2019", "2020", "2021"）
        ├── major_id: 关联专业
        ├── counselor_id: 关联辅导员（User.id）
        └── has many ► Student（通过 class_id）

Student（学生）
    ├── student_no: 学号（如 "20191101"）
    ├── name: 姓名
    ├── class_id: 班级ID
    ├── major_id: 专业ID
    ├── enrollment_year: 入学年份
    ├── raw_id: 原始系统ID（用于数据导入映射）
    └── belongs to ► Class
```

### 3.2 年级-班级-学生关系链

```
年级(Grade)
    └── 班级(Class)
        ├── 学生1(Student)
        ├── 学生2(Student)
        └── 学生N(Student)
```

**当前系统数据**：
- 3个年级：2019级、2020级、2021级
- 9个班级：每个年级3个班（软件工程1班/2班、计算机科学1班）
- 约354名学生

### 3.3 辅导员-班级-学生关系

```
辅导员(Counselor)
    └── 管理多个班级(Class via counselor_id)
        └── 每个班级有多个学生(Student via class_id)
```

**辅导员-年级分配规则**：
| 辅导员账号 | 管理年级 |
|-----------|---------|
| counselor | 2019级 |
| counselor2 | 2020级 |
| counselor3 | 2021级 |

---

## 四、教师-课程-学生关系

### 4.1 数据模型

```
Teacher
    └── 教授多门 Course（通过 Course.teacher_id）
        └── 每门 Course 有多个学生（通过 CourseEnrollment）
            └── Student
```

### 4.2 课程分配规则

当前系统有6门课程，分配给3位教师：

| 教师 | 课程 |
|------|------|
| teacher1 | 数据结构、软件工程 |
| teacher2 | 操作系统、人工智能导论 |
| teacher3 | 计算机网络、数据库原理 |

### 4.3 选课关系

```
年级 → 课程分配
├── 2021级 → 数据结构 + 计算机网络
├── 2020级 → 操作系统 + 数据库原理
└── 2019级 → 软件工程 + 人工智能导论
```

**CourseEnrollment 表**：
- `student_id` + `course_id` 唯一索引
- `status` 字段表示选课状态（1=正常）

---

## 五、预警体系关系

### 5.1 预警数据流

```
LearningActivity（学习活动）
    + HomeworkSubmission（作业提交）
    + ExamResult（考试结果）
    │
    ▼
StudentCourseScore（聚合得分表）
    ├── attendance_rate: 出勤率
    ├── video_progress: 视频进度
    ├── homework_avg: 作业平均分
    ├── homework_submit_rate: 作业提交率
    ├── exam_avg: 考试平均分
    └── knowledge_mastery: 知识掌握度
    │
    ▼
WarningPredictor（随机森林模型）
    │
    ▼
WarningRecord（预警记录）
    ├── risk_level: high/medium/low/normal
    ├── composite_score: 综合得分
    ├── attendance_score: 出勤得分
    ├── progress_score: 进度得分
    ├── homework_score: 作业得分
    └── exam_score: 考试得分
```

### 5.2 风险等级判定规则

| 综合得分 | 风险等级 | 颜色 |
|---------|---------|------|
| < 60 | high（高危） | 红色 |
| 60 - 75 | medium（中等） | 橙色 |
| 75 - 85 | low（低危） | 黄色 |
| >= 85 | normal（正常） | 绿色 |

### 5.3 综合得分计算权重

```
综合得分 = attendance_rate * 0.30
        + video_progress * 0.20
        + homework_avg * 0.30
        + exam_avg * 0.20
```

---

## 六、干预体系关系

### 6.1 干预数据流

```
WarningRecord（预警记录）
    │
    ├── 触发 InterventionRecord（干预记录）
    │   ├── intervention_type: 干预类型
    │   ├── content: 干预内容
    │   ├── intervention_time: 干预时间
    │   └── is_effective: 干预效果
    │
    └── 预警状态变更
        ├── active: 待处理
        ├── resolved: 已解决
        └── ignored: 已忽略
```

### 6.2 干预类型

| 类型 | 说明 |
|------|------|
| talk | 谈话辅导 |
| academic | 学业帮扶 |
| psychological | 心理疏导 |
| family | 家校联系 |
| other | 其他 |

---

## 七、完整关系图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户认证层                             │
│  ┌─────────┐    ┌──────────┐    ┌───────────┐              │
│  │  User   │◄──►│ Teacher  │    │ Counselor │              │
│  │(auth)   │    │(1:1扩展) │    │(1:1扩展)  │              │
│  └────┬────┘    └──────────┘    └─────┬─────┘              │
│       │                                │                     │
│       │ teacher_id                     │ counselor_id        │
│       ▼                                ▼                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      教学管理层                       │   │
│  │  ┌─────────┐    ┌──────────────┐    ┌───────────┐  │   │
│  │  │ Course  │◄───│ CourseEnrollment│───►│ Student   │  │   │
│  │  │         │    │              │    │           │  │   │
│  │  └────┬────┘    └──────────────┘    └─────┬─────┘  │   │
│  │       │                                   │         │   │
│  │       │ class_id                          │         │   │
│  │       ▼                                   │         │   │
│  │  ┌─────────┐                              │         │   │
│  │  │  Class  │◄─────────────────────────────┘         │   │
│  │  │         │                                       │   │
│  │  └────┬────┘                                       │   │
│  │       │ major_id                                    │   │
│  │       ▼                                             │   │
│  │  ┌─────────┐                                        │   │
│  │  │  Major  │                                        │   │
│  │  └─────────┘                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                      预警分析层                       │   │
│  │  ┌─────────────────┐    ┌───────────────────┐       │   │
│  │  │ StudentCourseScore│───►│  WarningRecord    │       │   │
│  │  │   (聚合数据)     │    │  (预警记录)        │       │   │
│  │  └─────────────────┘    └─────────┬───────────┘       │   │
│  │                                    │                   │   │
│  │                                    ▼                   │   │
│  │                           ┌───────────────────┐       │   │
│  │                           │ InterventionRecord│       │   │
│  │                           │   (干预记录)       │       │   │
│  │                           └───────────────────┘       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 八、关键字段映射说明

### 8.1 外键关联方式

由于 `Class` 和 `Student` 表设置为 `managed = False`（遗留/外部表），系统使用 **IntegerField** 存储关联ID，而非 Django 的 ForeignKey。

| 表 | 字段 | 关联目标 | 关联方式 |
|---|------|---------|---------|
| classes | counselor_id | auth_user.id | IntegerField |
| students | class_id | classes.id | IntegerField |
| students | major_id | majors.id | IntegerField |
| courses | teacher_id | teachers.user_id | IntegerField |
| course_enrollments | student_id | students.id | IntegerField |
| course_enrollments | course_id | courses.id | IntegerField |

### 8.2 辅导员查询学生的逻辑

```python
# 后端获取辅导员管理的学生ID列表
def _get_counselor_student_ids(user):
    # 1. 获取辅导员管理的班级
    managed_classes = Class.objects.filter(counselor_id=user.id)
    # 2. 获取这些班级的学生
    student_ids = Student.objects.filter(
        class_id__in=managed_classes.values_list('id', flat=True)
    ).values_list('id', flat=True)
    return student_ids
```

### 8.3 教师查询课程学生的逻辑

```python
# 后端获取教师的课程列表
def get_teacher_courses(user):
    teacher = user.teacher_profile
    courses = Course.objects.filter(teacher_id=teacher.id)
    return courses

# 获取课程下的学生
def get_course_students(course_id):
    enrollments = CourseEnrollment.objects.filter(course_id=course_id)
    student_ids = enrollments.values_list('student_id', flat=True)
    students = Student.objects.filter(id__in=student_ids)
    return students
```
