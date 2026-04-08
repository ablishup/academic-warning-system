-- ========================================================
-- 学生学业预警系统 - 数据库表结构（适配超星公网数据）
-- 简化方案：以课程章节作为知识点
-- ========================================================

-- 删除已存在的表（谨慎使用）
-- DROP TABLE IF EXISTS warning_records;
-- DROP TABLE IF EXISTS learning_activities;
-- DROP TABLE IF EXISTS knowledge_mastery;
-- DROP TABLE IF EXISTS knowledge_points;
-- DROP TABLE IF EXISTS exam_results;
-- DROP TABLE IF EXISTS exam_assignments;
-- DROP TABLE IF EXISTS homework_submissions;
-- DROP TABLE IF EXISTS homework_assignments;
-- DROP TABLE IF EXISTS course_enrollments;
-- DROP TABLE IF EXISTS courses;
-- DROP TABLE IF EXISTS students;
-- DROP TABLE IF EXISTS classes;
-- DROP TABLE IF EXISTS majors;

-- ========================================================
-- 1. 基础信息表
-- ========================================================

-- 专业表
CREATE TABLE IF NOT EXISTS majors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '专业名称',
    code VARCHAR(50) UNIQUE COMMENT '专业代码',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='专业信息表';

-- 班级表
CREATE TABLE IF NOT EXISTS classes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_id VARCHAR(50) COMMENT '超星原始ID',
    name VARCHAR(100) NOT NULL COMMENT '班级名称',
    grade VARCHAR(20) COMMENT '年级',
    major_id INT COMMENT '专业ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (major_id) REFERENCES majors(id) ON DELETE SET NULL,
    INDEX idx_original_id (original_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级信息表';

-- 学生表（基于超星t_stat_person）
CREATE TABLE IF NOT EXISTS students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_id VARCHAR(50) COMMENT '超星原始user_id',
    student_id VARCHAR(50) UNIQUE NOT NULL COMMENT '学号',
    name VARCHAR(100) NOT NULL COMMENT '姓名',
    class_id INT COMMENT '班级ID',
    gender ENUM('男', '女', '未知') DEFAULT '未知' COMMENT '性别',
    phone VARCHAR(20) COMMENT '电话',
    email VARCHAR(100) COMMENT '邮箱',
    status ENUM('在读', '休学', '退学', '毕业') DEFAULT '在读' COMMENT '学籍状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
    INDEX idx_student_id (student_id),
    INDEX idx_original_id (original_id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生信息表';

-- ========================================================
-- 2. 课程相关表
-- ========================================================

-- 课程表（基于超星t_stat_course）
CREATE TABLE IF NOT EXISTS courses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_id VARCHAR(50) COMMENT '超星原始course_id',
    name VARCHAR(200) NOT NULL COMMENT '课程名称',
    teacher_name VARCHAR(100) COMMENT '教师姓名',
    description TEXT COMMENT '课程描述',
    credit DECIMAL(3,1) DEFAULT 2.0 COMMENT '学分',
    semester VARCHAR(50) COMMENT '学期',
    total_chapters INT DEFAULT 8 COMMENT '总章节数',
    status ENUM('未开始', '进行中', '已结束') DEFAULT '进行中' COMMENT '课程状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_original_id (original_id),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程信息表';

-- 选课关系表（基于超星t_stat_course_person）
CREATE TABLE IF NOT EXISTS course_enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    course_id INT NOT NULL COMMENT '课程ID',
    enrollment_date DATE COMMENT '选课日期',
    status ENUM('正常', '退课', ' completed') DEFAULT '正常' COMMENT '选课状态',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, course_id),
    INDEX idx_student (student_id),
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生选课关系表';

-- ========================================================
-- 3. 知识点表（简化方案：章节即知识点）
-- ========================================================

CREATE TABLE IF NOT EXISTS knowledge_points (
    id INT PRIMARY KEY AUTO_INCREMENT,
    course_id INT NOT NULL COMMENT '所属课程ID',
    name VARCHAR(200) NOT NULL COMMENT '知识点名称（章节名）',
    description TEXT COMMENT '知识点描述',
    chapter_order INT DEFAULT 1 COMMENT '章节顺序',
    parent_id INT DEFAULT NULL COMMENT '父知识点ID（用于层级结构）',
    weight DECIMAL(3,2) DEFAULT 1.00 COMMENT '权重',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_id) REFERENCES knowledge_points(id) ON DELETE SET NULL,
    INDEX idx_course (course_id),
    INDEX idx_order (chapter_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识点表（章节级）';

-- 知识点掌握度表（学生-知识点关联）
CREATE TABLE IF NOT EXISTS knowledge_mastery (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    knowledge_point_id INT NOT NULL COMMENT '知识点ID',
    mastery_level DECIMAL(5,2) DEFAULT 0.00 COMMENT '掌握度 0-100',
    practice_count INT DEFAULT 0 COMMENT '练习次数',
    correct_count INT DEFAULT 0 COMMENT '正确次数',
    last_practice_at TIMESTAMP NULL COMMENT '最后练习时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE,
    UNIQUE KEY unique_mastery (student_id, knowledge_point_id),
    INDEX idx_student (student_id),
    INDEX idx_kp (knowledge_point_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学生知识点掌握度表';

-- ========================================================
-- 4. 学习活动表（基于超星t_stat_activity_log）
-- ========================================================

CREATE TABLE IF NOT EXISTS learning_activities (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    course_id INT NOT NULL COMMENT '课程ID',
    activity_type VARCHAR(50) NOT NULL COMMENT '活动类型',
    -- 视频观看、资料阅读、讨论参与、签到等
    activity_name VARCHAR(200) COMMENT '活动名称',
    duration INT DEFAULT 0 COMMENT '学习时长（秒）',
    progress DECIMAL(5,2) DEFAULT 0.00 COMMENT '完成进度 0-100',
    occurred_at TIMESTAMP NOT NULL COMMENT '活动时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_course (course_id),
    INDEX idx_type (activity_type),
    INDEX idx_occurred (occurred_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学习活动记录表';

-- ========================================================
-- 5. 作业相关表（基于超星t_stat_work_answer）
-- ========================================================

-- 作业任务表
CREATE TABLE IF NOT EXISTS homework_assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_id VARCHAR(50) COMMENT '超星原始作业ID',
    course_id INT NOT NULL COMMENT '所属课程ID',
    knowledge_point_id INT COMMENT '关联知识点ID',
    title VARCHAR(200) NOT NULL COMMENT '作业标题',
    description TEXT COMMENT '作业描述',
    total_score DECIMAL(5,2) DEFAULT 100.00 COMMENT '总分',
    start_time TIMESTAMP COMMENT '开始时间',
    end_time TIMESTAMP COMMENT '截止时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE SET NULL,
    INDEX idx_course (course_id),
    INDEX idx_kp (knowledge_point_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作业任务表';

-- 作业提交表
CREATE TABLE IF NOT EXISTS homework_submissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    homework_id INT NOT NULL COMMENT '作业ID',
    course_id INT NOT NULL COMMENT '课程ID',
    score DECIMAL(5,2) COMMENT '得分',
    content TEXT COMMENT '提交内容',
    submit_time TIMESTAMP COMMENT '提交时间',
    is_late TINYINT DEFAULT 0 COMMENT '是否迟交',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (homework_id) REFERENCES homework_assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_submission (student_id, homework_id),
    INDEX idx_student (student_id),
    INDEX idx_homework (homework_id),
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作业提交记录表';

-- ========================================================
-- 6. 考试相关表（基于超星t_stat_exam_answer）
-- ========================================================

-- 考试任务表
CREATE TABLE IF NOT EXISTS exam_assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    original_id VARCHAR(50) COMMENT '超星原始考试ID',
    course_id INT NOT NULL COMMENT '所属课程ID',
    title VARCHAR(200) NOT NULL COMMENT '考试标题',
    description TEXT COMMENT '考试描述',
    total_score DECIMAL(5,2) DEFAULT 100.00 COMMENT '总分',
    duration INT COMMENT '考试时长（分钟）',
    start_time TIMESTAMP COMMENT '开始时间',
    end_time TIMESTAMP COMMENT '截止时间',
    exam_type ENUM('期中', '期末', '平时测验') DEFAULT '平时测验' COMMENT '考试类型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试任务表';

-- 考试题目与知识点关联表
CREATE TABLE IF NOT EXISTS exam_question_knowledge (
    id INT PRIMARY KEY AUTO_INCREMENT,
    exam_id INT NOT NULL COMMENT '考试ID',
    question_id VARCHAR(50) COMMENT '题目ID',
    knowledge_point_id INT NOT NULL COMMENT '知识点ID',
    score DECIMAL(5,2) COMMENT '题目分值',
    FOREIGN KEY (exam_id) REFERENCES exam_assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试题目知识点关联表';

-- 考试结果表
CREATE TABLE IF NOT EXISTS exam_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    exam_id INT NOT NULL COMMENT '考试ID',
    course_id INT NOT NULL COMMENT '课程ID',
    score DECIMAL(5,2) COMMENT '得分',
    answers TEXT COMMENT '答题内容（JSON格式）',
    submit_time TIMESTAMP COMMENT '提交时间',
    cheating_suspected TINYINT DEFAULT 0 COMMENT '是否疑似作弊',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES exam_assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY unique_exam_result (student_id, exam_id),
    INDEX idx_student (student_id),
    INDEX idx_exam (exam_id),
    INDEX idx_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='考试结果表';

-- ========================================================
-- 7. 预警相关表
-- ========================================================

-- 预警记录表
CREATE TABLE IF NOT EXISTS warning_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL COMMENT '学生ID',
    course_id INT COMMENT '课程ID（可为空表示整体预警）',

    -- 各项指标得分
    attendance_score DECIMAL(5,2) COMMENT '出勤率得分',
    progress_score DECIMAL(5,2) COMMENT '进度得分',
    homework_score DECIMAL(5,2) COMMENT '作业得分',
    exam_score DECIMAL(5,2) COMMENT '考试得分',
    comprehensive_score DECIMAL(5,2) NOT NULL COMMENT '综合预警分数',

    -- 预警等级
    risk_level ENUM('red', 'orange', 'yellow', 'normal') NOT NULL COMMENT '风险等级',
    -- red: <60, orange: 60-75, yellow: 75-85, normal: >=85

    -- 预警原因分析（JSON格式）
    risk_factors JSON COMMENT '风险因素分析',

    -- 预警状态
    status ENUM('active', 'processed', 'resolved') DEFAULT 'active' COMMENT '预警状态',

    -- AI建议
    ai_suggestion TEXT COMMENT 'AI生成的干预建议',
    ai_suggestion_for_student TEXT COMMENT '面向学生的AI建议',

    -- 处理记录
    counselor_notes TEXT COMMENT '辅导员处理备注',
    intervention_plan TEXT COMMENT '干预计划',
    processed_by INT COMMENT '处理人ID',
    processed_at TIMESTAMP COMMENT '处理时间',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_course (course_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='学业预警记录表';

-- 预警规则配置表
CREATE TABLE IF NOT EXISTS warning_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL COMMENT '规则名称',
    description TEXT COMMENT '规则描述',

    -- 权重配置
    attendance_weight DECIMAL(3,2) DEFAULT 0.30 COMMENT '出勤率权重',
    progress_weight DECIMAL(3,2) DEFAULT 0.20 COMMENT '进度权重',
    homework_weight DECIMAL(3,2) DEFAULT 0.30 COMMENT '作业权重',
    exam_weight DECIMAL(3,2) DEFAULT 0.20 COMMENT '考试权重',

    -- 阈值配置
    red_threshold DECIMAL(5,2) DEFAULT 60.00 COMMENT '红色预警阈值',
    orange_threshold DECIMAL(5,2) DEFAULT 75.00 COMMENT '橙色预警阈值',
    yellow_threshold DECIMAL(5,2) DEFAULT 85.00 COMMENT '黄色预警阈值',

    is_active TINYINT DEFAULT 1 COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='预警规则配置表';

-- 插入默认预警规则
INSERT INTO warning_rules (name, description) VALUES
('默认预警规则', '系统默认的学业预警计算规则：出勤30% + 进度20% + 作业30% + 考试20%');

-- ========================================================
-- 8. 视图（方便查询）
-- ========================================================

-- 学生课程综合表现视图
CREATE OR REPLACE VIEW v_student_course_performance AS
SELECT
    s.id AS student_id,
    s.student_id AS student_code,
    s.name AS student_name,
    c.id AS course_id,
    c.name AS course_name,

    -- 出勤率（基于学习活动记录）
    COALESCE((
        SELECT COUNT(*) FROM learning_activities la
        WHERE la.student_id = s.id AND la.course_id = c.id
    ) * 10.0, 0) AS attendance_score,  -- 简化计算，实际需要更复杂的逻辑

    -- 作业平均分
    COALESCE((
        SELECT AVG(hs.score / ha.total_score * 100)
        FROM homework_submissions hs
        JOIN homework_assignments ha ON hs.homework_id = ha.id
        WHERE hs.student_id = s.id AND ha.course_id = c.id
    ), 0) AS homework_avg,

    -- 考试平均分
    COALESCE((
        SELECT AVG(er.score / ea.total_score * 100)
        FROM exam_results er
        JOIN exam_assignments ea ON er.exam_id = ea.id
        WHERE er.student_id = s.id AND ea.course_id = c.id
    ), 0) AS exam_avg

FROM students s
CROSS JOIN courses c
WHERE EXISTS (
    SELECT 1 FROM course_enrollments ce
    WHERE ce.student_id = s.id AND ce.course_id = c.id
);

-- ========================================================
-- 9. 初始化数据
-- ========================================================

-- 插入示例专业
INSERT INTO majors (name, code) VALUES
('计算机科学与技术', 'CS'),
('软件工程', 'SE'),
('信息安全', 'IS'),
('数据科学与大数据技术', 'DS');
