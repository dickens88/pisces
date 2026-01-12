-- 为 t_alerts 表增加 agent_name 字段，用于存储代理名称
ALTER TABLE `t_alerts`
ADD COLUMN `agent_name` varchar(100) DEFAULT NULL COMMENT '代理名称' AFTER `ipdrr_phase`;

