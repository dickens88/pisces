CREATE TABLE `t_app_user` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(128) DEFAULT NULL COMMENT '用户名',
  `password` varchar(256) DEFAULT NULL COMMENT '密码（SHA256加密）',
  `enabled` int DEFAULT NULL COMMENT '是否启用：1-启用，0-禁用',
  `group` varchar(256) DEFAULT 'default' COMMENT '用户组',
  `last_update_time` datetime DEFAULT NULL COMMENT '最后更新时间',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='应用用户表';

CREATE TABLE `t_comments` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `event_id` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '事件ID（告警ID或事件ID）',
  `comment_id` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '评论ID（唯一键，关联外部评论系统）',
  `owner` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '评论所有者',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `message` text COLLATE utf8mb4_unicode_ci COMMENT '评论内容',
  `file_type` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '文件类型（MIME类型，如 image/jpeg）',
  `file_obj` longblob COMMENT '文件二进制数据',
  `file_name` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_comment_id` (`comment_id`),
  KEY `idx_event_id` (`event_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评论表';


CREATE TABLE `t_incidents` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `incident_id` varchar(40) DEFAULT NULL COMMENT '事件唯一ID',
  `create_time` varchar(40) DEFAULT NULL COMMENT '创建时间，ISO8601含时区',
  `last_update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `close_time` varchar(40) DEFAULT NULL COMMENT '关闭时间，ISO8601含时区',
  `arrive_time` varchar(40) DEFAULT NULL COMMENT '到达时间，ISO8601含时区',
  `title` text COMMENT '标题',
  `description` text COMMENT '描述',
  `severity` enum('TIPS','LOW','MEDIUM','HIGH','FATAL') DEFAULT 'MEDIUM' COMMENT '严重程度',
  `handle_status` enum('Open','Block','Closed') DEFAULT 'Open' COMMENT '处理状态',
  `owner` tinytext COMMENT '负责人',
  `creator` tinytext COMMENT '创建人',
  `responsible_person` tinytext COMMENT '责任人',
  `responsible_dept` tinytext COMMENT '责任部门',
  `close_reason` enum('False positive','Resolved','Repeated','Other') DEFAULT NULL COMMENT '关闭原因',
  `close_comment` text COMMENT '关闭备注',
  `labels` text COMMENT '标签（多个标签用逗号分隔）',
  `root_cause` text COMMENT '根本原因',
  `category` tinytext COMMENT '分类',
  `ttd` varchar(40) DEFAULT NULL COMMENT '检测时间（Time To Detect）',
  `is_auto_closed` varchar(10) DEFAULT NULL COMMENT '是否自动关闭',
  `extend_properties` text COMMENT '扩展属性（JSON格式）',
  PRIMARY KEY (`id`),
  KEY `idx_incident_id` (`incident_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='事件表';


CREATE TABLE `t_revoked_tokens` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `jti` varchar(120) DEFAULT NULL COMMENT 'JWT Token ID',
  PRIMARY KEY (`id`),
  KEY `idx_jti` (`jti`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='已撤销的JWT令牌表';


CREATE TABLE `t_system_config` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '配置ID',
  `key_name` varchar(200) DEFAULT NULL COMMENT '配置键名',
  `key_value` varchar(500) DEFAULT NULL COMMENT '配置值',
  `last_update_time` datetime DEFAULT NULL COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_key_name` (`key_name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统配置表';


CREATE TABLE `t_alerts` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `alert_id` varchar(40) DEFAULT NULL COMMENT '告警唯一ID',
  `create_time` varchar(40) DEFAULT NULL COMMENT '创建时间，ISO8601含时区',
  `last_update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `close_time` varchar(40) DEFAULT NULL COMMENT '关闭时间，ISO8601含时区',
  `title` text COMMENT '标题',
  `description` text COMMENT '描述',
  `severity` varchar(10) NOT NULL COMMENT '严重程度',
  `handle_status` varchar(10) NOT NULL COMMENT '处理状态',
  `owner` tinytext COMMENT '负责人',
  `creator` tinytext COMMENT '创建人',
  `close_reason` enum('False positive','Resolved','Repeated','Other') DEFAULT NULL COMMENT '关闭原因',
  `close_comment` text COMMENT '关闭备注',
  `data_source_product_name` tinytext COMMENT '数据源产品名',
  `is_auto_closed` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alert_id_UNIQUE` (`alert_id`)
) ENGINE=InnoDB AUTO_INCREMENT=936 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='告警表';