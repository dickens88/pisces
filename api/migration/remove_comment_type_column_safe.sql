-- 迁移脚本（安全版本）：删除 t_comments 表中的冗余字段 comment_type
-- 原因：评论现在直接调用云脑接口，云脑返回的数据中已经有 note_type 字段，不再需要冗余存储 comment_type
-- 执行日期：2026-01-07
-- 
-- 此版本会先检查字段是否存在，如果存在才删除，避免报错
-- 
-- 注意：在生产环境执行前，请先备份数据库！

-- 创建临时存储过程来安全删除字段
DELIMITER $$

DROP PROCEDURE IF EXISTS `drop_comment_type_column_if_exists`$$

CREATE PROCEDURE `drop_comment_type_column_if_exists`()
BEGIN
    DECLARE column_exists INT DEFAULT 0;
    
    -- 检查字段是否存在
    SELECT COUNT(*) INTO column_exists
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 't_comments'
      AND COLUMN_NAME = 'comment_type';
    
    -- 如果字段存在，则删除
    IF column_exists > 0 THEN
        ALTER TABLE `t_comments` DROP COLUMN `comment_type`;
        SELECT 'Column comment_type has been dropped successfully.' AS result;
    ELSE
        SELECT 'Column comment_type does not exist, no action needed.' AS result;
    END IF;
END$$

DELIMITER ;

-- 执行存储过程
CALL `drop_comment_type_column_if_exists`;

-- 删除临时存储过程
DROP PROCEDURE IF EXISTS `drop_comment_type_column_if_exists`;

