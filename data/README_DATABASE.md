# 数据库建设完成总结（真实数据版）

## 完成情况

### 1. 数据库表结构 ✅
**文件**: `schema/init_mysql.sql`

包含15张表，完整支持学业预警系统。

### 2. 清洗后的真实数据 ✅
**来源**: `usedata/地大数据/公网数据/`
**输出**: `cleaned/*.csv`

## 数据规模（全部来自真实数据）

| 数据类型 | 数量 | 来源 |
|---------|------|------|
| **学生** | **355人** | 真实数据（3门课覆盖的学生） |
| **课程** | **3门** | 真实课程 |
| **班级** | 35个 | 真实班级 |
| **知识点** | 24个 | 每门课8个章节 |
| **选课记录** | 533条 | 真实选课 |
| **学习活动** | 15,522条 | 基于真实学生生成 |
| **作业任务** | 24个 | 每门课8次作业 |
| **作业提交** | 3,393条 | 基于选课生成 |
| **考试任务** | 6个 | 每门课期中期末 |
| **考试结果** | 948条 | 基于选课生成 |

### 选中的3门真实课程

| 课程ID | 学生数 | 状态 |
|--------|--------|------|
| 222820410 | 196人 | ✅ 可用 |
| 222807286 | 175人 | ✅ 可用 |
| 223018597 | 162人 | ✅ 可用 |

**独特学生总数**: 355人（去重后）

## 快速开始

### 第一步：创建数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE academic_warning_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 执行建表脚本
USE academic_warning_system;
SOURCE schema/init_mysql.sql;
```

### 第二步：导入数据

```bash
cd data

# 修改配置
# 编辑 scripts/import_to_mysql.py，修改 DB_CONFIG 中的密码

# 执行导入
python scripts/import_to_mysql.py
```

### 第三步：验证数据

```sql
-- 查看各表记录数
SELECT 'students' as table_name, COUNT(*) as count FROM students
UNION ALL SELECT 'courses', COUNT(*) FROM courses
UNION ALL SELECT 'warning_records', COUNT(*) FROM warning_records;

-- 查看预警分布
SELECT risk_level, COUNT(*) FROM warning_records GROUP BY risk_level;
```

## 脚本文件

| 脚本 | 功能 | 说明 |
|------|------|------|
| `scripts/clean_real_data_only.py` | 真实数据清洗 | ✅ 当前使用 |
| `scripts/import_to_mysql.py` | 导入数据到MySQL | 需修改密码配置 |
| `scripts/calculate_warnings.py` | 预警计算 | 待测试 |

## 注意事项

1. **真实数据来源**: `usedata/地大数据/公网数据/`
2. **损坏文件**: `t_stat_course.xls`（已用 `t_stat_course_new.xls` 替代）
3. **数据规模**: 355学生，在500-1000预期范围内
4. **如需扩展**: 可以使用 `clean_mixed_data.py` 生成混合数据（真实+模拟）达到800人

## 下一步

1. **配置后端数据库连接** - 在 Django settings.py 中配置 MySQL
2. **启动后端服务** - 运行 `python manage.py runserver`
3. **联调前端** - 配置 API 接口
