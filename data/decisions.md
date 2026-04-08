# 数据处理决策记录

> 记录数据集处理过程中的关键决策，用于毕设文档追溯

## 决策1：数据源选择

**日期**：2026-04-07  
**决策**：选用**公网数据**（地大数据集）  
**原因**：
- 雨课堂数据文件过大（单文件17M+），处理耗时
- 公网数据字段更完整，与项目需求匹配度更高
- 公网数据包含课程、班级、作业、考试等完整教学闭环

**数据文件清单**（共17个主表 + 7个日志CSV）：

| 文件名 | 说明 | 项目映射 |
|--------|------|----------|
| t_stat_person.xls | 学生信息表 | users_user |
| t_stat_course.xls | 课程信息表 | courses_course |
| t_stat_clazz.xls | 班级信息表 | courses_class |
| t_stat_course_person.xls | 学生选课关系 | 中间表 |
| t_stat_activity_log.xls | 活动日志（1.5M） | attendance_records |
| t_stat_work_answer.xls | 作业答案（1.7M） | homework_submissions |
| t_stat_exam_answer.xls | 考试答案 | exam_results |
| t_stat_student_score.xls | 最终成绩 | student_scores |
| t_stat_job_finish.xls | 任务完成情况 | learning_tasks |
| t_stat_question_bank.xls | 题库 | questions |
| t_stat_work_library.xls | 作业库 | homework_assignments |
| t_stat_exam_library.xls | 考试库 | exam_assignments |
| t_stat_bbs_log.xls | 论坛日志 | forum_activities |
| t_stat_widget_log.xls | 组件日志 | widget_activities |
| t_stat_course_job.xls | 课程作业关系 | 中间表 |
| t_stat_work_relation.xls | 作业关联 | 中间表 |
| t_stat_exam_relation.xls | 考试关联 | 中间表 |
| t_stat_log&t_stat_login/*.csv | 登录日志（7个CSV） | login_logs |

---

## 决策2：知识点关联方案

**日期**：2026-04-07  
**决策**：采用**简化方案** - 以"课程章节"作为知识点  
**原因**：
- 毕设时间紧迫（距答辩6周）
- 完整知识点解析需要NLP处理，技术复杂度较高
- 章节级粒度已能满足预警系统的演示需求

**实现方式**：
- 从 `t_stat_course.xls` 中提取章节信息
- 每个章节自动创建对应的知识点记录
- 作业/考试与章节关联即视为与知识点关联

---

## 决策3：预警算法权重

**日期**：2026-04-07  
**决策**：采用加权评分模型  
**权重分配**：
- 出勤率（视频观看、活动参与）：30%
- 学习进度（任务完成率）：20%
- 作业成绩：30%
- 考试成绩：20%

**预警等级**：
- 红色预警（高危）：综合评分 < 60
- 橙色预警（警告）：60 ≤ 综合评分 < 75
- 黄色预警（关注）：75 ≤ 综合评分 < 85
- 正常：综合评分 ≥ 85

---

## 决策4：数据清洗策略

**日期**：2026-04-07  
**决策**：
1. 筛选2-3门完整课程（学生数50-200人）
2. 去除测试账号（用户名含test、admin、教师账号）
3. 去除重复记录
4. 保留2021年全年数据（公网数据时间范围）

---

## 决策5：AI集成方案

**日期**：2026-04-07  
**决策**：DeepSeek API + 模板兜底机制  
**配置**：
- 模型：deepseek-chat
- 成本：¥2/百万tokens
- 超时：5秒
- 失败时 fallback 到本地模板

---

## 后续可优化点（如果时间允许）

1. **知识点细化**：从作业/考试题目中提取关键词，建立细粒度知识点
2. **时序分析**：增加学习行为的时间序列分析
3. **更多数据源**：整合雨课堂数据增加样本量
