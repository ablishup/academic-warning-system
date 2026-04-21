#!/usr/bin/env python
"""
添加AI评语扩展字段到数据库
由于模型使用 managed=False，需要通过此脚本直接修改数据库
"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection


def add_warning_record_fields():
    """添加warning_records表字段"""
    fields = [
        ('ai_generated_at', 'DATETIME NULL COMMENT "AI评语生成时间"'),
        ('ai_generated_by', 'INT NULL COMMENT "AI评语生成者ID"'),
        ('counselor_comment', 'TEXT NULL COMMENT "辅导员评语"'),
        ('counselor_suggestions', 'JSON NULL COMMENT "辅导员建议列表"'),
        ('counselor_talk_script', 'TEXT NULL COMMENT "沟通话术建议"'),
        ('sms_sent', 'TINYINT(1) DEFAULT 0 COMMENT "短信已发送"'),
        ('sms_sent_at', 'DATETIME NULL COMMENT "短信发送时间"'),
    ]

    with connection.cursor() as cursor:
        for field_name, field_def in fields:
            try:
                # 检查字段是否已存在
                cursor.execute(f"""
                    SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'warning_records'
                    AND COLUMN_NAME = '{field_name}'
                    AND TABLE_SCHEMA = DATABASE()
                """)
                exists = cursor.fetchone()[0]

                if exists:
                    print(f"字段 {field_name} 已存在，跳过")
                    continue

                # 添加字段
                sql = f"ALTER TABLE warning_records ADD COLUMN {field_name} {field_def}"
                cursor.execute(sql)
                print(f"成功添加字段: {field_name}")

            except Exception as e:
                print(f"添加字段 {field_name} 失败: {e}")


def create_sms_notifications_table():
    """创建短信通知记录表"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS sms_notifications (
        id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
        sender_id INT NOT NULL COMMENT '发送者ID',
        student_id INT NOT NULL COMMENT '接收学生ID',
        phone VARCHAR(20) NOT NULL COMMENT '接收手机号',
        warning_id INT NULL COMMENT '关联预警ID',
        content TEXT NOT NULL COMMENT '短信内容',
        status VARCHAR(20) DEFAULT 'pending' COMMENT '状态: pending/sent/delivered/failed',
        error_message TEXT NULL COMMENT '错误信息',
        sent_at DATETIME NULL COMMENT '发送时间',
        delivered_at DATETIME NULL COMMENT '送达时间',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
        INDEX idx_student (student_id),
        INDEX idx_status (status),
        INDEX idx_warning (warning_id),
        INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='短信通知记录表'
    """

    with connection.cursor() as cursor:
        try:
            cursor.execute(create_table_sql)
            print("成功创建表: sms_notifications")
        except Exception as e:
            if 'Table' in str(e) and 'already exists' in str(e):
                print("表 sms_notifications 已存在，跳过")
            else:
                print(f"创建表 sms_notifications 失败: {e}")


def main():
    print("=" * 60)
    print("AI PingYu KuoZhan - ShuJuKu ZiDuan TianJia")
    print("=" * 60)
    print()

    print("[1/2] TianJia warning_records Biao ZiDuan...")
    add_warning_record_fields()
    print()

    print("[2/2] ChuangJian sms_notifications Biao...")
    create_sms_notifications_table()
    print()

    print("=" * 60)
    print("ShuJuKu KuoZhan WanCheng!")
    print("=" * 60)


if __name__ == '__main__':
    main()
