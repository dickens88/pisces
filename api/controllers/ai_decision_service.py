from utils.logger_init import logger


class AiDecisionService:

     @classmethod
     def evaluate_ai_decision(cls, payload):
         if payload.get("is_auto_closed") == "AutoClosed" or payload.get("severity") == "Medium":
             return None
         elif payload.get("severity") == "Low" and payload.get("close_reason") == "False detection":
             return True
         elif payload.get("severity") == "High" and payload.get("close_reason") == "Resolved":
             return True

         return False

