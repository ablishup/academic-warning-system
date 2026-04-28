# Admin 前端 Mock 数据对接真实 API — 实施计划

## 一、理解确认

- **核心意图**：将 admin 前端 3 个页面中的模拟/硬编码数据替换为真实后端 API 调用。
  - `Classes.vue`：班级学生管理（列表、添加、移除）
  - `Courses.vue`：课程学生管理（列表、添加、移除）
  - `Counselors.vue`：院系筛选下拉（硬编码数组）
- **模糊点 / 待澄清**：
  1. 无额外模糊点。现有数据库模型（`Student.class_id`、`CourseEnrollment`、`Counselor.department`）已确认支持所需操作。
  2. 本次仅做数据读取与简单关联增删，不涉及复杂业务逻辑或数据库迁移。

---

## 二、改动计划

### 文件清单

| 文件路径 | 操作 | 改动摘要 |
|---|---|---|
| `back/backend/classes/views.py` | 修改 | 新增 `class_add_students_view`（批量添加学生到班级）、`class_remove_student_view`（从班级移除学生） |
| `back/backend/classes/urls.py` | 修改 | 注册 `POST <class_id>/add-students/` 和 `POST <class_id>/remove-student/` |
| `back/backend/courses/views.py` | 修改 | 新增 `course_students_view`（GET 课程学生列表）、`course_add_students_view`（批量选课）、`course_remove_student_view`（退选） |
| `back/backend/courses/urls.py` | 修改 | 注册 `GET/POST <course_id>/students/`、新增路由 |
| `back/backend/users/views.py` | 修改 | 新增 `department_list_view`（GET 返回 Counselor 表 distinct department） |
| `back/backend/users/urls.py` | 修改 | 注册 `GET departments/` |
| `forward/src/api/admin.js` | 修改 | 新增 `getClassStudents`、`addStudentsToClass`、`removeStudentFromClass`、`getCourseStudents`、`addStudentsToCourse`、`removeStudentFromCourse`、`getDepartmentList` |
| `forward/src/views/admin/Classes.vue` | 修改 | `manageStudents` 调真实 API 加载列表；`confirmAddStudents` 调批量添加；`removeStudentFromClass` 调移除；`availableStudentOptions` 加载无班级学生 |
| `forward/src/views/admin/Courses.vue` | 修改 | `manageStudents` 调真实 API 加载列表；`addStudents` 调批量选课；`removeStudent` 调退选；`studentOptions` 加载全部学生 |
| `forward/src/views/admin/Counselors.vue` | 修改 | `departments` 改为从 `getDepartmentList` 加载，onMounted 时请求 |

### 执行顺序
1. **后端先行**：按 `users → classes → courses` 顺序添加视图和路由（无模型变更，无需迁移）
2. **前端 API 层**：`forward/src/api/admin.js` 补充接口函数
3. **前端页面层**：`Classes.vue → Courses.vue → Counselors.vue` 依次替换 mock 逻辑
4. **验证**：前端编译检查 + 后端服务重启

---

## 三、风险评估

| 改动项 | 潜在风险 | 影响范围 | 验证/回滚建议 |
|---|---|---|---|
| 新增班级学生增删接口 | `Student` 表使用 `managed = False`，Django ORM 写操作依赖表结构匹配 | `classes/views.py`、数据库 `students` 表 | 接口仅更新 `class_id` 整数字段，风险极低；写完后用 Django shell 测试 `Student.objects.filter(class_id__isnull=True).count()` 确认查询正常 |
| 新增课程学生增删接口 | `CourseEnrollment` 同样 `managed = False`，需确保 `student_id`/`course_id` 字段正确 | `courses/views.py`、数据库 `course_enrollments` 表 | 新增记录时只需 `student_id` 和 `course_id` 两个整数字段，无额外约束风险；测试 `CourseEnrollment.objects.create(student_id=1, course_id=1)` |
| 新增院系列表接口 | `Counselor.department` 字段为空或重复值，distinct 查询可能返回 None | `users/views.py` | 过滤掉空字符串/None 即可 |
| 前端替换 mock 数据 | 若后端接口异常，弹窗可能显示空列表或报错 | `Classes.vue`、`Courses.vue`、`Counselors.vue` | 前端已有 `try/catch` 和 `ElMessage.error` 兜底；回滚只需还原前端文件 |

**总体风险评级**：低。本次仅新增独立 API 端点和前端调用，不修改现有接口签名或数据库结构。

---

## 四、等待确认

以上计划已汇总。如无疑问，请回复 **确认**，我将按顺序执行改动。
如有调整意见，请直接指出。
