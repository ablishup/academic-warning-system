# Git 提交记录

**日期**: 2026-04-08

---

## 提交信息

**Commit**: `5256130`  
**分支**: master  
**消息**: Initial commit: Student Academic Warning System

### 包含内容

- **前端**: Vue 3 + Element Plus (forward/)
- **后端**: Django 5.0 + DRF (back/backend/)
- **数据库**: MySQL schema + 数据导入脚本 (data/)
- **文档**: 进度记录、API文档、架构设计

### 文件统计
- 148个文件
- 7,755行插入

---

## 分支结构

```
master (5256130)  ← 稳定版本
  │
  └── dev/warning-api  ← 当前开发分支
```

### 分支说明

| 分支 | 用途 | 状态 |
|-----|------|------|
| master | 稳定版本，可运行的代码 | 已创建 |
| dev/warning-api | 预警API开发 | 当前分支 |

---

## 常用Git命令

```bash
# 查看状态
git status

# 查看提交历史
git log --oneline --graph

# 切换分支
git checkout master
git checkout dev/warning-api

# 拉取最新代码（如果有远程仓库）
git pull origin master

# 推送分支
git push -u origin master
git push -u origin dev/warning-api

# 合并分支
git checkout master
git merge dev/warning-api
```

---

## 下一步开发

在 `dev/warning-api` 分支上继续：
1. 实现预警API
2. 实现预警计算算法
3. 完成后合并回master
