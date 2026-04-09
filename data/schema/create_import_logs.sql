-- 创建导入记录表
CREATE TABLE IF NOT EXISTS import_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    import_type VARCHAR(20) NOT NULL COMMENT '导入类型:activities/homework/exams/enrollments',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_size INT DEFAULT 0 COMMENT '文件大小(字节)',
    uploaded_by INT UNSIGNED NULL COMMENT '上传者ID',
    course_id INT UNSIGNED NULL COMMENT '关联课程ID',
    total_rows INT DEFAULT 0 COMMENT '总行数',
    success_rows INT DEFAULT 0 COMMENT '成功行数',
    failed_rows INT DEFAULT 0 COMMENT '失败行数',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '状态:pending/success/partial/failed',
    error_message TEXT NULL COMMENT '错误信息',
    details JSON NULL COMMENT '详细信息',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_import_type (import_type),
    INDEX idx_course_id (course_id),
    INDEX idx_status (status),
    INDEX idx_uploaded_by (uploaded_by),
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据导入记录表';
