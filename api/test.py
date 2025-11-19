from controllers.alert_service import AlertService
from controllers.comment_service import CommentService
from controllers.incident_service import IncidentService
from models.user import AppUser
from utils.common_utils import decrypt, encrypt


conditions = [
    {"handle_status": ""},
    {"title": ""}
]
# alerts, total = AlertService.list_alerts(conditions, limit=50, offset=0,
#                                         start_time="2024-01-01T00:00:00Z+0800",
#                                         end_time="2024-01-02T00:00:00Z+0800")
#
# alert_id = alerts[0]["id"]
#
# alert_content = AlertService.retrieve_alert_by_id(alert_id)
# saved_alert = AlertService.create_alert(alert_content)
# print(saved_alert)


# incidents, total = IncidentService.list_incidents(conditions, limit=50, offset=0,
#                                                  start_time="2024-01-01T00:00:00Z+0800",
#                                                  end_time="2024-02-01T00:00:00Z+0800")
# print(incidents)
#
# content = IncidentService.retrieve_incident_by_id("7936425c-0ca9-4152-a526-a7fec119f05d")
# print(content)

# data = {
#     "create_time": "2025-11-13T21:08:39.255Z+0000",
#     "title": "MyXXX",
#     "description": "This my XXXX",
#     "severity": "Tips",
# 	}
# resp = AlertService.create_alert(data)
# print(resp)


# resp = IncidentService.associate_alerts_to_incident("d9af2358-39d7-4e3a-805d-af8d14247214", ["3c75238a-922b-4a55-9679-93ff4ebc0a57"])
# print(resp)

print(AppUser.generate_hash("123456"))

data = {
    "title": "test123",
    "description": "test123",
    "create_time": "2025-11-14T23:00:00Z+0800",
    "resource_list": [{
        "owner": "123",
        "responsible_person": "MyXXX",
        "responsible_dept": "123",
        "root_cause": "123",
        "category": "123"
    }]
}
resp = IncidentService.create_incident(data)
print(resp)