

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

-- 4. 创建数据库用户并授予权限
-- 创建用户 pisces_user，密码为 1234567
CREATE USER IF NOT EXISTS 'pisces_user'@'%' IDENTIFIED BY '1234567';

-- 授予 pisces_db 数据库的所有权限给 pisces_user
GRANT ALL PRIVILEGES ON pisces_db.* TO 'pisces_user'@'%';

-- 刷新权限使更改生效
FLUSH PRIVILEGES;
