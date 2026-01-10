-- 迁移脚本：删除 t_comments 表中的冗余字段 comment_type
-- 原因：评论现在直接调用云脑接口，云脑返回的数据中已经有 note_type 字段，不再需要冗余存储 comment_type
-- 执行日期：2026-01-07
-- 
-- 使用方法：
-- 1. 如果字段存在，执行此脚本会删除 comment_type 字段
-- 2. 如果字段不存在，执行会报错 "Unknown column 'comment_type'"，可以忽略此错误
-- 
-- 注意：在生产环境执行前，请先备份数据库！

-- 删除 comment_type 字段
-- 如果字段不存在，MySQL 会报错，但不会影响其他操作
ALTER TABLE `t_comments` DROP COLUMN `comment_type`;

