# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

这是一个学生学业预警系统（毕业设计项目），用于收集多维度学习数据（考勤、视频观看、作业成绩等），通过算法模型预测学生期末挂科风险，为教师、辅导员提供早期干预依据。

## Project Structure

项目分为前端和后端两个目录：

- `forward/` - Vue 3 前端项目
- `back/backend/` - Django 后端项目

### 前端 (forward/)

基于 Vue CLI 5 + Vue 3 + Element Plus 构建：

```
src/
  api/           # API 接口（待实现）
  assets/        # 静态资源
  components/    # 公共组件（Layout.vue 为主布局）
  router/        # 路由配置
  stores/        # Pinia 状态管理
  styles/        # 全局样式
  views/         # 页面视图
    admin/       # 管理员端：用户管理、课程管理、班级管理
    teacher/     # 教师端：课程监控、上传数据、教学资源
    counselor/   # 辅导员端：学生学情总览、预警与干预记录
    student/     # 学生端：学情分析、课程资源、个人信息
    login/       # 登录页
```

### 后端 (back/backend/)

基于 Django 5.0 + SQLite 构建，应用模块：

- `auth/` - 用户认证
- `users/` - 用户管理
- `courses/` - 课程管理
- `classes/` - 班级管理
- `attendances/` - 考勤数据
- `scores/` - 成绩数据
- `resources/` - 教学资源
- `student_analysis/` - 学生学情分析
- `school_analysis/` - 全校学情分析
- `interventions/` - 干预记录
- `intervention_system/` - 干预系统
- `student_interventions/` - 学生干预
- `warning_system/` - 预警系统
- `student_warnings/` - 学生预警

## Commands

### 前端开发 (forward/)

```bash
cd forward
npm install
npm run serve      # 开发服务器，热重载
npm run build      # 生产构建
```

### 后端开发 (back/backend/)

```bash
cd back/backend
python manage.py runserver           # 启动开发服务器
python manage.py makemigrations      # 生成迁移文件
python manage.py migrate             # 执行数据库迁移
python manage.py createsuperuser     # 创建管理员账号
python manage.py shell               # Django shell
```

## Architecture Notes

### 前端路由结构

- `/login` - 登录页
- `/admin/*` - 管理员端（用户/课程/班级管理）
- `/teacher/*` - 教师端（课程监控、数据上传）
- `/counselor/*` - 辅导员端（学情总览、预警干预）
- `/student/*` - 学生端（个人学情、课程资源）

路由守卫已配置：非登录页需要 token 才能访问。

### 技术栈

**前端：**
- Vue 3 + Vue Router 4
- Element Plus UI 框架
- Pinia 状态管理
- Axios HTTP 客户端（待配置）
- ECharts 图表库
- xlsx Excel 处理

**后端：**
- Django 5.0
- Django REST Framework（待添加）
- SQLite 数据库

### 数据流规划

1. 教师上传学习数据（考勤、视频观看、作业成绩）
2. 系统整合多维度数据进行融合分析
3. 算法模型预测学生挂科风险等级
4. 辅导员接收预警并实施干预
5. 学生查看个人学情分析和建议

## Development Notes

- 后端 API 尚未实现，前端使用 mock 数据
- 需实现数据导入功能（支持学习通、智慧树等平台格式）
- 核心算法：随机森林 等集成学习模型预测期末成绩
- 风险等级划分：75-60分中等风险，60分以下高风险
- 辅导员端是系统核心，需重点完善预警和干预功能
