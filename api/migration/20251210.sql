-- Add actor column to t_alerts if it does not already exist
ALTER TABLE `t_alerts`
ADD COLUMN `actor` TINYTEXT COMMENT '调查员' AFTER `creator`;

