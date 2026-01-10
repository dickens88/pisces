-- 将task_id字段重命名为project_uuid
-- 此迁移脚本将task_id字段重命名为project_uuid，以匹配新的API接口

-- 方案1：如果MySQL版本支持，直接重命名字段
ALTER TABLE `t_incidents`
CHANGE COLUMN `task_id` `project_uuid` TEXT NULL COMMENT '项目UUID，支持单个UUID（字符串）或多个UUID（JSON数组字符串）';



