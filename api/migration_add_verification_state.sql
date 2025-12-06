-- Migration script to add verification_state column to t_alerts table
-- Execute this script on existing databases to add the new field

ALTER TABLE `t_alerts` 
ADD COLUMN `verification_state` varchar(50) DEFAULT NULL 
COMMENT 'AI研判结果：True_Positive(可疑), False_Positive(误报), Unknown(未知)' 
AFTER `tta`;

