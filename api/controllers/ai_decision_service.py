from utils.logger_init import logger


class AiDecisionService:

     @classmethod
     def evaluate_ai_decision(cls, payload):
         """
         Evaluate AI decision correctness based on close_reason and verification_state.
         Returns:
             - 'TT' (True Positive): AI correctly identified a true positive
             - 'FP' (False Positive): AI incorrectly identified a false positive as true
             - 'FN' (False Negative): AI incorrectly identified a true positive as false
             - None: Cannot determine (e.g., AutoClosed or missing required fields)
         """
         # Skip if auto-closed or missing required fields
         if payload.get("is_auto_closed") == "AutoClosed":
             return None
         
         close_reason = payload.get("close_reason")
         verification_state = payload.get("verification_state")
         
         # Both fields are required for evaluation
         if not close_reason or not verification_state:
             return None
         
         # Apply the new rules
         if close_reason == "False detection" and verification_state == "False_Positive":
             return "TT"
         elif close_reason == "False detection" and verification_state == "True_Positive":
             return "FP"
         elif close_reason == "Resolved" and verification_state == "False_Positive":
             return "FN"
         elif close_reason == "Resolved" and verification_state == "True_Positive":
             return "TT"
         
         # Default: return None if no matching rule
         return None

