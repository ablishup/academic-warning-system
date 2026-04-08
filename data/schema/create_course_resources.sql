-- 创建课程资源表
CREATE TABLE IF NOT EXISTS course_resources (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    course_id INT UNSIGNED NOT NULL,
    knowledge_point_id INT UNSIGNED NULL,
    name VARCHAR(200) NOT NULL COMMENT '资料名称',
    file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
    resource_type VARCHAR(20) NOT NULL COMMENT '资料类型:video视频/document文档/ppt课件/exercise习题',
    description TEXT NULL COMMENT '描述',
    file_size INT DEFAULT 0 COMMENT '文件大小(字节)',
    download_count INT DEFAULT 0 COMMENT '下载次数',
    created_by INT UNSIGNED NULL COMMENT '上传者ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_course_id (course_id),
    INDEX idx_resource_type (resource_type),
    INDEX idx_knowledge_point (knowledge_point_id),
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='课程资源表';
