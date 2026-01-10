-- Add comment_type column to t_comments table
-- Comment types: comment, attackTracing, attackBlocking, riskMitigation, vulnerabilityIdentification
ALTER TABLE `t_comments`
ADD COLUMN `comment_type` VARCHAR(50) DEFAULT 'comment' COMMENT '评论类型：comment(评论), attackTracing(攻击溯源), attackBlocking(攻击阻断), riskMitigation(风险缓解), vulnerabilityIdentification(漏洞定位)' AFTER `message`;

