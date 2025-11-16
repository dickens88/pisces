-- ============================================
-- Pisces 数据库初始化脚本
-- ============================================

-- 创建数据库（如果不存在）
-- CREATE DATABASE IF NOT EXISTS pisces CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE pisces;

-- ============================================
-- 1. 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS `t_app_user` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username` VARCHAR(128) DEFAULT NULL COMMENT '用户名',
    `password` VARCHAR(256) DEFAULT NULL COMMENT '密码（SHA256加密）',
    `enabled` INT(11) DEFAULT NULL COMMENT '是否启用：1-启用，0-禁用',
    `group` VARCHAR(256) DEFAULT 'default' COMMENT '用户组',
    `last_update_time` DATETIME DEFAULT NULL COMMENT '最后更新时间',
    `create_time` DATETIME DEFAULT NULL COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='应用用户表';

-- ============================================
-- 2. 撤销的Token表
-- ============================================
CREATE TABLE IF NOT EXISTS `t_revoked_tokens` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `jti` VARCHAR(120) DEFAULT NULL COMMENT 'JWT Token ID',
    PRIMARY KEY (`id`),
    KEY `idx_jti` (`jti`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='撤销的Token表';

-- ============================================
-- 3. 告警表
-- ============================================
CREATE TABLE IF NOT EXISTS `t_alerts` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '告警ID',
    `alert_id` TEXT COMMENT '告警唯一标识',
    `create_time` VARCHAR(40) DEFAULT NULL COMMENT '创建时间',
    `last_update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    `close_time` VARCHAR(40) DEFAULT NULL COMMENT '关闭时间',
    `title` TEXT COMMENT '告警标题',
    `description` TEXT COMMENT '告警描述',
    `severity` VARCHAR(10) DEFAULT NULL COMMENT '严重程度',
    `handle_status` VARCHAR(10) DEFAULT NULL COMMENT '处理状态',
    `owner` TEXT COMMENT '负责人',
    `creator` TEXT COMMENT '创建人',
    `close_reason` ENUM('False positive', 'Resolved', 'Repeated', 'Other') DEFAULT NULL COMMENT '关闭原因',
    `close_comment` TEXT COMMENT '关闭备注',
    `is_auto_closed` VARCHAR(50) DEFAULT NULL COMMENT '是否自动关闭',
    `data_source_product_name` TEXT COMMENT '数据源产品名称',
    PRIMARY KEY (`id`),
    KEY `idx_alert_id` (`alert_id`(191)),
    KEY `idx_severity` (`severity`),
    KEY `idx_handle_status` (`handle_status`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='告警表';

-- ============================================
-- 4. 事件表
-- ============================================
CREATE TABLE IF NOT EXISTS `t_incidents` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '事件ID',
    `incident_id` TEXT COMMENT '事件唯一标识',
    `create_time` VARCHAR(40) DEFAULT NULL COMMENT '创建时间',
    `last_update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    `close_time` VARCHAR(40) DEFAULT NULL COMMENT '关闭时间',
    `arrive_time` VARCHAR(40) DEFAULT NULL COMMENT '到达时间',
    `title` TEXT COMMENT '事件标题',
    `description` TEXT COMMENT '事件描述',
    `severity` VARCHAR(10) DEFAULT NULL COMMENT '严重程度',
    `handle_status` VARCHAR(10) DEFAULT NULL COMMENT '处理状态',
    `owner` TEXT COMMENT '负责人',
    `creator` TEXT COMMENT '创建人',
    `responsible_person` TEXT COMMENT '责任人',
    `responsible_dept` TEXT COMMENT '责任部门',
    `close_reason` ENUM('False positive', 'Resolved', 'Repeated', 'Other') DEFAULT NULL COMMENT '关闭原因',
    `close_comment` TEXT COMMENT '关闭备注',
    `labels` TEXT COMMENT '标签（逗号分隔）',
    `root_cause` TEXT COMMENT '根本原因',
    `category` TEXT COMMENT '分类',
    `ttd` VARCHAR(40) DEFAULT NULL COMMENT '处理时间（Time to Detect）',
    `is_auto_closed` VARCHAR(10) DEFAULT NULL COMMENT '是否自动关闭',
    `extend_properties` TEXT COMMENT '扩展属性（JSON格式）',
    PRIMARY KEY (`id`),
    KEY `idx_incident_id` (`incident_id`(191)),
    KEY `idx_severity` (`severity`),
    KEY `idx_handle_status` (`handle_status`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='事件表';

-- ============================================
-- 5. 评论表
-- ============================================
CREATE TABLE IF NOT EXISTS `t_comments` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    `event_id` VARCHAR(255) DEFAULT NULL COMMENT '关联的事件ID（告警或事件）',
    `comment_id` VARCHAR(255) NOT NULL COMMENT '评论唯一标识',
    `owner` VARCHAR(255) DEFAULT NULL COMMENT '评论人',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `message` TEXT COMMENT '评论内容',
    `file_type` VARCHAR(100) DEFAULT NULL COMMENT '附件类型',
    `file_name` VARCHAR(500) DEFAULT NULL COMMENT '附件文件名',
    `file_obj` LONGBLOB COMMENT '附件文件内容',
    `last_update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_comment_id` (`comment_id`),
    KEY `idx_event_id` (`event_id`),
    KEY `idx_owner` (`owner`),
    KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论表';

-- ============================================
-- 6. 系统配置表
-- ============================================
CREATE TABLE IF NOT EXISTS `t_system_config` (
    `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '配置ID',
    `key_name` VARCHAR(200) DEFAULT NULL COMMENT '配置键名',
    `key_value` VARCHAR(500) DEFAULT NULL COMMENT '配置值',
    `last_update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_key_name` (`key_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ============================================
-- 初始化数据（可选）
-- ============================================

