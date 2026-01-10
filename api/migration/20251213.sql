ALTER TABLE `pisces_db`.`t_incidents` 
CHANGE COLUMN `severity` `severity` VARCHAR(40) NULL DEFAULT 'MEDIUM' COMMENT '严重程度' ,
CHANGE COLUMN `handle_status` `handle_status` VARCHAR(40) NULL DEFAULT 'Open' COMMENT '处理状态' ,
CHANGE COLUMN `close_reason` `close_reason` VARCHAR(40) NULL DEFAULT NULL COMMENT '关闭原因' ;