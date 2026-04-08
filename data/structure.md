  project/
  ├── data/                           # 数据集目录（新建）
  │   ├── schema/                     # 数据库表结构
  │   │   └── init_mysql.sql          # MySQL建表脚本
  │   │
  │   ├── raw/                        # 原始数据文件（Excel/CSV）
  │   │   ├── students.xlsx           # 学生基本信息
  │   │   ├── courses.xlsx            # 课程信息
  │   │   ├── knowledge_points.xlsx   # 知识点体系
  │   │   ├── attendance.xlsx         # 考勤数据
  │   │   ├── video_progress.xlsx     # 视频学习进度
  │   │   ├── homework.xlsx           # 作业成绩（含知识点关联）
  │   │   └── exam_scores.xlsx        # 考试成绩（可选）
  │   │
  │   └── scripts/                    # 数据生成/导入脚本
  │       ├── generate_mock_data.py   # 生成模拟数据
  │       ├── export_to_excel.py      # 导出Excel模板
  │       └── import_to_mysql.py      # 导入MySQL脚本
  │
  └── back/backend/                   # Django后端
      └── courses/models.py           # 知识点关联模型