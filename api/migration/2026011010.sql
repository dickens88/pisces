-- Modify is_ai_decision_correct column type from int to varchar(10)
-- This change supports the new evaluation logic that returns string values: 'TP', 'FP', 'FN'
ALTER TABLE `t_alerts`
MODIFY COLUMN `is_ai_decision_correct` varchar(10) DEFAULT NULL COMMENT 'AI决策正确性：TP(真阳性), FP(假阳性), FN(假阴性)';

update t_alerts set is_ai_decision_correct='TP' where close_reason='False detection' and verification_state='False_Positive';
update t_alerts set is_ai_decision_correct='TP' where close_reason='Resolved' and verification_state='True_Positive';
update t_alerts set is_ai_decision_correct='FP' where close_reason='False detection' and verification_state='True_Positive';
update t_alerts set is_ai_decision_correct='FN' where close_reason='Resolved' and verification_state='False_Positive';