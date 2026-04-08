# 数据处理脚本使用指南

本文档指导你如何使用数据处理脚本将超星公网数据处理后导入项目数据库。

## 文件说明

| 脚本 | 功能 | 输入 | 输出 |
|------|------|------|------|
| `clean_data.py` | 数据清洗 | 原始xls/xlsx | 清洗后的CSV |
| `import_to_mysql.py` | 导入数据库 | 清洗后的CSV | MySQL表数据 |
| `calculate_warnings.py` | 计算预警 | MySQL数据 | 预警记录 |

## 环境准备

### 1. 安装Python依赖

```bash
pip install pandas pymysql openpyxl requests
```

### 2. 创建MySQL数据库

```sql
CREATE DATABASE academic_warning_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 修改配置

编辑以下文件中的配置：

**`import_to_mysql.py`:**
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '你的密码',  # <-- 修改这里
    'database': 'academic_warning_system',
    'charset': 'utf8mb4'
}
```

**`calculate_warnings.py`:**
```python
DB_CONFIG = {
    # 同上
}

DEEPSEEK_CONFIG = {
    'api_key': '你的API Key',  # <-- 可选，不填则使用模板
    # ...
}
```

## 执行步骤

### 步骤1：数据清洗

```bash
python clean_data.py
```

功能：
- 筛选2-3门完整课程（学生数50-200人）
- 去除测试账号和重复数据
- 字段映射和类型转换
- 提取知识点（章节级）

输出文件（在 `../cleaned/` 目录）：
- `cleaned_persons.csv` - 学生数据
- `cleaned_courses.csv` - 课程数据
- `cleaned_classes.csv` - 班级数据
- `cleaned_knowledge_points.csv` - 知识点数据
- `cleaned_activity_logs.csv` - 活动日志
- `cleaned_work_answers.csv` - 作业答案
- `cleaned_exam_answers.csv` - 考试答案
- `selected_courses.json` - 选中的课程信息
- `cleaning_report.json` - 清洗统计报告

### 步骤2：创建数据库表

```bash
# 方式1：命令行
mysql -u root -p academic_warning_system < ../../backend/sql/chaoxing_schema.sql

# 方式2：使用MySQL客户端工具（如Navicat、DataGrip）导入SQL文件
```

### 步骤3：导入数据到MySQL

```bash
python import_to_mysql.py
```

导入顺序：
1. 专业（使用默认值）
2. 班级
3. 学生
4. 课程
5. 选课关系
6. 知识点（章节级）
7. 学习活动
8. 作业任务和提交
9. 考试任务和结果
10. 知识点掌握度（自动计算）

### 步骤4：计算预警指标

```bash
python calculate_warnings.py
```

功能：
- 计算每名学生-课程的综合得分
- 划分预警等级
- 生成AI建议（DeepSeek API + 模板兜底）
- 输出统计摘要

## 预警算法说明

### 指标权重

| 指标 | 权重 | 计算方式 |
|------|------|----------|
| 出勤率 | 30% | 活动参与次数 / 预期次数 |
| 学习进度 | 20% | 知识点掌握度平均值 |
| 作业成绩 | 30% | 作业平均分 × 0.7 + 提交率 × 0.3 |
| 考试成绩 | 20% | 考试平均分 |

### 预警等级

| 等级 | 分数范围 | 说明 |
|------|----------|------|
| 红色预警 | < 60 | 高危，需立即干预 |
| 橙色预警 | 60-75 | 警告，需重点关注 |
| 黄色预警 | 75-85 | 关注，需适当引导 |
| 正常 | ≥ 85 | 状态良好 |

## 数据映射关系

| 原始表（超星） | 项目表 | 说明 |
|----------------|--------|------|
| t_stat_person | students | 学生信息 |
| t_stat_course | courses | 课程信息 |
| t_stat_clazz | classes | 班级信息 |
| t_stat_course_person | course_enrollments | 选课关系 |
| t_stat_activity_log | learning_activities | 学习活动 |
| t_stat_work_answer | homework_submissions | 作业提交 |
| t_stat_exam_answer | exam_results | 考试结果 |
| chapters字段 | knowledge_points | 知识点（章节） |

## 常见问题

### Q: 数据清洗时内存不足？

**A:** 脚本已使用分批读取。如仍不足，修改 `clean_data.py`：

```python
# 减少目标课程数量
TARGET_COURSES = 2  # 改为1或2

# 或增大筛选条件，选择更少的课程
MIN_STUDENTS_PER_COURSE = 100  # 增大最小学生数
```

### Q: DeepSeek API调用失败或超时？

**A:** 脚本会自动使用模板兜底，无需担心。如需使用API：

1. 获取API Key：https://platform.deepseek.com/
2. 配置到 `calculate_warnings.py` 的 `DEEPSEEK_CONFIG`

### Q: 如何重新运行某个步骤？

**A:** 每个脚本都是独立的：

```bash
# 重新清洗（会覆盖cleaned目录）
python clean_data.py

# 重新导入（先清空表）
mysql -e "TRUNCATE TABLE warning_records; TRUNCATE TABLE learning_activities; ..."
python import_to_mysql.py

# 重新计算预警（会自动更新已有记录）
python calculate_warnings.py
```

### Q: 如何验证数据导入成功？

**A:** 在MySQL中执行：

```sql
-- 查看各表记录数
SELECT 'students' as table_name, COUNT(*) as count FROM students
UNION ALL SELECT 'courses', COUNT(*) FROM courses
UNION ALL SELECT 'knowledge_points', COUNT(*) FROM knowledge_points
UNION ALL SELECT 'warning_records', COUNT(*) FROM warning_records;

-- 查看预警统计
SELECT risk_level, COUNT(*) FROM warning_records GROUP BY risk_level;
```

### Q: 知识点如何关联？

**A:** 使用**简化方案**（章节即知识点）：

1. 从 `t_stat_course.xls` 中提取章节信息
2. 每个章节创建一条知识点记录
3. 作业/考试与课程的关联即视为与知识点关联

如需更细粒度的知识点，需要手动标注或NLP解析题目内容。

## 下一步

数据导入完成后，你可以：

1. 启动Django后端，配置MySQL数据库连接
2. 运行前端，查看预警数据展示
3. 根据预警记录，完善辅导员端的干预功能
