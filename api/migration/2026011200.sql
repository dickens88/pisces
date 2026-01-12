-- 为 t_alerts 表增加 ipdrr_phase 字段，用于标记是否已升级为事件等阶段信息
ALTER TABLE `t_alerts`
ADD COLUMN `ipdrr_phase` varchar(100) DEFAULT NULL COMMENT 'IPDRR阶段/处置状态' AFTER `verification_state`;

