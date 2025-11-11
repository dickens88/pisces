from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from utils.common_utils import decrypt, encrypt


conditions = [
    {"handle_status": ""},
    {"title": ""}
]
alerts, total = AlertService.list_alerts(conditions, time_range=1, limit=50, offset=0)

alert_id = alerts[0]["id"]

alert_content = AlertService.retrieve_alert_by_id(alert_id)
print(alert_content)
