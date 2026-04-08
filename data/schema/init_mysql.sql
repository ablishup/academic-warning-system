-- 学业预警系统数据库初始化脚本
-- 创建时间: 2026-04-07
-- 数据库: academic_warning_system

-- 设置字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 基础数据表
-- ============================================

-- 专业表
DROP TABLE IF EXISTS `majors`;
CREATE TABLE `majors` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '专业名称',
    `code` VARCHAR(20) UNIQUE COMMENT '专业代码',
    `department` VARCHAR(100) COMMENT '所属院系',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='专业信息表';

-- 班级表
DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL COMMENT '班级名称',
    `grade` VARCHAR(10) COMMENT '年级(如: 2021)',
    `major_id` INT UNSIGNED COMMENT '所属专业',
    `counselor_id` INT UNSIGNED COMMENT '辅导员ID',
    `student_count` INT DEFAULT 0 COMMENT '学生人数',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`major_id`) REFERENCES `majors`(`id`) ON DELETE SET NULL,
    INDEX `idx_grade` (`grade`),
    INDEX `idx_major` (`major_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级信息表';

-- 学生表
DROP TABLE IF EXISTS `students`;
CREATE TABLE `students` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_no` VARCHAR(20) UNIQUE NOT NULL COMMENT '学号',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `gender` TINYINT DEFAULT 0 COMMENT '性别: 0未知, 1男, 2女',
    `phone` VARCHAR(20) COMMENT '手机号',
    `email` VARCHAR(100) COMMENT '邮箱',
    `class_id` INT UNSIGNED COMMENT '班级ID',
    `major_id` INT UNSIGNED COMMENT '专业ID',
    `enrollment_year` YEAR COMMENT '入学年份',
    `status` TINYINT DEFAULT 1 COMMENT '状态: 0离校, 1在读',
    `raw_id` VARCHAR(50) COMMENT '原始数据ID(用于追溯)',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`class_id`) REFERENCES `classes`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`major_id`) REFERENCES `majors`(`id`) ON DELETE SET NULL,
    INDEX `idx_student_no` (`student_no`),
    INDEX `idx_class` (`class_id`),
    INDEX `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生信息表';

-- 教师/辅导员/管理员表 (统一用户表)
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名/工号',
    `password` VARCHAR(255) NOT NULL COMMENT '密码(加密存储)',
    `name` VARCHAR(50) NOT NULL COMMENT '姓名',
    `role` ENUM('admin', 'teacher', 'counselor', 'student') NOT NULL COMMENT '角色',
    `email` VARCHAR(100) COMMENT '邮箱',
    `phone` VARCHAR(20) COMMENT '手机号',
    `is_active` TINYINT DEFAULT 1 COMMENT '是否启用',
    `last_login` DATETIME COMMENT '最后登录时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_username` (`username`),
    INDEX `idx_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. 课程相关表
-- ============================================

-- 课程表
DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `course_no` VARCHAR(20) UNIQUE COMMENT '课程编号',
    `name` VARCHAR(200) NOT NULL COMMENT '课程名称',
    `description` TEXT COMMENT '课程描述',
    `credit` DECIMAL(3,1) DEFAULT 2.0 COMMENT '学分',
    `hours` INT COMMENT '学时',
    `teacher_id` INT UNSIGNED COMMENT '授课教师ID',
    `semester` VARCHAR(20) COMMENT '学期(如: 2021-2024-1)',
    `chapters` JSON COMMENT '章节信息(用于知识点提取)',
    `status` TINYINT DEFAULT 1 COMMENT '状态: 0结课, 1进行中',
    `raw_id` VARCHAR(50) COMMENT '原始数据ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`teacher_id`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_course_no` (`course_no`),
    INDEX `idx_teacher` (`teacher_id`),
    INDEX `idx_semester` (`semester`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程信息表';

-- 选课关系表
DROP TABLE IF EXISTS `course_enrollments`;
CREATE TABLE `course_enrollments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `enroll_time` DATETIME COMMENT '选课时间',
    `status` TINYINT DEFAULT 1 COMMENT '状态: 0退课, 1正常',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_student_course` (`student_id`, `course_id`),
    INDEX `idx_course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课关系表';

-- 知识点表
DROP TABLE IF EXISTS `knowledge_points`;
CREATE TABLE `knowledge_points` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程',
    `name` VARCHAR(200) NOT NULL COMMENT '知识点名称',
    `chapter_no` VARCHAR(20) COMMENT '章节编号',
    `parent_id` INT UNSIGNED COMMENT '父知识点ID(用于层级)',
    `description` TEXT COMMENT '描述',
    `weight` DECIMAL(4,2) DEFAULT 1.00 COMMENT '权重',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`parent_id`) REFERENCES `knowledge_points`(`id`) ON DELETE SET NULL,
    INDEX `idx_course` (`course_id`),
    INDEX `idx_chapter` (`chapter_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='知识点表';

-- ============================================
-- 3. 学习数据表
-- ============================================

-- 学习活动表(考勤、视频观看等)
DROP TABLE IF EXISTS `learning_activities`;
CREATE TABLE `learning_activities` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `activity_type` ENUM('video', 'sign_in', 'discuss', 'quiz', 'other') NOT NULL COMMENT '活动类型',
    `activity_name` VARCHAR(200) COMMENT '活动名称',
    `chapter_id` INT UNSIGNED COMMENT '关联章节/知识点',
    `start_time` DATETIME COMMENT '开始时间',
    `end_time` DATETIME COMMENT '结束时间',
    `duration` INT COMMENT '持续时长(秒)',
    `progress` DECIMAL(5,2) COMMENT '进度百分比(视频)',
    `score` DECIMAL(5,2) COMMENT '得分(如果有)',
    `raw_data` JSON COMMENT '原始数据备份',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`chapter_id`) REFERENCES `knowledge_points`(`id`) ON DELETE SET NULL,
    INDEX `idx_student_course` (`student_id`, `course_id`),
    INDEX `idx_type` (`activity_type`),
    INDEX `idx_time` (`start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习活动表';

-- 作业任务表
DROP TABLE IF EXISTS `homework_assignments`;
CREATE TABLE `homework_assignments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程',
    `title` VARCHAR(200) NOT NULL COMMENT '作业标题',
    `description` TEXT COMMENT '作业描述',
    `knowledge_point_id` INT UNSIGNED COMMENT '关联知识点',
    `full_score` DECIMAL(5,2) DEFAULT 100.00 COMMENT '满分',
    `start_time` DATETIME COMMENT '开始时间',
    `deadline` DATETIME COMMENT '截止时间',
    `status` TINYINT DEFAULT 1 COMMENT '状态',
    `raw_id` VARCHAR(50) COMMENT '原始数据ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`knowledge_point_id`) REFERENCES `knowledge_points`(`id`) ON DELETE SET NULL,
    INDEX `idx_course` (`course_id`),
    INDEX `idx_deadline` (`deadline`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业任务表';

-- 作业提交表
DROP TABLE IF EXISTS `homework_submissions`;
CREATE TABLE `homework_submissions` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `assignment_id` INT UNSIGNED NOT NULL COMMENT '作业任务ID',
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `score` DECIMAL(5,2) COMMENT '得分',
    `submit_time` DATETIME COMMENT '提交时间',
    `is_late` TINYINT DEFAULT 0 COMMENT '是否迟交',
    `correct_count` INT COMMENT '答对题数',
    `total_count` INT COMMENT '总题数',
    `raw_data` JSON COMMENT '原始答案数据',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`assignment_id`) REFERENCES `homework_assignments`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_assignment_student` (`assignment_id`, `student_id`),
    INDEX `idx_student` (`student_id`),
    INDEX `idx_score` (`score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业提交表';

-- 考试任务表
DROP TABLE IF EXISTS `exam_assignments`;
CREATE TABLE `exam_assignments` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `course_id` INT UNSIGNED NOT NULL COMMENT '所属课程',
    `title` VARCHAR(200) NOT NULL COMMENT '考试标题',
    `exam_type` ENUM('midterm', 'final', 'quiz', 'other') DEFAULT 'quiz' COMMENT '考试类型',
    `full_score` DECIMAL(5,2) DEFAULT 100.00 COMMENT '满分',
    `start_time` DATETIME COMMENT '开始时间',
    `end_time` DATETIME COMMENT '结束时间',
    `duration` INT COMMENT '考试时长(分钟)',
    `status` TINYINT DEFAULT 1 COMMENT '状态',
    `raw_id` VARCHAR(50) COMMENT '原始数据ID',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    INDEX `idx_course` (`course_id`),
    INDEX `idx_type` (`exam_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试任务表';

-- 考试结果表
DROP TABLE IF EXISTS `exam_results`;
CREATE TABLE `exam_results` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `exam_id` INT UNSIGNED NOT NULL COMMENT '考试任务ID',
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `score` DECIMAL(5,2) COMMENT '得分',
    `submit_time` DATETIME COMMENT '提交时间',
    `is_submitted` TINYINT DEFAULT 1 COMMENT '是否提交',
    `correct_count` INT COMMENT '答对题数',
    `total_count` INT COMMENT '总题数',
    `raw_data` JSON COMMENT '原始答案数据',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`exam_id`) REFERENCES `exam_assignments`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_exam_student` (`exam_id`, `student_id`),
    INDEX `idx_student` (`student_id`),
    INDEX `idx_score` (`score`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='考试结果表';

-- ============================================
-- 4. 预警与干预表
-- ============================================

-- 预警记录表
DROP TABLE IF EXISTS `warning_records`;
CREATE TABLE `warning_records` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `course_id` INT UNSIGNED COMMENT '课程ID(为空表示综合预警)',
    `risk_level` ENUM('high', 'medium', 'low', 'normal') NOT NULL COMMENT '风险等级: high红, medium橙, low黄, normal正常',
    `composite_score` DECIMAL(5,2) COMMENT '综合得分',
    -- 各维度得分
    `attendance_score` DECIMAL(5,2) COMMENT '出勤率得分',
    `progress_score` DECIMAL(5,2) COMMENT '学习进度得分',
    `homework_score` DECIMAL(5,2) COMMENT '作业成绩得分',
    `exam_score` DECIMAL(5,2) COMMENT '考试成绩得分',
    -- AI建议
    `ai_analysis` TEXT COMMENT 'AI问题分析',
    `ai_suggestions` JSON COMMENT 'AI建议列表',
    `ai_parent_script` TEXT COMMENT 'AI家长沟通文案',
    `ai_encouragement` TEXT COMMENT 'AI激励信',
    `ai_source` ENUM('ai', 'template') DEFAULT 'template' COMMENT '建议来源',
    -- 状态
    `status` ENUM('active', 'resolved', 'ignored') DEFAULT 'active' COMMENT '预警状态',
    `resolved_at` DATETIME COMMENT '解决时间',
    `resolved_by` INT UNSIGNED COMMENT '处理人ID',
    `resolve_note` TEXT COMMENT '处理备注',
    `calculation_time` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '计算时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`resolved_by`) REFERENCES `users`(`id`) ON DELETE SET NULL,
    INDEX `idx_student` (`student_id`),
    INDEX `idx_course` (`course_id`),
    INDEX `idx_risk_level` (`risk_level`),
    INDEX `idx_status` (`status`),
    INDEX `idx_calc_time` (`calculation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预警记录表';

-- 干预记录表
DROP TABLE IF EXISTS `intervention_records`;
CREATE TABLE `intervention_records` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `warning_id` INT UNSIGNED COMMENT '关联预警ID',
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `course_id` INT UNSIGNED COMMENT '关联课程',
    `intervenor_id` INT UNSIGNED NOT NULL COMMENT '干预人ID(辅导员/教师)',
    `intervention_type` ENUM('talk', 'parent_contact', 'study_plan', 'tutor', 'other') NOT NULL COMMENT '干预类型',
    `title` VARCHAR(200) COMMENT '干预标题',
    `content` TEXT COMMENT '干预内容详情',
    `method` VARCHAR(100) COMMENT '干预方式(面谈/电话/微信等)',
    `result` TEXT COMMENT '干预结果',
    `is_effective` TINYINT COMMENT '是否有效: 0无效, 1有效, 2待观察',
    `follow_up_needed` TINYINT DEFAULT 0 COMMENT '是否需要跟进',
    `follow_up_time` DATETIME COMMENT '计划跟进时间',
    `intervention_time` DATETIME NOT NULL COMMENT '干预时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`warning_id`) REFERENCES `warning_records`(`id`) ON DELETE SET NULL,
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`intervenor_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_student` (`student_id`),
    INDEX `idx_warning` (`warning_id`),
    INDEX `idx_intervenor` (`intervenor_id`),
    INDEX `idx_time` (`intervention_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='干预记录表';

-- 学生综合得分表(用于快速查询)
DROP TABLE IF EXISTS `student_course_scores`;
CREATE TABLE `student_course_scores` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` INT UNSIGNED NOT NULL COMMENT '学生ID',
    `course_id` INT UNSIGNED NOT NULL COMMENT '课程ID',
    `attendance_rate` DECIMAL(5,2) COMMENT '出勤率',
    `video_progress` DECIMAL(5,2) COMMENT '视频进度',
    `homework_avg` DECIMAL(5,2) COMMENT '作业平均分',
    `homework_submit_rate` DECIMAL(5,2) COMMENT '作业提交率',
    `exam_avg` DECIMAL(5,2) COMMENT '考试平均分',
    `knowledge_mastery` DECIMAL(5,2) COMMENT '知识点掌握度',
    `final_score` DECIMAL(5,2) COMMENT '期末成绩(如果有)',
    `last_calculated` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后计算时间',
    FOREIGN KEY (`student_id`) REFERENCES `students`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`course_id`) REFERENCES `courses`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `uk_student_course` (`student_id`, `course_id`),
    INDEX `idx_course` (`course_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生课程综合得分表';

-- ============================================
-- 5. 初始化数据
-- ============================================

-- 插入默认专业
INSERT INTO `majors` (`name`, `code`, `department`) VALUES
('计算机科学与技术', 'CS001', '计算机学院'),
('软件工程', 'SE001', '软件学院'),
('数据科学与大数据技术', 'DS001', '数据学院');

-- 插入管理员账号(密码需加密替换)
INSERT INTO `users` (`username`, `password`, `name`, `role`, `email`, `is_active`) VALUES
('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '系统管理员', 'admin', 'admin@example.edu.cn', 1);
-- 默认密码: password (请修改!)

SET FOREIGN_KEY_CHECKS = 1;
