-- 创建影响服务和事件简报统一表
-- 用于存储事件管理中的影响服务和事件简报数据
-- 通过 type 字段区分：'impacted_service'（影响服务）或 'incident_brief'（事件简报）
-- 执行日期：2026-01-XX

CREATE TABLE IF NOT EXISTS `t_impacted_services` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `incident_id` varchar(40) NOT NULL COMMENT '事件ID',
  `type` enum('impacted_service','incident_brief') NOT NULL DEFAULT 'impacted_service' COMMENT '类型：impacted_service-影响服务，incident_brief-事件简报',
  -- 影响服务字段
  `service` varchar(255) DEFAULT NULL COMMENT '服务名称（影响服务用）',
  `measure` text COMMENT '改进措施（影响服务用）',
  `sla` varchar(100) DEFAULT NULL COMMENT 'SLA（影响服务用）',
  `planned_completion_time` varchar(40) DEFAULT NULL COMMENT '计划完成时间，ISO8601含时区（影响服务用）',
  -- 事件简报字段
  `event` varchar(255) DEFAULT NULL COMMENT '通报事件（事件简报用）',
  `notification_type` varchar(50) DEFAULT NULL COMMENT '通报类型：firstNotification/closeNotification/networkProtectionDaily/other（事件简报用）',
  `next_plan` text COMMENT '下一步计划（事件简报用）',
  -- 通用字段
  `owner` varchar(255) DEFAULT NULL COMMENT '负责人',
  `progress` varchar(50) DEFAULT NULL COMMENT '进度/进展',
  `remark` text COMMENT '备注',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_incident_id` (`incident_id`),
  KEY `idx_type` (`type`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB COMMENT='影响服务和事件简报统一表';

