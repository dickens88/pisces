-- Update is_ai_decision_correct field for False detection and False_Positive
update t_alerts set is_ai_decision_correct='TP' where close_reason='False detection' and verification_state='False_Positive';
update t_alerts set is_ai_decision_correct='TP' where close_reason='Resolved' and verification_state='True_Positive';
