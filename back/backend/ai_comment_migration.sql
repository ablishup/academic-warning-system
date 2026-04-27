-- AI评语扩展数据库迁移脚本
-- 执行时间: 2026-04-19

-- =============================================
-- 1. 扩展 warning_records 表（添加辅导员评语字段）
-- =============================================

-- 添加AI评语生成时间和生成者
ALTER TABLE warning_records
ADD COLUMN ai_generated_at DATETIME NULL COMMENT 'AI评语生成时间';

ALTER TABLE warning_records
ADD COLUMN ai_generated_by INT NULL COMMENT 'AI评语生成者ID';

-- 添加辅导员评语字段
ALTER TABLE warning_records
ADD COLUMN counselor_comment TEXT NULL COMMENT '辅导员评语';

ALTER TABLE warning_records
ADD COLUMN counselor_suggestions JSON NULL COMMENT '辅导员建议列表';

ALTER TABLE warning_records
ADD COLUMN counselor_talk_script TEXT NULL COMMENT '沟通话术建议';

-- 添加短信通知状态
ALTER TABLE warning_records
ADD COLUMN sms_sent TINYINT(1) DEFAULT 0 COMMENT '短信已发送';

ALTER TABLE warning_records
ADD COLUMN sms_sent_at DATETIME NULL COMMENT '短信发送时间';

-- =============================================
-- 2. 创建短信通知记录表
-- =============================================

CREATE TABLE IF NOT EXISTS sms_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',

    -- 发送信息
    sender_id INT NOT NULL COMMENT '发送者ID',
    student_id INT NOT NULL COMMENT '接收学生ID',
    phone VARCHAR(20) NOT NULL COMMENT '接收手机号',

    -- 关联内容
    warning_id INT NULL COMMENT '关联预警ID',
    content TEXT NOT NULL COMMENT '短信内容',

    -- 状态
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/sent/delivered/failed',
    error_message TEXT NULL COMMENT '错误信息',

    -- 时间戳
    sent_at DATETIME NULL COMMENT '发送时间',
    delivered_at DATETIME NULL COMMENT '送达时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    -- 索引
    INDEX idx_student (student_id),
    INDEX idx_status (status),
    INDEX idx_warning (warning_id),
    INDEX idx_created (created_at)

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='短信通知记录表';

-- =============================================
-- 3. SQLite 兼容版本（如果使用的是SQLite）
-- =============================================
-- 对于SQLite，请使用以下命令：

-- ALTER TABLE warning_records ADD COLUMN ai_generated_at DATETIME;
-- ALTER TABLE warning_records ADD COLUMN ai_generated_by INTEGER;
-- ALTER TABLE warning_records ADD COLUMN counselor_comment TEXT;
-- ALTER TABLE warning_records ADD COLUMN counselor_suggestions TEXT; -- SQLite没有JSON类型，用TEXT存储
-- ALTER TABLE warning_records ADD COLUMN counselor_talk_script TEXT;
-- ALTER TABLE warning_records ADD COLUMN sms_sent INTEGER DEFAULT 0;
-- ALTER TABLE warning_records ADD COLUMN sms_sent_at DATETIME;

-- CREATE TABLE sms_notifications (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     sender_id INTEGER NOT NULL,
--     student_id INTEGER NOT NULL,
--     phone TEXT NOT NULL,
--     warning_id INTEGER,
--     content TEXT NOT NULL,
--     status TEXT DEFAULT 'pending',
--     error_message TEXT,
--     sent_at DATETIME,
--     delivered_at DATETIME,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
-- );
