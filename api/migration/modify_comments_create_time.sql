-- Modify t_comments table: change create_time from datetime to varchar(40)
-- This aligns with other tables like t_alerts and t_incidents

-- Drop the index on create_time first
-- Note: If the index doesn't exist, this will show a warning/error
-- For MySQL 5.7.4+, you can use: DROP INDEX IF EXISTS `idx_create_time` ON `t_comments`;
ALTER TABLE `t_comments` DROP INDEX `idx_create_time`;

-- Change create_time column type from datetime to varchar(40)
ALTER TABLE `t_comments` 
MODIFY COLUMN `create_time` VARCHAR(40) DEFAULT NULL COMMENT '创建时间，ISO8601含时区';

-- Note: Index on varchar(40) create_time is not recreated as it's not used in queries
-- If needed in the future, can add: ALTER TABLE `t_comments` ADD INDEX `idx_create_time` (`create_time`);

