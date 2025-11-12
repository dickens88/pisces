

-- 1. 应用用户表
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='应用用户表';

-- 2. 系统配置表
CREATE TABLE IF NOT EXISTS `t_system_config` (
    `id` BIGINT(20) NOT NULL AUTO_INCREMENT COMMENT '配置ID',
    `key_name` VARCHAR(200) DEFAULT NULL COMMENT '配置键名',
    `key_value` VARCHAR(500) DEFAULT NULL COMMENT '配置值',
    `last_update_time` DATETIME DEFAULT NULL COMMENT '最后更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_key_name` (`key_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';

-- 3. 已撤销令牌表
CREATE TABLE IF NOT EXISTS `t_revoked_tokens` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
    `jti` VARCHAR(120) DEFAULT NULL COMMENT 'JWT Token ID',
    PRIMARY KEY (`id`),
    KEY `idx_jti` (`jti`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='已撤销的JWT令牌表';

-- 4. 告警表
CREATE TABLE IF NOT EXISTS `t_alerts` (
    `id` INT(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `alert_id` TINYTEXT COMMENT '告警唯一ID',
    `create_time` VARCHAR(40) DEFAULT NULL COMMENT '创建时间，ISO8601含时区',
    `last_update_time` VARCHAR(40) DEFAULT NULL COMMENT '最后更新时间，ISO8601含时区',
    `close_time` VARCHAR(40) DEFAULT NULL COMMENT '关闭时间，ISO8601含时区',
    `title` TEXT COMMENT '标题',
    `description` TEXT COMMENT '描述',
    `severity` ENUM('TIPS', 'LOW', 'MEDIUM', 'HIGH', 'FATAL') DEFAULT 'MEDIUM' COMMENT '严重程度',
    `handle_status` ENUM('Open', 'Block', 'Closed') DEFAULT 'Open' COMMENT '处理状态',
    `owner` TINYTEXT COMMENT '负责人',
    `creator` TINYTEXT COMMENT '创建人',
    `close_reason` ENUM('False positive', 'Resolved', 'Repeated', 'Other') DEFAULT NULL COMMENT '关闭原因',
    `close_comment` TEXT COMMENT '关闭备注',
    `data_source_product_name` TINYTEXT COMMENT '数据源产品名',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='告警表';

-- 5. 创建数据库用户并授予权限
-- 创建用户 pisces_user，密码为 1234567
CREATE USER IF NOT EXISTS 'pisces_user'@'%' IDENTIFIED BY '1234567';

-- 授予 pisces_db 数据库的所有权限给 pisces_user
GRANT ALL PRIVILEGES ON pisces_db.* TO 'pisces_user'@'%';

-- 刷新权限使更改生效
FLUSH PRIVILEGES;
