-- Migration: create table for storing latest AI Fine-tune results per alert/workflow
-- Date: 2026-01-13

CREATE TABLE IF NOT EXISTS `t_alert_ai_finetune_result` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `alert_id` VARCHAR(255) NOT NULL COMMENT 'External alert identifier (matches t_alerts.alert_id)',
  `workflow_id` VARCHAR(255) DEFAULT NULL COMMENT 'AI workflow / app identifier',
  `agent_name` VARCHAR(100) DEFAULT NULL COMMENT 'Agent name used for this run',

  `is_threat` VARCHAR(50) DEFAULT NULL COMMENT 'Parsed [Is Threat] value',
  `confidence_score` VARCHAR(10) DEFAULT NULL COMMENT 'Parsed [Confidence Score] value',
  `reason` TEXT DEFAULT NULL COMMENT 'Parsed [Reason] value',

  `raw_text` LONGTEXT NOT NULL COMMENT 'Full combined text returned by the AI workflow',

  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_alert_ai_finetune_alert_workflow` (`alert_id`, `workflow_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


